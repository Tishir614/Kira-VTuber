"""PUBG Mobile training-mode brain.
Autonomous controls are permitted only after the user explicitly marks the session as training/non-competitive.
"""
from __future__ import annotations
import asyncio,time
from dataclasses import dataclass,asdict
from .vision import analyze_game
from .pubg_vision import observe as pubg_observe
from .cloud_client import cloud_post
from .experience_engine import record as record_experience
from .learning_memory import recall as recall_learned
from .research_brain import research
from .pubg_aim import adjust as aim_adjust, compensate as recoil_compensate, learn as learn_aim

@dataclass
class PUBGTrainingState:
    running:bool=False
    training_confirmed:bool=False
    steps:int=0
    shots:int=0
    last_action:str="idle"
    last_error:str=""
state=PUBGTrainingState()

def confirm_training(value:bool):
    state.training_confirmed=bool(value)
    if not value:state.running=False
    return asdict(state)

async def _act(action:str):
    if not state.training_confirmed:raise PermissionError("PUBG autonomous controls require training/non-competitive mode")
    mapping={
      "forward":{"keys":["w"],"hold_ms":220},"left":{"keys":["a"],"hold_ms":140},
      "right":{"keys":["d"],"hold_ms":140},"back":{"keys":["s"],"hold_ms":140},
      "interact":{"keys":["e"],"hold_ms":45},"reload":{"keys":["r"],"hold_ms":45},
    }
    if action=="shoot":
        state.shots+=1;return await cloud_post("/game/click",{})
    return await cloud_post("/game/input",mapping.get(action,{"keys":[],"hold_ms":40}))

async def training_session(max_steps:int=40):
    if not state.training_confirmed:raise PermissionError("Confirm PUBG training/non-competitive mode first")
    state.running=True
    try:
      learned=recall_learned("pubg_mobile","training aim loot recoil")
      if not learned:
          try:await research("PUBG Mobile","training ground aim recoil loot",limit=2)
          except Exception:pass
      for _ in range(max(1,min(max_steps,120))):
        if not state.running or not state.training_confirmed:break
        pv=await pubg_observe()
        if pv.get("mode")!="training":
            state.last_error="Autonomous PUBG controls paused: training mode not visually confirmed";break
        before=await analyze_game("PUBG Mobile TRAINING GROUND only. Practice movement, loot and shooting at training targets.")
        ui=before.get("ui_state","unknown")
        if pv.get("reload_needed") or pv.get("ammo_current")==0:action="reload"
        elif pv.get("training_targets") and not pv.get("crosshair_target"):
            off=pv.get("target_offset") or {};await aim_adjust(float(off.get("x",0) or 0),float(off.get("y",0) or 0),pv.get("weapon_primary",""));action="aim"
        elif pv.get("crosshair_target") and pv.get("training_targets"):action="shoot"
        elif pv.get("interact_available") or pv.get("nearby_loot"):action="interact"
        elif pv.get("movement",{}).get("blocked"):action=["left","right"][state.steps%2]
        elif ui in {"loading","menu","dialog","unknown"}:action="forward"
        else:action=["forward","left","right"][state.steps%3]
        if action=="shoot":await recoil_compensate(pv.get("weapon_primary",""))
        if action!="aim":await _act(action)
        await asyncio.sleep(.35)
        after=await analyze_game("Evaluate PUBG training action result.",str(before)[:800])
        if action=="shoot":
            try:
                pv2=await pubg_observe();fb=pv2.get("shot_feedback") or {};learn_aim(pv.get("weapon_primary",""),bool(fb.get("hit")),float(fb.get("vertical_drift",0) or 0))
            except Exception:pass
        record_experience("pubg_mobile_training",{"action":action},before,after,learned)
        state.steps+=1;state.last_action=action
      return asdict(state)
    except Exception as exc:state.last_error=str(exc)[:400];raise
    finally:state.running=False

def stop():state.running=False
def snapshot():return asdict(state)
