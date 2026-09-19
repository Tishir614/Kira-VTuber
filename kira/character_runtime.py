"""Character-aware runtime tuning for AI, voice and avatar motion."""
from __future__ import annotations
import json, os
from pathlib import Path
from .live2d_model import profile as live2d_profile
from .characters import active_id, get as character_get, save_profile

DATA=Path(os.environ.get("KIRA_DATA_DIR","runtime"))
FILE=DATA/"character-runtime.json"
DEFAULT={
 "name":"Kira","voice":{"speed":1.0,"energy":0.72,"mouth_gain":1.0,"mouth_attack":0.58,"mouth_release":0.28,"mouth_gate":0.018,"mouth_peak":9000.0},
 "ai":{"temperature":0.75,"reply_style":"живой, естественный, персонажный"},
 "motion":{"speech_energy":0.65,"ear_reactivity":0.55,"tail_reactivity":0.45},
 "plugins":{"allow_avatar_events":True}
}
def _merge(a,b):
 out={k:(v.copy() if isinstance(v,dict) else v) for k,v in a.items()}
 for k,v in b.items():
  if isinstance(v,dict) and isinstance(out.get(k),dict):out[k]=_merge(out[k],v)
  else:out[k]=v
 return out
def load():
 cid=active_id();x=character_get(cid)
 if cid=="kira" and not x.get("voice") and FILE.exists():
  try:x=_merge(x,json.loads(FILE.read_text("utf-8")))
  except Exception:pass
 return _merge(DEFAULT,x)
def save(patch):
 x=load()
 for k,v in patch.items():
  if isinstance(v,dict) and isinstance(x.get(k),dict):x[k]={**x[k],**v}
  else:x[k]=v
 save_profile(active_id(),x);return x
def capabilities():
 p=live2d_profile().get("parameters",{})
 return {k:bool(v) for k,v in p.items()}
def ai_context():
 x=load();caps=capabilities()
 features=", ".join(k for k,v in caps.items() if v) or "базовая модель"
 return f"""Ты управляешь персонажем {x.get('name','Kira')}. Стиль ответа: {x['ai'].get('reply_style','естественный')}.
Доступные визуальные возможности аватара: {features}. Не описывай движения, которых модель не поддерживает."""
def recommend():
 caps=capabilities()
 furry=caps.get("ear_l") or caps.get("ear_r") or caps.get("tail_x")
 expressive=sum(bool(caps.get(x)) for x in ("brow_l","brow_r","mouth_form","eye_l","eye_r"))
 return {
  "voice":{"speed":0.96 if expressive>=3 else 1.0,"energy":0.82 if furry else 0.68,"mouth_gain":1.08 if caps.get("mouth_form") else 1.0,"mouth_attack":0.64 if expressive>=3 else 0.54,"mouth_release":0.32 if expressive>=3 else 0.25,"mouth_gate":0.016,"mouth_peak":9000.0},
  "ai":{"temperature":0.82 if expressive>=3 else 0.72,"reply_style":"эмоциональный VTuber, живой и естественный" if expressive>=3 else "живой, естественный, персонажный"},
  "motion":{"speech_energy":0.78 if expressive>=3 else 0.62,"ear_reactivity":0.72 if furry else 0.0,"tail_reactivity":0.62 if caps.get("tail_x") else 0.0},
  "plugins":{"allow_avatar_events":True}
 }
def _plugin_recommendations(caps):
 rec=[]
 def add(pid,reason,score):rec.append({"id":pid,"reason":reason,"score":score})
 add("obs","Сцены, субтитры и реакции персонажа во время эфира",98)
 if caps.get("mouth_open"):add("twitch","Чат и события можно связывать с речью и мимикой",94)
 if caps.get("ear_l") or caps.get("tail_x"):add("twitch","Подписки, рейды и сообщения могут запускать реакции ушей и хвоста",96)
 add("youtube","Подходит для автономных эфиров, чата и публикаций",90)
 return sorted(rec,key=lambda x:x["score"],reverse=True)
def _ai_calibration(caps):
 expressive=sum(bool(caps.get(x)) for x in ("mouth_form","brow_l","brow_r","eye_l","eye_r"))
 motion=sum(bool(caps.get(x)) for x in ("ear_l","ear_r","tail_x","tail_y"))
 return {
  "temperature":round(min(.9,.70+expressive*.025+motion*.01),2),
  "reply_style":"эмоциональный VTuber, естественный, короткие разговорные реплики" if expressive>=3 else "живой, естественный, персонажный",
  "max_history":24 if expressive>=3 else 18,
  "reaction_density":round(min(.9,.45+expressive*.06+motion*.04),2),
  "prefer_short_speech":True
 }
def auto_tune():
 caps=capabilities();r=recommend();r["ai"].update(_ai_calibration(caps));r["plugins"]["recommendations"]=_plugin_recommendations(caps);save(r);return snapshot()
def plugin_event(kind:str,intensity:float=.5):
 x=load();caps=capabilities()
 if not x.get("plugins",{}).get("allow_avatar_events",True):return {}
 intensity=max(0.0,min(1.0,float(intensity)));out={}
 if caps.get("ear_l"):out["ear_l"]=intensity
 if caps.get("ear_r"):out["ear_r"]=intensity*.85
 if caps.get("tail_x"):out["tail_x"]=intensity
 if caps.get("brow_l"):out["brow_l"]=intensity*.35
 if caps.get("brow_r"):out["brow_r"]=intensity*.35
 return {"event":kind,"avatar":out}
def snapshot():
 caps=capabilities();recommended=recommend();recommended["ai"].update(_ai_calibration(caps));recommended["plugins"]["recommendations"]=_plugin_recommendations(caps)
 return {"profile":load(),"capabilities":caps,"recommended":recommended,"plugin_recommendations":_plugin_recommendations(caps)}
