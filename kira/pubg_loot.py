"""Loot and weapon learning for PUBG Mobile training mode only."""
from __future__ import annotations
import json,time
from pathlib import Path
PATH=Path("runtime/pubg_weapon_knowledge.json")
def _load():
    try:return json.loads(PATH.read_text(encoding="utf-8"))
    except Exception:return {"weapons":{},"loot":{}}
def _save(d):
    PATH.parent.mkdir(parents=True,exist_ok=True);tmp=PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8");tmp.replace(PATH)
def observe(v:dict):
    d=_load();now=time.time()
    w=str(v.get("weapon_primary") or "").strip()
    if w:
        p=d["weapons"].setdefault(w,{"seen":0,"scopes":{},"attachments":{},"ammo_samples":[]})
        p["seen"]+=1;p["last_seen"]=now
        scope=str(v.get("scope") or "").strip()
        if scope:p["scopes"][scope]=p["scopes"].get(scope,0)+1
        for a in v.get("attachments") or []:
            a=str(a);p["attachments"][a]=p["attachments"].get(a,0)+1
        ammo=v.get("ammo_current",-1)
        if isinstance(ammo,(int,float)) and ammo>=0:p["ammo_samples"]=(p["ammo_samples"]+[int(ammo)])[-30:]
    for item in v.get("nearby_loot") or []:
        k=str(item).strip()
        if k:
            x=d["loot"].setdefault(k,{"seen":0});x["seen"]+=1;x["last_seen"]=now
    _save(d);return d
def score_item(item:str,current_weapon:str="")->float:
    d=_load();x=d["loot"].get(item,{})
    score=min(2.0,float(x.get("seen",0))*.03)
    s=item.lower()
    if any(k in s for k in ("ammo","патрон","scope","прицел","mag","магаз","grip","рукоят")):score+=2
    if current_weapon and current_weapon.lower() in s:score+=1
    return score
def choose_loot(v:dict)->str:
    items=[str(x) for x in (v.get("nearby_loot") or [])]
    if not items:return ""
    return max(items,key=lambda x:score_item(x,str(v.get("weapon_primary") or "")))
def knowledge():return _load()
