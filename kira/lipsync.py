import asyncio
import math
import wave
from pathlib import Path
from .live2d import live2d

def _pcm_rms(raw: bytes, width: int) -> float:
    """RMS for PCM WAV samples without audioop (removed in Python 3.13)."""
    if not raw or width not in (1, 2, 3, 4):
        return 0.0
    count = len(raw) // width
    if count <= 0:
        return 0.0
    total = 0.0
    for i in range(0, count * width, width):
        chunk = raw[i:i + width]
        if width == 1:
            sample = chunk[0] - 128
        else:
            sample = int.from_bytes(chunk, "little", signed=True)
        total += sample * sample
    return math.sqrt(total / count)

async def drive_from_wav(path: Path, frame_ms: int = 40):
    """Drive normalized mouth_open from WAV RMS while audio is playing."""
    try:
        with wave.open(str(path), "rb") as w:
            width = w.getsampwidth()
            rate = w.getframerate()
            frames = max(1, int(rate * frame_ms / 1000))
            while True:
                raw = w.readframes(frames)
                if not raw:
                    break
                rms = _pcm_rms(raw, width)
                mouth = min(1.0, max(0.0, rms / 9000.0))
                live2d.set_mouth(mouth)
                await asyncio.sleep(frame_ms / 1000)
    finally:
        live2d.set_mouth(0.0)
