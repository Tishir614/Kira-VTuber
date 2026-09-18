import asyncio
from dataclasses import dataclass, asdict
from .youtube import YouTubeAdapter

@dataclass
class IntegrationState:
    youtube: bool=False
    twitch: bool=False
    last_error: str=""

class IntegrationManager:
    def __init__(self): self.state=IntegrationState(); self.tasks={}
    def snapshot(self): return asdict(self.state)
    def start_youtube(self,api_key,live_chat_id):
        if "youtube" in self.tasks and not self.tasks["youtube"].done(): return
        adapter=YouTubeAdapter(api_key,live_chat_id); self.state.youtube=True
        async def runner():
            try: await adapter.run()
            except Exception as e: self.state.last_error=f"YouTube: {e}"
            finally: self.state.youtube=False
        self.tasks["youtube"]=asyncio.create_task(runner())
    async def stop_youtube(self):
        t=self.tasks.get("youtube")
        if t: t.cancel()
        self.state.youtube=False

integrations=IntegrationManager()
