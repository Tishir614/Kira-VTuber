"""Experience engine: compare before/after gameplay and reinforce useful knowledge."""
from __future__ import annotations
import json,time
from pathlib import Path
PATH=Path("runtime/game_experience.json")
def _load():
    try:return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:return {}
def _save(d):
    PATH.parent.mkdir(parents=True,exist_ok=True)
    tmp=PATH.with_suffix(".tmp");tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8");tmp.replace(PATH)
def outcome(before:dict,after:dict)->str:
    if after.get("death_detected"):return "death"
    bp=str(before.get("progress",""));ap=str(after.get("progress",""))
    if ap and ap!=bp:return "progress"
    if str(after.get("location",""))!=str(before.get("location","")):return "progress"
    return "neutral"
def record(game:str,action:dict,before:dict,after:dict,knowledge:list|None=None):
    d=_load();items=d.setdefault(game,[]);result=outcome(before,after)
    items.append({"at":time.time(),"action":action,"result":result,"before":str(before.get("scene",""))[:300],"after":str(after.get("scene",""))[:300],"knowledge_sources":[x.get("source_url","") for x in (knowledge or [])[:4]]})
    d[game]=items[-300:];_save(d);return result
def summary(game:str,limit:int=30):
    items=_load().get(game,[])[-limit:];score={}
    for x in items:
        key=json.dumps(x.get("action",{}),ensure_ascii=False,sort_keys=True)
        s=score.setdefault(key,{"progress":0,"death":0,"neutral":0});s[x.get("result","neutral")]+=1
    return score
