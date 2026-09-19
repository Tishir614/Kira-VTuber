import asyncio
import json,os,shutil,tempfile
from pathlib import Path
from uuid import uuid4
DATA=Path(os.environ.get("KIRA_DATA_DIR","runtime"))
def _engine_root(engine):return DATA/"engines"/engine/"venv"
def _engine_bin(engine,name):
 root=_engine_root(engine);return root/("Scripts" if os.name=="nt" else "bin")/(name+".exe" if os.name=="nt" else name)
def _engine_python(engine):
 root=_engine_root(engine);return root/("Scripts/python.exe" if os.name=="nt" else "bin/python")
def _catalog_state():
 try:return json.loads((DATA/"catalog-installed.json").read_text("utf-8"))
 except Exception:return {}
class VoiceEngine:
 def _piper(self):
  local=_engine_bin("piper","piper");return str(local) if local.exists() else shutil.which("piper")
 def _kokoro_python(self):
  p=_engine_python("kokoro");return str(p) if p.exists() else None
 @property
 def available(self):return bool(self._piper() or self._kokoro_python())
 async def synthesize(self,text:str,model_path:str="",length_scale:float=1.0,engine:str="piper",voice_id:str="")->Path:
  if engine=="kokoro":return await self._kokoro(text,voice_id or "af_heart",length_scale)
  piper=self._piper()
  if not piper:raise RuntimeError("Piper executable not found. Install Piper in Kira Store.")
  if not model_path:raise RuntimeError("Piper voice model is not configured")
  output=Path(tempfile.gettempdir())/f"kira_tts_{uuid4().hex}.wav"
  cmd=[piper,"--model",model_path,"--output_file",str(output),"--length_scale",str(max(.5,min(2.0,length_scale)))]
  proc=await asyncio.create_subprocess_exec(*cmd,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.PIPE)
  _,err=await proc.communicate(text.encode("utf-8"))
  if proc.returncode:output.unlink(missing_ok=True);raise RuntimeError("Piper synthesis failed: "+err.decode("utf-8","ignore")[-500:])
  if not output.exists() or output.stat().st_size<44:raise RuntimeError("Piper produced no audio")
  return output
 async def _kokoro(self,text,voice_id,speed):
  py=self._kokoro_python()
  if not py:raise RuntimeError("Kokoro is not installed in Kira Store")
  out=Path(tempfile.gettempdir())/f"kira_kokoro_{uuid4().hex}.wav"
  lang=(voice_id or "af_heart")[0]
  cmd=[py,"-m","kokoro","--text",text,"--voice",voice_id or "af_heart","--language",lang,"--speed",str(max(.5,min(2.0,speed))),"--output-file",str(out)]
  p=await asyncio.create_subprocess_exec(*cmd,stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.PIPE)
  _,err=await p.communicate()
  if p.returncode:out.unlink(missing_ok=True);raise RuntimeError("Kokoro synthesis failed: "+err.decode("utf-8","ignore")[-500:])
  if not out.exists() or out.stat().st_size<44:raise RuntimeError("Kokoro produced no audio")
  return out
 def active(self):
  st=_catalog_state();return {"engine":st.get("active_voice_engine","piper"),"voice_id":st.get("active_voice_id",""),"model":st.get("active_voice","")}
voice=VoiceEngine()
