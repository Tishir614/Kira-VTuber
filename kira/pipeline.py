import asyncio
from .config import settings
from .emotion import detect_emotion
from .live2d import live2d
from .llm import chat
from .memory import memory
from .voice import voice
from .audio_output import play_wav_to_output
from .settings_store import settings_store
from .stream_state import state as stream_state
from .subtitles import subtitles
from .lipsync import drive_from_wav
from .character_runtime import load as character_profile

async def respond(text: str, speak: bool = True) -> dict:
    history = memory.history()
    memory.add("user", text)
    answer = await chat(text, history)
    memory.add("assistant", answer)
    emotion = detect_emotion(answer)
    live2d.set_emotion(emotion)
    stream_state.subtitle = answer
    subtitles.set(answer)

    spoken = False
    active=voice.active()
    can_speak=voice.available and (active.get("engine")=="kokoro" or active.get("model") or settings.piper_model)
    if speak and can_speak:
        live2d.set_speaking(True)
        try:
            profile=character_profile(); speed=profile.get("voice",{}).get("speed",1.0)
            engine=active.get("engine") or "piper"; model=active.get("model") or settings.piper_model
            wav = await voice.synthesize(answer, model, speed, engine=engine, voice_id=active.get("voice_id",""))
            # Temporary amplitude animation until real PCM/RMS lip-sync lands.
            task = asyncio.create_task(drive_from_wav(wav))
            try:
                await play_wav_to_output(wav, settings_store.load().get("audio_output", ""))
                spoken = True
            finally:
                task.cancel()
                live2d.set_mouth(0.0)
        finally:
            live2d.set_speaking(False)

    return {"answer": answer, "emotion": emotion, "spoken": spoken}

async def _animate_mouth():
    value = 0.15
    while True:
        live2d.set_mouth(value)
        value = 0.85 if value < 0.5 else 0.15
        await asyncio.sleep(0.11)
