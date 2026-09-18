import asyncio
from pathlib import Path
from .config import settings
from .microphone import record
from .stt import stt
from .voice import voice
from .audio import play_wav

async def microphone_test(seconds: int = 3):
    path=await asyncio.to_thread(record, max(1,min(seconds,5)))
    size=path.stat().st_size if path.exists() else 0
    return {"ok":size>1000,"file_size":size}

async def stt_test(seconds: int = 4):
    path=await asyncio.to_thread(record, max(1,min(seconds,6)))
    text=await asyncio.to_thread(stt.transcribe,str(path),settings.stt_language)
    return {"ok":bool(text),"text":text}

async def voice_test(text: str = "Привет! Я Кира. Проверка голоса завершена."):
    if not voice.available: raise RuntimeError("Piper executable not found")
    if not settings.piper_model: raise RuntimeError("KIRA_PIPER_MODEL is not configured")
    wav=await voice.synthesize(text[:300],settings.piper_model)
    await play_wav(wav)
    return {"ok":True}
