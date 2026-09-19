from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
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
from .selftest import microphone_test, stt_test, voice_test, broadcast_test
from .model_manager import ollama_models
from .stream_state import snapshot as stream_snapshot
from .chat_events import chat_queue
from .stream_chat import stream_chat
from .audience import audience
from .integrations.manager import integrations
from .integrations.twitch_oauth import twitch_oauth
from .integrations.youtube_oauth import youtube_oauth
from .stream_brain import stream_brain
from .viewer_memory import viewer_memory
from .subtitles import subtitles
from .obs import obs_config
from .voice_catalog import voice_models
from .autopilot import autopilot
from .telegram_channel import telegram_status, telegram_post
from .obs_websocket import obs_ws
from .showrunner import showrunner
from .director import director
from .schedule import schedule
from .watchdog import watchdog
from .live2d_model import status as live2d_model_status, install_zip as install_live2d_zip, MODEL_DIR
from .mobile_bundle import export_bundle
from .self_heal import repair as self_repair
from .cloud_client import cloud_status, cloud_post
from .cloud_brain import run_goal as cloud_run_goal
from .game_brain import run as game_run
from .vision import status as vision_status, describe_game
from .game_reflex import snapshot as reflex_status
from .game_profile import get as get_game_profile
from .autonomy import autonomy
from .activity_brain import snapshot as activity_snapshot
from .mood import snapshot as mood_snapshot
from .media_learner import study_url
from .learning_memory import recall as learned_recall
from .research_brain import research
from .adaptive_learning import snapshot as adaptive_learning_status
from .experience_engine import summary as game_experience_summary
from .proxy import status as proxy_status
from .network_brain import network_brain
import asyncio

app = FastAPI(title="Kira VTuber Core", version="0.2.0")
WEB = Path(__file__).resolve().parent.parent / "web"

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(avatar_controller.idle_loop())
    local=settings_store.load()
    if local.get("schedule_enabled",False): schedule.start()
    if local.get("autopilot_enabled",False): autopilot.start()
    if local.get("watchdog_enabled",True): watchdog.start()
    if local.get("master_autonomy_enabled",False): autonomy.start()

class TelegramPostRequest(BaseModel):
    text: str

class ChatRequest(BaseModel):
    message: str
    speak: bool = True

class MemoryRequest(BaseModel):
    fact: str

class HandsFreeRequest(BaseModel):
    wake_word: str = "кира"

class TwitchOAuthConfig(BaseModel):
    client_id: str
    client_secret: str

class YouTubeOAuthConfig(BaseModel):
    client_id: str
    client_secret: str

class TwitchConnect(BaseModel):
    client_id: str
    access_token: str
    broadcaster_user_id: str
    bot_user_id: str

class YouTubeBroadcastCreate(BaseModel):
    title: str
    scheduled_start: str
    privacy: str = "unlisted"
    description: str = ""
    stream_id: str

class YouTubeTransition(BaseModel):
    broadcast_id: str
    status: str

class YouTubeConnect(BaseModel):
    api_key: str
    live_chat_id: str

class ViewerFact(BaseModel):
    platform: str
    user: str
    fact: str

class StreamBrainPatch(BaseModel):
    mode: str | None = None
    global_cooldown: float | None = None
    per_viewer_cooldown: float | None = None
    mention_required: bool | None = None

class StreamMessage(BaseModel):
    platform: str = "local"
    user: str
    text: str

class ModelPullRequest(BaseModel):
    model: str

class CloudUrlRequest(BaseModel):
    url: str

class CloudSearchRequest(BaseModel):
    query: str

class CloudGameRequest(BaseModel):
    game: str

class CloudGoalRequest(BaseModel):
    goal: str
    max_steps: int = 12

class ResearchRequest(BaseModel):
    game: str
    mission: str = ""
    limit: int = 3

class StudyRequest(BaseModel):
    game: str
    url: str
    title: str = ""
    samples: int = 6

class GameGoalRequest(BaseModel):
    goal: str
    steps: int = 20
    game_id: str = "default"

class StudioSettings(BaseModel):
    wake_word: str | None = None
    audio_output: str | None = None
    piper_model: str | None = None
    voice_speed: float | None = None
    voice_enabled: bool | None = None
    volume: float | None = None
    personality: dict | None = None
    telegram_bot_token: str | None = None
    telegram_channel: str | None = None
    autopilot_post_interval_hours: float | None = None
    obs_ws_url: str | None = None
    obs_ws_password: str | None = None
    obs_live_scene: str | None = None
    autonomous_talk_interval_minutes: float | None = None
    director_silence_minutes: float | None = None
    obs_scene_follow: str | None = None
    obs_scene_subscribe: str | None = None
    obs_scene_raid: str | None = None
    obs_event_scene_seconds: float | None = None
    schedule_days: str | None = None
    schedule_start: str | None = None
    schedule_duration_minutes: int | None = None
    watchdog_interval_seconds: float | None = None
    watchdog_failure_limit: int | None = None
    watchdog_safe_stop: bool | None = None
    watchdog_reconnect_twitch: bool | None = None
    youtube_client_id: str | None = None
    youtube_client_secret: str | None = None
    proxy_enabled: bool | None = None
    proxy_url: str | None = None
    proxy_services: list[str] | None = None

@app.get("/")
async def home(): return FileResponse(WEB / "index.html")

@app.post("/auth/twitch/url")
async def twitch_auth_url(req: TwitchOAuthConfig):
    redirect="http://127.0.0.1:8765/auth/twitch/callback"
    # Client secret is intentionally not returned or persisted here.
    settings_store.save({"twitch_client_id":req.client_id,"twitch_client_secret":req.client_secret})
    return {"url":twitch_oauth.authorize_url(req.client_id,redirect)}

@app.get("/auth/twitch/callback")
async def twitch_callback(code: str, state: str):
    local=settings_store.load(); cid=local.get("twitch_client_id",""); secret=local.get("twitch_client_secret","")
    if not cid or not secret: raise HTTPException(400,"Twitch OAuth configuration missing")
    try:
        token=await twitch_oauth.exchange(cid,secret,"http://127.0.0.1:8765/auth/twitch/callback",code,state)
        info=await twitch_oauth.validate(token["access_token"])
        twitch_oauth.start_hourly_validation(cid,secret)
        if info:
            integrations.start_twitch(cid,token["access_token"],info["user_id"],info["user_id"])
            stream_chat.start()
        return {"ok":True,"user":info.get("login") if info else None,"message":"Twitch connected and chat started."}
    except Exception as exc: raise HTTPException(400,str(exc)) from exc

@app.get("/auth/twitch/status")
async def twitch_auth_status():
    token=twitch_oauth.load()
    if not token: return {"connected":False}
    local=settings_store.load(); cid=local.get("twitch_client_id",""); secret=local.get("twitch_client_secret","")
    try:
        valid=await twitch_oauth.ensure_valid(cid,secret) if cid and secret else None
        if not valid: return {"connected":False}
        _,info=valid
        return {"connected":True,"user":info.get("login"),"user_id":info.get("user_id")}
    except Exception: return {"connected":False}

@app.delete("/auth/twitch")
async def twitch_disconnect():
    twitch_oauth.disconnect()
    return {"ok":True}

@app.post("/integrations/twitch/start")
async def twitch_start(req: TwitchConnect):
    integrations.start_twitch(req.client_id,req.access_token,req.broadcaster_user_id,req.bot_user_id)
    stream_chat.start()
    return {"ok":True}

@app.post("/integrations/twitch/stop")
async def twitch_stop():
    await integrations.stop("twitch")
    return {"ok":True}

@app.post("/integrations/twitch/autostart")
async def twitch_autostart():
    local=settings_store.load(); cid=local.get("twitch_client_id",""); secret=local.get("twitch_client_secret","")
    valid=await twitch_oauth.ensure_valid(cid,secret) if cid and secret else None
    if not valid: raise HTTPException(401,"Twitch is not connected")
    token,info=valid; integrations.start_twitch(cid,token["access_token"],info["user_id"],info["user_id"]); stream_chat.start()
    return {"ok":True,"user":info.get("login")}

@app.post("/auth/youtube/url")
async def youtube_auth_url(req: YouTubeOAuthConfig):
    redirect="http://127.0.0.1:8765/auth/youtube/callback"
    settings_store.save({"youtube_client_id":req.client_id,"youtube_client_secret":req.client_secret})
    return {"url":youtube_oauth.authorize_url(req.client_id,redirect)}

@app.get("/auth/youtube/callback")
async def youtube_callback(code:str,state:str):
    s=settings_store.load();cid=s.get("youtube_client_id","");secret=s.get("youtube_client_secret","")
    try:
        await youtube_oauth.exchange(cid,secret,"http://127.0.0.1:8765/auth/youtube/callback",code,state)
        token=await youtube_oauth.access_token(cid,secret);active=await youtube_oauth.active_broadcast(token)
        if active and active.get("live_chat_id"): integrations.start_youtube_oauth(token,active["live_chat_id"]);stream_chat.start()
        return {"ok":True,"active":active}
    except Exception as exc: raise HTTPException(400,str(exc)) from exc

@app.get("/auth/youtube/status")
async def youtube_auth_status():
    s=settings_store.load();cid=s.get("youtube_client_id","");secret=s.get("youtube_client_secret","")
    try:
        token=await youtube_oauth.access_token(cid,secret) if cid and secret else None
        if not token:return {"connected":False}
        active=await youtube_oauth.active_broadcast(token)
        return {"connected":True,"active":active}
    except Exception as exc:return {"connected":False,"error":str(exc)}

@app.post("/integrations/youtube/autostart")
async def youtube_autostart():
    s=settings_store.load();cid=s.get("youtube_client_id","");secret=s.get("youtube_client_secret","")
    token=await youtube_oauth.access_token(cid,secret) if cid and secret else None
    if not token:raise HTTPException(401,"YouTube is not connected")
    active=await youtube_oauth.active_broadcast(token)
    if not active or not active.get("live_chat_id"):raise HTTPException(404,"No active YouTube live broadcast")
    integrations.start_youtube_oauth(token,active["live_chat_id"]);stream_chat.start();return {"ok":True,**active}

@app.get("/youtube/streams")
async def youtube_streams():
    s=settings_store.load();cid=s.get("youtube_client_id","");secret=s.get("youtube_client_secret","");token=await youtube_oauth.access_token(cid,secret) if cid and secret else None
    if not token: raise HTTPException(401,"YouTube is not connected")
    return {"streams":await youtube_oauth.streams(token)}

@app.post("/youtube/broadcast")
async def youtube_create_broadcast(req:YouTubeBroadcastCreate):
    if req.privacy not in {"private","unlisted","public"}: raise HTTPException(400,"invalid privacy")
    s=settings_store.load();cid=s.get("youtube_client_id","");secret=s.get("youtube_client_secret","");token=await youtube_oauth.access_token(cid,secret) if cid and secret else None
    if not token: raise HTTPException(401,"YouTube is not connected")
    b=await youtube_oauth.create_broadcast(token,req.title,req.scheduled_start,req.privacy,req.description)
    await youtube_oauth.bind(token,b["id"],req.stream_id)
    settings_store.save({"youtube_broadcast_id":b["id"],"youtube_stream_id":req.stream_id})
    return {"ok":True,"broadcast_id":b["id"],"stream_id":req.stream_id}

@app.post("/youtube/transition")
async def youtube_transition(req:YouTubeTransition):
    if req.status not in {"testing","live","complete"}: raise HTTPException(400,"invalid transition")
    s=settings_store.load();cid=s.get("youtube_client_id","");secret=s.get("youtube_client_secret","");token=await youtube_oauth.access_token(cid,secret) if cid and secret else None
    if not token: raise HTTPException(401,"YouTube is not connected")
    if req.status in {"testing","live"}:
        stream_id=s.get("youtube_stream_id","")
        if not stream_id or await youtube_oauth.stream_status(token,stream_id)!="active": raise HTTPException(409,"YouTube ingest stream is not active yet")
    return await youtube_oauth.transition(token,req.broadcast_id,req.status)

@app.delete("/auth/youtube")
async def youtube_disconnect():
    await integrations.stop("youtube");youtube_oauth.disconnect();return {"ok":True}

@app.get("/obs/ws/status")
async def obs_ws_status():
    try: return {"connected":True,**await obs_ws.stream_status()}
    except Exception as exc: return {"connected":False,"error":str(exc)}

@app.post("/show/start")
async def show_start():
    try: return await showrunner.start()
    except Exception as exc: raise HTTPException(503,str(exc)) from exc

@app.post("/show/stop")
async def show_stop():
    try: return await showrunner.stop()
    except Exception as exc: raise HTTPException(503,str(exc)) from exc

@app.get("/watchdog")
async def watchdog_status(): return watchdog.snapshot()

@app.post("/watchdog/start")
async def watchdog_start(): settings_store.save({"watchdog_enabled":True}); watchdog.start(); return {"ok":True,**watchdog.snapshot()}

@app.post("/watchdog/stop")
async def watchdog_stop(): settings_store.save({"watchdog_enabled":False}); watchdog.stop(); return {"ok":True,**watchdog.snapshot()}

@app.get("/schedule")
async def schedule_status(): return schedule.snapshot()

@app.post("/schedule/start")
async def schedule_start(): settings_store.save({"schedule_enabled":True}); schedule.start(); return {"ok":True,**schedule.snapshot()}

@app.post("/schedule/stop")
async def schedule_stop(): settings_store.save({"schedule_enabled":False}); schedule.stop(); return {"ok":True,**schedule.snapshot()}

@app.get("/director")
async def director_status(): return director.snapshot()

@app.get("/show")
async def show_status(): return showrunner.snapshot()

@app.get("/learning/adaptive")
async def learning_adaptive_state(): return adaptive_learning_status()

@app.post("/learning/research")
async def learning_research(req:ResearchRequest):
    try:return await research(req.game,req.mission,max(1,min(req.limit,5)))
    except Exception as exc:raise HTTPException(503,str(exc)) from exc

@app.post("/learning/study")
async def learning_study(req:StudyRequest):
    try:return await study_url(req.game,req.url,req.title,req.samples)
    except Exception as exc:raise HTTPException(503,str(exc)) from exc

@app.get("/learning/{game}")
async def learning_state(game:str,q:str=""): return {"items":learned_recall(game,q,50)}

@app.get("/network")
async def kira_network(): return network_brain.snapshot()

@app.post("/network/check")
async def kira_network_check(): return await network_brain.check_all()

@app.get("/proxy/status")
async def kira_proxy_status(): return await proxy_status()

@app.get("/activity")
async def activity_state(): return activity_snapshot()

@app.get("/mood")
async def mood_state(): return mood_snapshot()

@app.get("/autonomy")
async def autonomy_state(): return autonomy.snapshot()

@app.post("/autonomy/start")
async def autonomy_start(): autonomy.start(); return {"ok":True,**autonomy.snapshot()}

@app.post("/autonomy/stop")
async def autonomy_stop(): autonomy.stop(); return {"ok":True,**autonomy.snapshot()}

@app.get("/autopilot")
async def autopilot_state(): return autopilot.snapshot()

@app.post("/autopilot/start")
async def autopilot_start(): settings_store.save({"autopilot_enabled":True}); autopilot.start(); stream_chat.start(); return {"ok":True,**autopilot.snapshot()}

@app.post("/autopilot/stop")
async def autopilot_stop(): settings_store.save({"autopilot_enabled":False}); autopilot.stop(); return {"ok":True,**autopilot.snapshot()}

@app.get("/integrations/telegram/status")
async def tg_status(): return await telegram_status()

@app.post("/integrations/telegram/post")
async def tg_post(req: TelegramPostRequest):
    try: return await telegram_post(req.text)
    except Exception as exc: raise HTTPException(503,str(exc)) from exc

@app.get("/integrations")
async def integration_state(): return integrations.snapshot()

@app.post("/integrations/youtube/start")
async def youtube_start(req: YouTubeConnect):
    integrations.start_youtube(req.api_key,req.live_chat_id)
    stream_chat.start()
    return {"ok":True}

@app.post("/integrations/youtube/stop")
async def youtube_stop():
    await integrations.stop("youtube")
    return {"ok":True}

@app.get("/viewers")
async def viewers(): return {"viewers":viewer_memory.list()}

@app.get("/viewers/{platform}/{user}")
async def viewer(platform: str,user: str): return viewer_memory.get(platform,user) or {}

@app.post("/viewers/fact")
async def viewer_fact(req: ViewerFact): return viewer_memory.remember(req.platform[:24],req.user[:64],req.fact[:500]) or {}

@app.delete("/viewers/{platform}/{user}")
async def viewer_forget(platform: str,user: str): return {"ok":viewer_memory.forget(platform,user)}

@app.get("/stream/brain")
async def stream_brain_state(): return stream_brain.snapshot()

@app.patch("/stream/brain")
async def stream_brain_patch(req: StreamBrainPatch):
    p={k:v for k,v in req.model_dump().items() if v is not None}
    if "mode" in p and p["mode"] not in {"quiet","active","chaos"}: raise HTTPException(400,"invalid mode")
    if "global_cooldown" in p: p["global_cooldown"]=max(1.0,min(120.0,p["global_cooldown"]))
    if "per_viewer_cooldown" in p: p["per_viewer_cooldown"]=max(1.0,min(600.0,p["per_viewer_cooldown"]))
    stream_brain.configure(**p); return stream_brain.snapshot()

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

@app.get("/subtitles")
async def subtitle_state(): return subtitles.snapshot()

@app.get("/voices")
async def voices(): return voice_models()

@app.get("/obs")
async def obs_state(): return obs_config.load()

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

@app.get("/mobile/bundle")
async def mobile_bundle():
    # Portable project data for Android. Secrets are deliberately excluded.
    data=export_bundle(False)
    return StreamingResponse(data,media_type="application/zip",headers={"Content-Disposition":"attachment; filename=Kira-Mobile-Data.zip"})
@app.get("/mobile/summary")
async def mobile_summary():
    return {"health":await health(),"show":showrunner.snapshot(),"autopilot":autopilot.snapshot(),"watchdog":watchdog.snapshot(),"integrations":integrations.snapshot(),"avatar":live2d.snapshot(),"live2d":live2d_model_status(),"memory":persistent_memory.load()}
@app.get("/manifest.webmanifest")
async def pwa_manifest(): return FileResponse(WEB / "manifest.webmanifest",media_type="application/manifest+json")
@app.get("/sw.js")
async def pwa_sw(): return FileResponse(WEB / "sw.js",media_type="application/javascript")
@app.get("/pwa/{asset}")
async def pwa_asset(asset:str):
    p=WEB/"pwa"/asset
    if not p.is_file(): raise HTTPException(404,"PWA asset not found")
    return FileResponse(p)
@app.get("/studio")
async def studio(): return FileResponse(WEB / "studio.html")

@app.get("/settings")
async def get_settings(): return settings_store.load()

@app.patch("/settings")
async def patch_settings(req: StudioSettings):
    patch={k:v for k,v in req.model_dump().items() if v is not None}
    if "volume" in patch: patch["volume"]=max(0.0,min(1.0,patch["volume"]))
    if "voice_speed" in patch: patch["voice_speed"]=max(0.5,min(2.0,patch["voice_speed"]))
    if "autopilot_post_interval_hours" in patch: patch["autopilot_post_interval_hours"]=max(1.0,min(168.0,patch["autopilot_post_interval_hours"]))
    if "autonomous_talk_interval_minutes" in patch: patch["autonomous_talk_interval_minutes"]=max(2.0,min(120.0,patch["autonomous_talk_interval_minutes"]))
    if "personality" in patch:
        p=patch["personality"]
        for key in ("warmth","humor","energy","verbosity"):
            if key in p: setattr(personality,key,max(0.0,min(1.0,float(p[key]))))
    return settings_store.save(patch)

@app.get("/devices/audio")
async def devices_audio(): return {"devices":audio_devices(),"default":default_audio()}

@app.get("/broadcast/status")
async def broadcast_status():
    result=await broadcast_test(); result["integrations"]=integrations.snapshot(); result["avatar"]=live2d.snapshot(); return result

@app.post("/broadcast/test")
async def test_broadcast():
    result=await broadcast_test(); result["integrations"]=integrations.snapshot(); return result

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

@app.get("/cloud/status")
async def kira_cloud_status(): return await cloud_status()

@app.post("/cloud/browser/open")
async def kira_cloud_open(req:CloudUrlRequest):
    try:return await cloud_post("/browser/open",{"url":req.url})
    except Exception as exc:raise HTTPException(503,str(exc)) from exc

@app.post("/cloud/browser/search")
async def kira_cloud_search(req:CloudSearchRequest):
    try:return await cloud_post("/browser/search",{"query":req.query})
    except Exception as exc:raise HTTPException(503,str(exc)) from exc

@app.post("/cloud/games/launch")
async def kira_cloud_game(req:CloudGameRequest):
    try:return await cloud_post("/games/launch",{"game":req.game})
    except Exception as exc:raise HTTPException(503,str(exc)) from exc

@app.post("/cloud/goal")
async def kira_cloud_goal(req:CloudGoalRequest):
    goal=req.goal.strip()
    if not goal:raise HTTPException(400,"goal is empty")
    try:return await cloud_run_goal(goal,req.max_steps)
    except Exception as exc:raise HTTPException(503,str(exc)) from exc

@app.post("/cloud/game/goal")
async def kira_game_goal(req:GameGoalRequest):
    goal=req.goal.strip()
    if not goal:raise HTTPException(400,"goal is empty")
    try:return await game_run(goal,req.steps,req.game_id)
    except Exception as exc:raise HTTPException(503,str(exc)) from exc

@app.get("/cloud/game/experience/{game_id}")
async def kira_game_experience(game_id:str): return {"actions":game_experience_summary(game_id)}

@app.get("/cloud/game/profile/{game_id}")
async def kira_game_profile(game_id:str): return get_game_profile(game_id)

@app.get("/cloud/game/reflex")
async def kira_game_reflex_status(): return reflex_status()

@app.get("/vision/status")
async def kira_vision_status(): return await vision_status()

@app.post("/vision/describe")
async def kira_vision_describe():
    try:return {"description":await describe_game()}
    except Exception as exc:raise HTTPException(503,str(exc)) from exc

@app.get("/diagnostics")
async def get_diagnostics(): return await diagnostics()

@app.post("/repair")
async def repair_core():
    return await self_repair()

@app.get("/health")
async def health():
    ollama=False
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            ollama=(await client.get(f"{settings.llm_base_url}/api/tags")).is_success
    except Exception: pass
    return {"ok":True,"ollama":ollama,"model":settings.llm_model}

@app.get("/live2d")
async def live2d_page(): return FileResponse(WEB / "live2d.html")

@app.get("/live2d/status")
async def live2d_status(): return live2d_model_status()

@app.get("/live2d/model/{asset_path:path}")
async def live2d_asset(asset_path:str):
    p=(MODEL_DIR/asset_path).resolve()
    if MODEL_DIR.resolve() not in p.parents and p!=MODEL_DIR.resolve(): raise HTTPException(400,"invalid asset path")
    if not p.is_file(): raise HTTPException(404,"Live2D asset not found")
    return FileResponse(p)

@app.post("/live2d/install")
async def live2d_install(file:UploadFile=File(...)):
    if not (file.filename or "").lower().endswith(".zip"): raise HTTPException(400,"Upload a Live2D ZIP")
    tmp=MODEL_DIR.parent/"upload.zip";tmp.parent.mkdir(parents=True,exist_ok=True)
    try:
        with tmp.open("wb") as out:
            while chunk:=await file.read(1024*1024):out.write(chunk)
        return install_live2d_zip(tmp)
    except Exception as exc: raise HTTPException(400,str(exc)) from exc
    finally:
        tmp.unlink(missing_ok=True)

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
