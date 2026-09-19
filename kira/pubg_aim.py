"""Adaptive aim/recoil practice for PUBG Mobile training targets only."""
from __future__ import annotations
import json,time
from pathlib import Path
from .cloud_client import cloud_post
PATH=Path("runtime/pubg_training_skills.json")
def _load():
    try:return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:return {}
def _save(d):
    PATH.parent.mkdir(parents=True,exist_ok=True);tmp=PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8");tmp.replace(PATH)
def profile(weapon:str):
    d=_load();return d.get(weapon or "unknown",{"pull_down":18,"gain":.35,"samples":0,"hits":0,"shots":0})
async def adjust(dx:float,dy:float,weapon:str):
    p=profile(weapon);gain=max(.08,min(.65,float(p.get("gain",.35))))
    x=int(max(-220,min(220,dx*gain)));y=int(max(-220,min(220,dy*gain)))
    return await cloud_post("/game/mouse",{"dx":x,"dy":y})
async def compensate(weapon:str):
    p=profile(weapon);return await cloud_post("/game/mouse",{"dx":0,"dy":int(max(-90,min(90,p.get("pull_down",18))))})
def learn(weapon:str,hit:bool,vertical_drift:float=0):
    key=weapon or "unknown";d=_load();p=d.setdefault(key,profile(key))
    p["samples"]=int(p.get("samples",0))+1;p["shots"]=int(p.get("shots",0))+1
    if hit:p["hits"]=int(p.get("hits",0))+1
    target=max(-70,min(70,-vertical_drift*.25))
    p["pull_down"]=round(float(p.get("pull_down",18))*.9+target*.1,2)
    rate=p["hits"]/max(1,p["shots"]);p["gain"]=round(max(.12,min(.55,.25+rate*.25)),3)
    p["updated_at"]=time.time();_save(d);return p
def all_profiles():return _load()
