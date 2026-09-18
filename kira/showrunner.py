import asyncio
from dataclasses import dataclass, asdict
from time import time
from .obs_websocket import obs_ws
from .pipeline import respond
from .stream_chat import stream_chat
from .settings_store import settings_store

@dataclass
class ShowState:
    live: bool=False
    started_at: float=0
    phase: str="idle"
    last_error: str=""

class ShowRunner:
    def __init__(self): self.state=ShowState(); self.task=None
    def snapshot(self): return asdict(self.state)
    async def start(self):
        if self.state.live: return self.snapshot()
        s=settings_store.load(); scene=s.get("obs_live_scene","")
        try:
            self.state.phase="starting"
            if scene: await obs_ws.set_scene(scene)
            await obs_ws.start_stream(); stream_chat.start()
            self.state.live=True; self.state.started_at=time(); self.state.phase="live"; self.state.last_error=""
            self.task=asyncio.create_task(self._host_loop())
            return self.snapshot()
        except Exception as e:
            self.state.phase="error"; self.state.last_error=str(e)[:300]; raise
    async def stop(self):
        self.state.phase="stopping"
        if self.task and not self.task.done(): self.task.cancel()
        try: await obs_ws.stop_stream()
        finally:
            self.state.live=False; self.state.phase="idle"
        return self.snapshot()
    async def _host_loop(self):
        while self.state.live:
            try:
                s=settings_store.load(); minutes=max(2,float(s.get("autonomous_talk_interval_minutes",8)))
                await asyncio.sleep(minutes*60)
                if not self.state.live: break
                await respond("Ты сейчас сама ведёшь прямой эфир. Скажи зрителям короткую естественную реплику, начни новую тему или задай вопрос чату. Не выдумывай новости и факты о реальном мире. До 2 предложений.",True)
            except asyncio.CancelledError: break
            except Exception as e: self.state.last_error=str(e)[:300]
showrunner=ShowRunner()
