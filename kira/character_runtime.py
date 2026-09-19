"""Character-aware runtime tuning for AI, voice and avatar motion."""
from __future__ import annotations
import json, os
from pathlib import Path
from .live2d_model import profile as live2d_profile

DATA=Path(os.environ.get("KIRA_DATA_DIR","runtime"))
FILE=DATA/"character-runtime.json"
DEFAULT={
 "name":"Kira","voice":{"speed":1.0,"energy":0.72,"mouth_gain":1.0,"mouth_attack":0.58,"mouth_release":0.28,"mouth_gate":0.018,"mouth_peak":9000.0},
 "ai":{"temperature":0.75,"reply_style":"живой, естественный, персонажный"},
 "motion":{"speech_energy":0.65,"ear_reactivity":0.55,"tail_reactivity":0.45},
 "plugins":{"allow_avatar_events":True}
}
def load():
 try:
  x=json.loads(FILE.read_text("utf-8"));return {**DEFAULT,**x}
 except Exception:return DEFAULT.copy()
def save(patch):
 x=load()
 for k,v in patch.items():
  if isinstance(v,dict) and isinstance(x.get(k),dict):x[k]={**x[k],**v}
  else:x[k]=v
 DATA.mkdir(parents=True,exist_ok=True);FILE.write_text(json.dumps(x,ensure_ascii=False,indent=2),"utf-8");return x
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
def auto_tune():
 r=recommend();save(r);return snapshot()
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
def snapshot():return {"profile":load(),"capabilities":capabilities(),"recommended":recommend()}
