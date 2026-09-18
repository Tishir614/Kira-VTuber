"""Fast reflex layer for Kira's isolated single-player game controller.
No LLM call is made here. It converts recent structured vision into tiny bounded reactions.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
import time

@dataclass
class ReflexState:
    enabled:bool=True
    hz:int=12
    last_action:dict|None=None
    last_at:float=0.0

state=ReflexState()

def choose(v:dict)->dict:
    if not state.enabled:return {"action":"wait","reason":"reflex disabled"}
    ui=v.get("ui_state","unknown")
    confidence=float(v.get("confidence",0) or 0)
    threats=v.get("threats") or []
    interact=v.get("interactables") or []
    if ui in {"loading","unknown"} or confidence<.35:return {"action":"wait","reason":"uncertain frame"}
    if ui in {"menu","dialog"}:return {"action":"wait","reason":"strategy handles menus"}
    if threats:
        # Defensive micro-reaction only. Strategy remains responsible for combat decisions.
        return {"action":"move","keys":["s"],"hold_ms":90,"reason":"visible threat: create distance"}
    if interact and confidence>=.72:
        return {"action":"move","keys":["e"],"hold_ms":45,"reason":"high-confidence nearby interaction"}
    return {"action":"wait","reason":"no reflex needed"}

def record(action:dict):
    state.last_action=action;state.last_at=time.time()

def snapshot():return asdict(state)
