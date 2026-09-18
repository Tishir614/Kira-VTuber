import asyncio
from dataclasses import dataclass, asdict
from .youtube import YouTubeAdapter
from .twitch import TwitchAdapter

@dataclass
class IntegrationState:
    youtube: bool=False
    twitch: bool=False
    last_error: str=""

class IntegrationManager:
    def __init__(self): self.state=IntegrationState(); self.tasks={}; self.adapters={}
    def snapshot(self): return asdict(self.state)
    def _start(self,name,adapter):
        t=self.tasks.get(name)
        if t and not t.done(): return
        self.adapters[name]=adapter; setattr(self.state,name,True); self.state.last_error=""
        async def runner():
            try: await adapter.run()
            except asyncio.CancelledError: pass
            except Exception as e: self.state.last_error=f"{name}: {e}"
            finally: setattr(self.state,name,False)
        self.tasks[name]=asyncio.create_task(runner())
    def start_youtube(self,api_key,live_chat_id): self._start("youtube",YouTubeAdapter(live_chat_id,api_key=api_key))
    def start_youtube_oauth(self,access_token,live_chat_id): self._start("youtube",YouTubeAdapter(live_chat_id,access_token=access_token))
    def start_twitch(self,client_id,access_token,broadcaster_user_id,bot_user_id): self._start("twitch",TwitchAdapter(client_id,access_token,broadcaster_user_id,bot_user_id))
    async def stop(self,name):
        a=self.adapters.get(name)
        if a:
            try: await a.stop()
            except Exception: pass
        t=self.tasks.get(name)
        if t and not t.done(): t.cancel()
        setattr(self.state,name,False)

integrations=IntegrationManager()
