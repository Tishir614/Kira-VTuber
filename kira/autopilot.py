import asyncio, json
from dataclasses import dataclass, asdict
from pathlib import Path
from time import time
import httpx
from .pipeline import respond
from .settings_store import settings_store

@dataclass
class AutopilotState:
    enabled: bool=False
    last_post: float=0
    last_error: str=""
    posts_sent: int=0

class KiraAutopilot:
    def __init__(self):
        self.state=AutopilotState(); self.task=None
    def snapshot(self): return asdict(self.state)
    def start(self):
        self.state.enabled=True
        if not self.task or self.task.done(): self.task=asyncio.create_task(self._loop())
    def stop(self):
        self.state.enabled=False
        if self.task and not self.task.done(): self.task.cancel()
    async def _generate_post(self):
        r=await respond("Ты ведёшь собственные каналы как виртуальная ведущая Кира. Придумай короткий самостоятельный пост для аудитории на русском: живой, без выдуманных новостей и без утверждений о событиях, которых ты не проверяла. До 500 символов.",False)
        return r["answer"][:1000]
    async def _telegram_post(self,text):
        s=settings_store.load(); token=s.get("telegram_bot_token",""); chat=s.get("telegram_channel","")
        if not token or not chat: return False
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.post(f"https://api.telegram.org/bot{token}/sendMessage",json={"chat_id":chat,"text":text}); r.raise_for_status()
        return True
    async def _loop(self):
        while self.state.enabled:
            try:
                s=settings_store.load(); hours=max(1,float(s.get("autopilot_post_interval_hours",6)))
                if time()-self.state.last_post >= hours*3600:
                    text=await self._generate_post()
                    sent=await self._telegram_post(text)
                    if sent:
                        self.state.last_post=time(); self.state.posts_sent+=1
            except asyncio.CancelledError: raise
            except Exception as e: self.state.last_error=str(e)[:300]
            await asyncio.sleep(60)

autopilot=KiraAutopilot()
