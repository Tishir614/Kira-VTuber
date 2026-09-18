"""Detect when Kira is stuck and research only the missing gameplay knowledge."""
from __future__ import annotations
import time
from dataclasses import dataclass,asdict
from .research_brain import research

@dataclass
class LearningState:
    researching:bool=False
    last_query:str=""
    last_at:float=0
    triggered:int=0
    cooldown_seconds:int=600
state=LearningState()

def should_research(vision:dict,stagnant:int,recent:list)->bool:
    confidence=float(vision.get("confidence",0) or 0)
    unknown=not vision.get("progress") and not vision.get("suggested_action")
    repeated=len(recent)>=4 and len({str(x) for x in recent[-4:]})<=2
    return stagnant>=3 or repeated or (confidence<.35 and unknown)

async def learn_when_stuck(game:str,goal:str,vision:dict,stagnant:int,recent:list):
    if not should_research(vision,stagnant,recent):return None
    if time.time()-state.last_at<state.cooldown_seconds:return None
    scene=str(vision.get("scene",""))[:500];location=str(vision.get("location",""))[:200]
    mission=" ".join(x for x in [goal,location,scene] if x)[:900]
    state.researching=True;state.last_query=mission;state.last_at=time.time();state.triggered+=1
    try:return await research(game,mission,limit=2)
    finally:state.researching=False

def snapshot():return asdict(state)
