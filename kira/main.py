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

@app.get("/")
async def home(): return FileResponse(WEB / "index.html")

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
