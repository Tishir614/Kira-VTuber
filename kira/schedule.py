import asyncio
from dataclasses import dataclass, asdict
from datetime import datetime
from .settings_store import settings_store
from .showrunner import showrunner
from .autopilot import autopilot
from .pipeline import respond
from .telegram_channel import telegram_post

@dataclass
class ScheduleState:
    enabled: bool=False
    last_run_key: str=""
    last_error: str=""

class KiraSchedule:
    def __init__(self): self.state=ScheduleState(); self.task=None
    def snapshot(self): return asdict(self.state)
    def start(self):
        self.state.enabled=True
        if not self.task or self.task.done(): self.task=asyncio.create_task(self._loop())
    def stop(self):
        self.state.enabled=False
        if self.task and not self.task.done(): self.task.cancel()
    async def _announce(self,kind):
        try:
            p="Напиши короткий пост в Telegram: эфир Киры начинается прямо сейчас." if kind=="start" else "Напиши короткий пост в Telegram: эфир Киры завершён, поблагодари зрителей."
            r=await respond(p,False); await telegram_post(r["answer"])
        except Exception: pass
    async def _loop(self):
        while self.state.enabled:
            try:
                s=settings_store.load(); now=datetime.now()
                days={int(x) for x in str(s.get("schedule_days","0,1,2,3,4,5,6")).split(",") if x.strip().isdigit()}
                start=str(s.get("schedule_start","19:00")); duration=max(10,int(s.get("schedule_duration_minutes",120)))
                hh,mm=[int(x) for x in start.split(":")[:2]]
                start_min=hh*60+mm; cur=now.hour*60+now.minute
                key=f"{now.date()}:{start}"
                if now.weekday() in days and start_min<=cur<start_min+2 and self.state.last_run_key!=key and not showrunner.state.live:
                    self.state.last_run_key=key
                    await showrunner.start(); await self._announce("start")
                    asyncio.create_task(self._stop_later(duration))
            except asyncio.CancelledError: break
            except Exception as e: self.state.last_error=str(e)[:300]
            await asyncio.sleep(30)
    async def _stop_later(self,minutes):
        await asyncio.sleep(minutes*60)
        if showrunner.state.live:
            await showrunner.stop(); await self._announce("stop")
schedule=KiraSchedule()
