"""Master autonomy switch for Kira.
Runs only previously configured, bounded subsystems. The user-facing control is ON/OFF.
"""
from __future__ import annotations
import asyncio,time
from dataclasses import dataclass,asdict
from .settings_store import settings_store
from .autopilot import autopilot
from .schedule import schedule
from .watchdog import watchdog
from .stream_chat import stream_chat
from .self_heal import repair
from .cloud_client import cloud_status
from .activity_brain import tick as activity_tick, snapshot as activity_status
from .mood import nudge
from .network_brain import network_brain

@dataclass
class AutonomyState:
    enabled:bool=False
    started_at:float=0
    last_tick:float=0
    last_error:str=""
    recoveries:int=0
    last_activity_at:float=0

class Autonomy:
    def __init__(self):self.state=AutonomyState();self.task=None
    def snapshot(self):return asdict(self.state)
    def start(self):
        self.state.enabled=True;self.state.started_at=time.time()
        settings_store.save({"master_autonomy_enabled":True})
        watchdog.start();schedule.start();autopilot.start();stream_chat.start();network_brain.start()
        if not self.task or self.task.done():self.task=asyncio.create_task(self._loop())
    def stop(self):
        self.state.enabled=False;settings_store.save({"master_autonomy_enabled":False})
        autopilot.stop();schedule.stop();stream_chat.stop();watchdog.stop();network_brain.stop()
        if self.task and not self.task.done():self.task.cancel()
    async def _loop(self):
        while self.state.enabled:
            try:
                self.state.last_tick=time.time()
                result=await repair()
                self.state.recoveries+=len(result.get("actions",[]))
                self.state.last_error="; ".join(result.get("unresolved",[]))[:500]
                # Cloud is optional. Probe it without granting new capabilities.
                await cloud_status()
                interval=max(10,float(settings_store.load().get("autonomous_activity_minutes",30)))*60
                if time.time()-self.state.last_activity_at>=interval:
                    before=activity_status().get("completed",0);await activity_tick()
                    if activity_status().get("completed",0)>before:nudge(curiosity=.01,focus=.005)
                    self.state.last_activity_at=time.time()
            except asyncio.CancelledError:raise
            except Exception as exc:self.state.last_error=str(exc)[:500]
            await asyncio.sleep(60)

autonomy=Autonomy()
