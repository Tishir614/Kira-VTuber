import asyncio, os, shutil
from pathlib import Path

async def play_wav_to_output(path: Path, target: str = "") -> None:
    """Play locally, optionally targeting a PipeWire node via pw-play --target."""
    if shutil.which("pw-play"):
        cmd=["pw-play"]
        if target.strip(): cmd += ["--target",target.strip()]
        cmd.append(str(path))
    elif shutil.which("aplay"):
        cmd=["aplay",str(path)]
    else:
        raise RuntimeError("No pw-play/aplay audio player found")
    proc=await asyncio.create_subprocess_exec(*cmd)
    await proc.wait()
    if proc.returncode: raise RuntimeError("Audio playback failed")
