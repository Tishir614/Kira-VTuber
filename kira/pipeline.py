import asyncio
from .config import settings
from .emotion import detect_emotion
from .live2d import live2d
from .llm import chat
from .memory import memory
from .voice import voice
from .audio import play_wav
from .stream_state import state as stream_state

async def respond(text: str, speak: bool = True) -> dict:
    history = memory.history()
    memory.add("user", text)
    answer = await chat(text, history)
    memory.add("assistant", answer)
    emotion = detect_emotion(answer)
    live2d.set_emotion(emotion)
    stream_state.subtitle = answer

    spoken = False
    if speak and voice.available and settings.piper_model:
        live2d.set_speaking(True)
        try:
            wav = await voice.synthesize(answer, settings.piper_model)
            # Temporary amplitude animation until real PCM/RMS lip-sync lands.
            task = asyncio.create_task(_animate_mouth())
            try:
                await play_wav(wav)
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
