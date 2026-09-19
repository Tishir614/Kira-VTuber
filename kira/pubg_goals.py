"""Self-directed goals for PUBG Mobile training/non-competitive sessions."""
from __future__ import annotations
import json,time
from pathlib import Path
from .pubg_aim import all_profiles
PATH=Path("runtime/pubg_training_goals.json")
WEAPONS=["M416","AKM","UMP45","SCAR-L","DP-28"]
def _load():
    try:return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:return {"active":None,"completed":[]}
def _save(d):
    PATH.parent.mkdir(parents=True,exist_ok=True);tmp=PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8");tmp.replace(PATH)
def _new():
    skills=all_profiles()
    weapon=min(WEAPONS,key=lambda w:int(skills.get(w,{}).get("shots",0)))
    return {"weapon":weapon,"stage":"find_weapon","target_shots":30,"started_at":time.time(),"updated_at":time.time()}
def current():
    d=_load()
    if not d.get("active"):d["active"]=_new();_save(d)
    return d["active"]
def update(v:dict,shots:int):
    d=_load();g=d.get("active") or _new();weapon=g["weapon"]
    primary=str(v.get("weapon_primary") or "")
    if g["stage"]=="find_weapon" and weapon.lower() in primary.lower():g["stage"]="find_scope"
    elif g["stage"]=="find_scope" and str(v.get("scope") or ""):g["stage"]="practice"
    elif g["stage"]=="practice" and shots>=g["target_shots"]:g["stage"]="complete"
    if g["stage"]=="complete":
        g["completed_at"]=time.time();d.setdefault("completed",[]).append(g);d["completed"]=d["completed"][-50:];d["active"]=_new()
    else:d["active"]=g
    d["active"]["updated_at"]=time.time();_save(d);return d["active"]
def desired_action(v:dict,shots:int)->str|None:
    g=update(v,shots)
    if g["stage"] in {"find_weapon","find_scope"}:return "interact" if v.get("nearby_loot") else None
    if g["stage"]=="practice":
        if v.get("reload_needed") or v.get("ammo_current")==0:return "reload"
        if v.get("crosshair_target") and v.get("training_targets"):return "shoot"
    return None
def state():return _load()
