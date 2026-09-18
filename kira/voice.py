import asyncio
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

class VoiceEngine:
    def __init__(self): self.piper=shutil.which("piper")
    @property
    def available(self): return self.piper is not None
    async def synthesize(self,text:str,model_path:str,length_scale:float=1.0)->Path:
        if not self.piper: raise RuntimeError("Piper executable not found")
        if not model_path: raise RuntimeError("Piper voice model is not configured")
        output=Path(tempfile.gettempdir())/f"kira_tts_{uuid4().hex}.wav"
        cmd=[self.piper,"--model",model_path,"--output_file",str(output),"--length_scale",str(max(.5,min(2.0,length_scale)))]
        proc=await asyncio.create_subprocess_exec(*cmd,stdin=asyncio.subprocess.PIPE)
        await proc.communicate(text.encode("utf-8"))
        if proc.returncode: raise RuntimeError("Piper synthesis failed")
        return output
voice=VoiceEngine()
