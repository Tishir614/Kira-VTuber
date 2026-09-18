from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx, uvicorn
from .config import settings
from .pipeline import respond
from .live2d import live2d
from .microphone import record
from .stt import stt
from .avatar_controller import avatar_controller
from .persistent_memory import persistent_memory
from .handsfree import handsfree
from .settings_store import settings_store
from .personality import personality
from .diagnostics import diagnostics
from .setup import setup_status, pull_ollama_model
from .devices import audio_devices, default_audio
from .selftest import microphone_test, stt_test, voice_test
from .model_manager import ollama_models
from .stream_state import snapshot as stream_snapshot
from .chat_events import chat_queue
from .stream_chat import stream_chat
from .audience import audience
from .integrations.manager import integrations
import asyncio

app = FastAPI(title="Kira VTuber Core", version="0.2.0")
WEB = Path(__file__).resolve().parent.parent / "web"

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(avatar_controller.idle_loop())

class ChatRequest(BaseModel):
    message: str
    speak: bool = True

class MemoryRequest(BaseModel):
    fact: str

class HandsFreeRequest(BaseModel):
    wake_word: str = "кира"

class YouTubeConnect(BaseModel):
    api_key: str
    live_chat_id: str

class StreamMessage(BaseModel):
    platform: str = "local"
    user: str
    text: str

class ModelPullRequest(BaseModel):
    model: str

class StudioSettings(BaseModel):
    wake_word: str | None = None
    voice_enabled: bool | None = None
    volume: float | None = None
    personality: dict | None = None

@app.get("/")
async def home(): return FileResponse(WEB / "index.html")

@app.get("/integrations")
async def integration_state(): return integrations.snapshot()

@app.post("/integrations/youtube/start")
async def youtube_start(req: YouTubeConnect):
    integrations.start_youtube(req.api_key,req.live_chat_id)
    stream_chat.start()
    return {"ok":True}

@app.post("/integrations/youtube/stop")
async def youtube_stop():
    await integrations.stop_youtube()
    return {"ok":True}

@app.post("/stream/start")
async def stream_start(): stream_chat.start(); return {"ok":True,"enabled":True}

@app.post("/stream/stop")
async def stream_stop(): stream_chat.stop(); return {"ok":True,"enabled":False}

@app.post("/stream/message")
async def stream_message(req: StreamMessage):
    ok=chat_queue.push(req.platform[:24],req.user[:64],req.text[:1000])
    return {"ok":ok}

@app.get("/stream/audience")
async def stream_audience(): return {"viewers":audience.snapshot()}

@app.get("/overlay")
async def overlay(): return FileResponse(WEB / "overlay.html")

@app.get("/overlay/state")
async def overlay_state(): return stream_snapshot()

@app.get("/models")
async def models():
    try: return {"models": await ollama_models(), "active": settings.llm_model}
    except Exception as exc: raise HTTPException(503,str(exc)) from exc

@app.get("/setup")
async def setup_page(): return FileResponse(WEB / "setup.html")

@app.get("/setup/status")
async def setup_check(): return await setup_status()

@app.post("/setup/pull-model")
async def setup_pull(req: ModelPullRequest):
    allowed={"qwen3:4b","qwen3:8b","qwen3:14b"}
    if req.model not in allowed: raise HTTPException(400,"unsupported setup model")
    try: return await pull_ollama_model(req.model)
    except RuntimeError as exc: raise HTTPException(503,str(exc)) from exc

@app.get("/studio")
async def studio(): return FileResponse(WEB / "studio.html")

@app.get("/settings")
async def get_settings(): return settings_store.load()

@app.patch("/settings")
async def patch_settings(req: StudioSettings):
    patch={k:v for k,v in req.model_dump().items() if v is not None}
    if "volume" in patch: patch["volume"]=max(0.0,min(1.0,patch["volume"]))
    if "personality" in patch:
        p=patch["personality"]
        for key in ("warmth","humor","energy","verbosity"):
            if key in p: setattr(personality,key,max(0.0,min(1.0,float(p[key]))))
    return settings_store.save(patch)

@app.get("/devices/audio")
async def devices_audio(): return {"devices":audio_devices(),"default":default_audio()}

@app.post("/selftest/microphone")
async def test_microphone():
    try: return await microphone_test()
    except Exception as exc: raise HTTPException(503,str(exc)) from exc

@app.post("/selftest/stt")
async def test_stt():
    try: return await stt_test()
    except Exception as exc: raise HTTPException(503,str(exc)) from exc

@app.post("/selftest/voice")
async def test_voice():
    try: return await voice_test()
    except Exception as exc: raise HTTPException(503,str(exc)) from exc

@app.get("/diagnostics")
async def get_diagnostics(): return await diagnostics()

@app.get("/health")
async def health():
    ollama=False
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            ollama=(await client.get(f"{settings.llm_base_url}/api/tags")).is_success
    except Exception: pass
    return {"ok":True,"ollama":ollama,"model":settings.llm_model}

@app.get("/avatar/state")
async def avatar_state(): return live2d.snapshot()

@app.post("/chat")
async def kira_chat(req: ChatRequest):
    if not req.message.strip(): raise HTTPException(400,"message is empty")
    try: return await respond(req.message, req.speak)
    except httpx.HTTPError as exc: raise HTTPException(503,f"Local LLM unavailable: {exc}") from exc
    except RuntimeError as exc: raise HTTPException(503,str(exc)) from exc

@app.get("/memory")
async def get_memory(): return persistent_memory.load()

@app.post("/memory")
async def add_memory(req: MemoryRequest):
    persistent_memory.remember(req.fact)
    return {"ok": True, "memory": persistent_memory.load()}

@app.delete("/memory")
async def clear_memory():
    persistent_memory.forget_all()
    return {"ok": True}

@app.get("/handsfree")
async def handsfree_state(): return handsfree.snapshot()

@app.post("/handsfree/start")
async def handsfree_start(req: HandsFreeRequest):
    handsfree.start(req.wake_word)
    return {"ok": True, **handsfree.snapshot()}

@app.post("/handsfree/stop")
async def handsfree_stop():
    handsfree.stop()
    return {"ok": True, **handsfree.snapshot()}

@app.post("/listen")
async def listen(seconds: int = 6):
    live2d.state.listening=True
    try:
        audio=record(max(1,min(seconds,30)))
        text=stt.transcribe(str(audio), language=settings.stt_language)
    finally:
        live2d.state.listening=False
    if not text: return {"heard":"","answer":"","emotion":"neutral","spoken":False}
    result=await respond(text, True)
    return {"heard":text,**result}

if __name__=="__main__":
    uvicorn.run("kira.main:app",host=settings.host,port=settings.port)
