"""Lightweight navigation memory for PUBG Mobile training ground only."""
from __future__ import annotations
import json,time,hashlib
from pathlib import Path
PATH=Path("runtime/pubg_training_map.json")
def _load():
    try:return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:return {"nodes":{},"edges":{}}
def _save(d):
    PATH.parent.mkdir(parents=True,exist_ok=True);tmp=PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8");tmp.replace(PATH)
def signature(v:dict)->str:
    mm=v.get("minimap") or {};parts=[str(mm.get("heading","")),str(v.get("weapon_primary",""))]
    parts+=sorted(str(x) for x in (v.get("nearby_loot") or []))[:4]
    parts+=sorted(str(x) for x in (v.get("training_targets") or []))[:3]
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:12]
def observe(v:dict,previous:str=""):
    d=_load();sid=signature(v);n=d["nodes"].setdefault(sid,{"visits":0,"targets":0,"loot":0,"blocked":0})
    n["visits"]+=1;n["targets"]=max(n["targets"],len(v.get("training_targets") or []));n["loot"]=max(n["loot"],len(v.get("nearby_loot") or []))
    if (v.get("movement") or {}).get("blocked"):n["blocked"]+=1
    n["last_seen"]=time.time()
    if previous and previous!=sid:
        key=previous+">"+sid;e=d["edges"].setdefault(key,{"uses":0});e["uses"]+=1;e["last_used"]=time.time()
    _save(d);return sid
def choose_direction(v:dict,node_id:str)->str:
    d=_load();n=d["nodes"].get(node_id,{})
    if (v.get("movement") or {}).get("blocked"):return "right" if int(n.get("visits",0))%2 else "left"
    # Prefer exploration; periodic turns prevent a permanent straight-line loop.
    k=int(n.get("visits",0))%7
    if k==5:return "left"
    if k==6:return "right"
    return "forward"
def map_state():return _load()
