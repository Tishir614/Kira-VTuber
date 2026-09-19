import asyncio
import os,shutil,tempfile
from pathlib import Path
from uuid import uuid4

DATA=Path(os.environ.get("KIRA_DATA_DIR","runtime"))
def _engine_bin(engine,name):
 root=DATA/"engines"/engine/"venv"
 return root/("Scripts" if os.name=="nt" else "bin")/(name+".exe" if os.name=="nt" else name)

class VoiceEngine:
 def _piper(self):
  local=_engine_bin("piper","piper")
  return str(local) if local.exists() else shutil.which("piper")
 @property
 def available(self):return self._piper() is not None
 async def synthesize(self,text:str,model_path:str,length_scale:float=1.0)->Path:
  piper=self._piper()
  if not piper:raise RuntimeError("Piper executable not found. Install Piper in Kira Store.")
  if not model_path:raise RuntimeError("Piper voice model is not configured")
  output=Path(tempfile.gettempdir())/f"kira_tts_{uuid4().hex}.wav"
  cmd=[piper,"--model",model_path,"--output_file",str(output),"--length_scale",str(max(.5,min(2.0,length_scale)))]
  proc=await asyncio.create_subprocess_exec(*cmd,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.PIPE)
  _,err=await proc.communicate(text.encode("utf-8"))
  if proc.returncode:
   output.unlink(missing_ok=True);raise RuntimeError("Piper synthesis failed: "+err.decode("utf-8","ignore")[-500:])
  if not output.exists() or output.stat().st_size<44:raise RuntimeError("Piper produced no audio")
  return output
voice=VoiceEngine()
