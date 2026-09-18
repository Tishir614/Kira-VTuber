import asyncio, shutil
from .config import settings
from .microphone import record
from .stt import stt
from .voice import voice
from .audio_output import play_wav_to_output
from .settings_store import settings_store

async def microphone_test(seconds:int=3):
    path=await asyncio.to_thread(record,max(1,min(seconds,5))); size=path.stat().st_size if path.exists() else 0
    return {"ok":size>1000,"file_size":size}
async def stt_test(seconds:int=4):
    path=await asyncio.to_thread(record,max(1,min(seconds,6))); text=await asyncio.to_thread(stt.transcribe,str(path),settings.stt_language)
    return {"ok":bool(text),"text":text}
async def voice_test(text="Привет! Я Кира. Голосовой тракт работает."):
    local=settings_store.load(); model=local.get("piper_model") or settings.piper_model
    if not voice.available: raise RuntimeError("Piper executable not found")
    if not model: raise RuntimeError("Piper voice model is not configured")
    wav=await voice.synthesize(text[:300],model,float(local.get("voice_speed",1)))
    await play_wav_to_output(wav,local.get("audio_output","")); return {"ok":True}

async def broadcast_test():
    local=settings_store.load(); results={}
    results["llm"]=False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=3) as c: results["llm"]=(await c.get(f"{settings.llm_base_url}/api/tags")).is_success
    except Exception: pass
    results["tts"]=bool(voice.available and (local.get("piper_model") or settings.piper_model))
    results["audio"]=bool(shutil.which("pw-play") or shutil.which("aplay"))
    results["microphone"]=bool(shutil.which("pw-record") or shutil.which("arecord"))
    results["obs_overlay"]=True
    return {"ok":all(results[k] for k in ("llm","tts","audio","obs_overlay")),"checks":results}
