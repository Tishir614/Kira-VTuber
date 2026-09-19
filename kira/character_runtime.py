"""Character-aware runtime tuning for AI, voice and avatar motion."""
from __future__ import annotations
import json, os
from pathlib import Path
from .live2d_model import profile as live2d_profile

DATA=Path(os.environ.get("KIRA_DATA_DIR","runtime"))
FILE=DATA/"character-runtime.json"
DEFAULT={
 "name":"Kira","voice":{"speed":1.0,"energy":0.72,"mouth_gain":1.0},
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
def snapshot():return {"profile":load(),"capabilities":capabilities()}
