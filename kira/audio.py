import asyncio
import shutil
from pathlib import Path

async def play_wav(path: Path) -> None:
    player = shutil.which("pw-play") or shutil.which("aplay")
    if not player:
        raise RuntimeError("Install PipeWire (pw-play) or ALSA (aplay)")
    proc = await asyncio.create_subprocess_exec(player, str(path))
    await proc.wait()
    if proc.returncode != 0:
        raise RuntimeError("Audio playback failed")
