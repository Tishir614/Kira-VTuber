"""Read-only PUBG online assistant. Never sends game controls."""
from __future__ import annotations
from dataclasses import dataclass,asdict
import time
from .pubg_vision import observe
@dataclass
class OnlineState:
    enabled:bool=False
    observations:int=0
    last_seen:float=0
    last_advice:str=""
state=OnlineState()
def set_enabled(v:bool):state.enabled=bool(v);return asdict(state)
async def tick():
    if not state.enabled:return {**asdict(state),"vision":None}
    v=await observe();state.observations+=1;state.last_seen=time.time()
    hp=v.get("health",-1);ammo=v.get("ammo_current",-1)
    tips=[]
    if isinstance(hp,(int,float)) and 0<=hp<35:tips.append("низкое здоровье")
    if v.get("reload_needed") or ammo==0:tips.append("нужна перезарядка")
    if (v.get("movement") or {}).get("blocked"):tips.append("путь перекрыт")
    state.last_advice=", ".join(tips) or "ситуация стабильна"
    return {**asdict(state),"vision":v}
def snapshot():return asdict(state)
