"""Learning memory: turn observed public media into source-tagged game knowledge."""
from __future__ import annotations
import json,time
from pathlib import Path
from .llm import chat
PATH=Path("runtime/learned_knowledge.json")
def _load():
    try:return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:return {}
def _save(x):
    PATH.parent.mkdir(parents=True,exist_ok=True);PATH.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")
def recall(game:str,query:str="",limit:int=12):
    items=_load().get(game,[])
    if query:
        words={w.lower() for w in query.split() if len(w)>2}
        items=sorted(items,key=lambda x:sum(w in (x.get("lesson","")+" "+x.get("mission","")).lower() for w in words),reverse=True)
    return items[-limit:]
async def learn(game:str,title:str,source_url:str,observations:str):
    prompt=f"""Extract reusable gameplay knowledge from observations of a public video/page.
Game: {game}
Title: {title}
Observations: {observations[:10000]}
Return ONLY JSON array, max 8 objects:
[{{"mission":"","lesson":"","steps":[],"confidence":0.0}}]
Only record what is supported by the observations. No invented secrets or hidden game state."""
    raw=await chat(prompt,[])
    try:items=json.loads(raw[raw.find("["):raw.rfind("]")+1])
    except Exception:return []
    data=_load();bucket=data.setdefault(game,[])
    for x in items[:8]:
        if not isinstance(x,dict) or not x.get("lesson"):continue
        x["source_title"]=title[:300];x["source_url"]=source_url[:1000];x["learned_at"]=time.time();x["verified_in_game"]=False;x["successes"]=0;x["failures"]=0
        x["confidence"]=max(0,min(1,float(x.get("confidence",0))))
        bucket.append(x)
    data[game]=bucket[-500:];_save(data);return items[:8]

def feedback(game:str,source_url:str,success:bool):
    data=_load();changed=0
    for x in data.get(game,[]):
        if x.get("source_url")==source_url:
            key="successes" if success else "failures";x[key]=int(x.get(key,0))+1
            total=x.get("successes",0)+x.get("failures",0)
            x["verified_in_game"]=x.get("successes",0)>0
            if total:x["confidence"]=max(0.05,min(1.0,(float(x.get("confidence",.5))*2+x["successes"]/total)/3))
            changed+=1
    _save(data);return changed
