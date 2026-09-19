"""End-to-end character calibration orchestrator."""
from __future__ import annotations
from .character_runtime import auto_tune,snapshot
from .ai_calibration import calibrate_ai
from .voice_calibration import calibrate as calibrate_voice
from .voice import voice
from .config import settings

async def full_calibration():
 report={"steps":[],"ready":False}
 base=auto_tune();report["steps"].append({"id":"avatar","ok":True,"detail":"Live2D capabilities and motion profile tuned"})
 try:
  ai=await calibrate_ai();report["steps"].append({"id":"ai","ok":True,"score":ai.get("score")})
 except Exception as exc:report["steps"].append({"id":"ai","ok":False,"error":str(exc)})
 wav=None
 try:
  if not settings.piper_model:raise RuntimeError("Voice model is not configured")
  wav=await voice.synthesize("Привет! Проверяю голос, мимику и синхронизацию персонажа.",settings.piper_model)
  vc=calibrate_voice(wav);report["steps"].append({"id":"voice","ok":True,"calibration":vc.get("calibration",{})})
 except Exception as exc:report["steps"].append({"id":"voice","ok":False,"error":str(exc)})
 finally:
  try:
   if wav:wav.unlink(missing_ok=True)
  except Exception:pass
 state=snapshot();plugins=state.get("plugin_recommendations",[])
 report["steps"].append({"id":"plugins","ok":True,"recommendations":plugins})
 required=[x for x in report["steps"] if x["id"] in ("avatar","ai","voice")]
 report["ready"]=all(x.get("ok") for x in required)
 report["profile"]=state
 return report
