"""Per-game adaptive profile: controls, deaths, quests, inventory and lightweight map."""
from __future__ import annotations
import json,time
from pathlib import Path
PATH=Path("runtime/game_profiles.json")

def _all():
    try:return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:return {}
def _save(x):
    PATH.parent.mkdir(parents=True,exist_ok=True);PATH.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")
def get(game):
    return _all().get(game,{"controls":{},"deaths":[],"quests":[],"inventory":[],"places":[],"stats":{"sessions":0,"steps":0}})
def patch(game,**changes):
    a=_all();p=a.setdefault(game,get(game))
    for k,v in changes.items():p[k]=v
    _save(a);return p
def session(game):
    p=get(game);p["stats"]["sessions"]=p["stats"].get("sessions",0)+1;return patch(game,**p)
def step(game):
    p=get(game);p["stats"]["steps"]=p["stats"].get("steps",0)+1;return patch(game,**p)
def death(game,scene):
    p=get(game);p["deaths"].append({"at":time.time(),"scene":scene[:500]});p["deaths"]=p["deaths"][-30:];return patch(game,**p)
def update_world(game,vision):
    p=get(game)
    for q in vision.get("quests",[]) or []:
        if q and q not in p["quests"]:p["quests"].append(q)
    for i in vision.get("inventory",[]) or []:
        if i and i not in p["inventory"]:p["inventory"].append(i)
    place=vision.get("location","")
    if place and place not in p["places"]:p["places"].append(place)
    p["quests"]=p["quests"][-50:];p["inventory"]=p["inventory"][-100:];p["places"]=p["places"][-100:]
    return patch(game,**p)
