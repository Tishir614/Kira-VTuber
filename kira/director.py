import asyncio, random
from dataclasses import dataclass, asdict
from time import time
from .obs_websocket import obs_ws
from .pipeline import respond
from .settings_store import settings_store

@dataclass
class DirectorState:
    enabled: bool=False
    last_chat_at: float=0
    last_action_at: float=0
    last_action: str=""
    last_error: str=""

class Director:
    def __init__(self): self.state=DirectorState(); self.task=None; self.lock=asyncio.Lock()
    def snapshot(self): return asdict(self.state)
    def note_chat(self): self.state.last_chat_at=time()
    def start(self):
        self.state.enabled=True
        if not self.state.last_chat_at: self.state.last_chat_at=time()
        if not self.task or self.task.done(): self.task=asyncio.create_task(self._loop())
    def stop(self):
        self.state.enabled=False
        if self.task and not self.task.done(): self.task.cancel()
    async def react_event(self,kind,user,platform,text=""):
        if not self.state.enabled: return
        prompts={
          "follow":f"На {platform} новый подписчик @{user}. Коротко поприветствуй его.",
          "subscribe":f"@{user} оформил подписку на {platform}. Тепло и коротко поблагодари.",
          "gift":f"@{user} подарил подписки на {platform}. Энергично и коротко поблагодари.",
          "raid":f"На эфир пришёл рейд от @{user} на {platform}. Ярко поприветствуй рейдеров.",
          "cheer":f"@{user} поддержал эфир на {platform}. Коротко поблагодари."
        }
        p=prompts.get(kind)
        if p:
            async with self.lock: await respond(p,True)
            await self._event_scene(kind)
            self.state.last_action=f"{kind}:{user}"; self.state.last_action_at=time()
    async def _event_scene(self,kind):
        s=settings_store.load(); scene=s.get(f"obs_scene_{kind}","")
        live=s.get("obs_live_scene","")
        if not scene: return
        try:
            await obs_ws.set_scene(scene); await asyncio.sleep(max(1,min(15,float(s.get("obs_event_scene_seconds",5)))))
            if live: await obs_ws.set_scene(live)
        except Exception as e: self.state.last_error=str(e)[:300]
    async def _loop(self):
        while self.state.enabled:
            try:
                s=settings_store.load(); silence=max(2,float(s.get("director_silence_minutes",5)))*60
                if time()-self.state.last_chat_at>=silence and time()-self.state.last_action_at>=silence:
                    prompts=[
                      "В чате наступила тишина. Сама начни короткую интересную тему и задай зрителям вопрос. Не выдумывай новости.",
                      "Эфир немного затих. Скажи короткую живую реплику и вовлеки зрителей в разговор.",
                      "Предложи зрителям лёгкую тему для разговора или мини-вопрос. Максимум два предложения."
                    ]
                    async with self.lock: await respond(random.choice(prompts),True)
                    self.state.last_action="silence_topic"; self.state.last_action_at=time()
            except asyncio.CancelledError: break
            except Exception as e: self.state.last_error=str(e)[:300]
            await asyncio.sleep(15)

director=Director()
