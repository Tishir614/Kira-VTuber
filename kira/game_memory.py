"""Persistent per-game learning memory for Kira."""
from __future__ import annotations
import json, time
from pathlib import Path

PATH=Path("runtime/game_memory.json")

def _load():
    try:return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:return {}

def _save(data):
    PATH.parent.mkdir(parents=True,exist_ok=True)
    PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

def recall(game:str,limit:int=10):
    data=_load().get(game,{})
    return {"notes":data.get("notes",[])[-limit:],"failures":data.get("failures",[])[-limit:],"controls":data.get("controls",{})}

def remember(game:str,kind:str,text:str):
    if not text:return
    all_data=_load();data=all_data.setdefault(game,{"notes":[],"failures":[],"controls":{}})
    bucket="failures" if kind=="failure" else "notes"
    data[bucket].append({"at":time.time(),"text":text[:700]})
    data[bucket]=data[bucket][-100:]
    _save(all_data)

def learn_control(game:str,action:str,keys:list[str]):
    all_data=_load();data=all_data.setdefault(game,{"notes":[],"failures":[],"controls":{}})
    data["controls"][action[:80]]=keys[:4];_save(all_data)
