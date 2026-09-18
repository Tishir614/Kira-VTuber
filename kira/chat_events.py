import asyncio
from dataclasses import dataclass, asdict
from time import time

@dataclass
class ChatEvent:
    platform: str
    user: str
    text: str
    kind: str = "message"
    at: float = 0.0

class ChatQueue:
    def __init__(self):
        self.q=asyncio.Queue(maxsize=200)
        self.recent={}
    def push(self,platform,user,text,kind="message"):
        text=(text or "").strip()
        if not text: return False
        key=(platform,user,text)
        now=time()
        if now-self.recent.get(key,0)<8: return False
        self.recent[key]=now
        if self.q.full(): return False
        self.q.put_nowait(ChatEvent(platform,user,text,kind,now))
        return True
    async def pop(self):
        return await self.q.get()

chat_queue=ChatQueue()
