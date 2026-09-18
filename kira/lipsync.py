import asyncio, wave, audioop
from pathlib import Path
from .live2d import live2d

async def drive_from_wav(path: Path, frame_ms: int = 40):
    """Drive normalized mouth_open from WAV RMS while audio is playing."""
    try:
        with wave.open(str(path),"rb") as w:
            width=w.getsampwidth(); rate=w.getframerate(); channels=w.getnchannels()
            frames=max(1,int(rate*frame_ms/1000))
            while True:
                raw=w.readframes(frames)
                if not raw: break
                rms=audioop.rms(raw,width)
                # Conservative normalization; renderer can smooth further.
                mouth=min(1.0,max(0.0,rms/9000.0))
                live2d.set_mouth(mouth)
                await asyncio.sleep(frame_ms/1000)
    finally:
        live2d.set_mouth(0.0)
