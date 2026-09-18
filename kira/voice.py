import asyncio
import shutil
import tempfile
from pathlib import Path

class VoiceEngine:
    def __init__(self) -> None:
        self.piper = shutil.which("piper")

    @property
    def available(self) -> bool:
        return self.piper is not None

    async def synthesize(self, text: str, model_path: str) -> Path:
        if not self.piper:
            raise RuntimeError("Piper executable not found")
        if not model_path:
            raise RuntimeError("Piper voice model is not configured")
        output = Path(tempfile.gettempdir()) / "kira_tts.wav"
        proc = await asyncio.create_subprocess_exec(
            self.piper, "--model", model_path, "--output_file", str(output),
            stdin=asyncio.subprocess.PIPE,
        )
        await proc.communicate(text.encode("utf-8"))
        if proc.returncode != 0:
            raise RuntimeError("Piper synthesis failed")
        return output

voice = VoiceEngine()
