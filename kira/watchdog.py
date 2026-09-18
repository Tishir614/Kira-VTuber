import asyncio
from dataclasses import dataclass, asdict
from time import time
import httpx
from .config import settings
from .settings_store import settings_store
from .obs_websocket import obs_ws
from .integrations.manager import integrations
from .integrations.twitch_oauth import twitch_oauth
from .stream_chat import stream_chat
from .showrunner import showrunner

@dataclass
class WatchdogState:
    enabled: bool=False
    llm: bool=False
    obs: bool=False
    twitch: bool=False
    youtube: bool=False
    failures: int=0
    recoveries: int=0
    last_error: str=""
    checked_at: float=0

class Watchdog:
    def __init__(self): self.state=WatchdogState(); self.task=None
    def snapshot(self): return asdict(self.state)
    def start(self):
        self.state.enabled=True
        if not self.task or self.task.done(): self.task=asyncio.create_task(self._loop())
    def stop(self):
        self.state.enabled=False
        if self.task and not self.task.done(): self.task.cancel()
    async def _check_llm(self):
        try:
            async with httpx.AsyncClient(timeout=3) as c: return (await c.get(f"{settings.llm_base_url}/api/tags")).is_success
        except Exception: return False
    async def _check_obs(self):
        try: await obs_ws.stream_status(); return True
        except Exception:
            try: await obs_ws.close()
            except Exception: pass
            return False
    async def _recover_twitch(self):
        s=settings_store.load(); cid=s.get("twitch_client_id",""); secret=s.get("twitch_client_secret","")
        if not cid or not secret: return False
        try:
            valid=await twitch_oauth.ensure_valid(cid,secret)
            if not valid: return False
            token,info=valid; integrations.start_twitch(cid,token["access_token"],info["user_id"],info["user_id"]); stream_chat.start()
            return True
        except Exception as e: self.state.last_error=f"Twitch recovery: {e}"[:300]; return False
    async def _loop(self):
        while self.state.enabled:
            try:
                self.state.llm=await self._check_llm(); self.state.obs=await self._check_obs()
                snap=integrations.snapshot(); self.state.twitch=bool(snap.get("twitch")); self.state.youtube=bool(snap.get("youtube"))
                s=settings_store.load()
                if s.get("watchdog_reconnect_twitch",True) and twitch_oauth.load() and not self.state.twitch:
                    if await self._recover_twitch(): self.state.twitch=True; self.state.recoveries+=1
                if showrunner.state.live and (not self.state.llm or not self.state.obs):
                    self.state.failures+=1
                    limit=max(1,int(s.get("watchdog_failure_limit",3)))
                    if self.state.failures>=limit and s.get("watchdog_safe_stop",True):
                        try: await showrunner.stop()
                        except Exception: pass
                else: self.state.failures=0
                self.state.checked_at=time()
            except asyncio.CancelledError: break
            except Exception as e: self.state.last_error=str(e)[:300]
            await asyncio.sleep(max(10,float(settings_store.load().get("watchdog_interval_seconds",30))))
watchdog=Watchdog()
