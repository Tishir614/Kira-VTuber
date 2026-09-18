import asyncio
from .audience import audience
from .chat_events import chat_queue
from .pipeline import respond

class StreamChatController:
    def __init__(self):
        self.enabled=False
        self._task=None
        self.require_mention=True
        self.names=("кира","kira")

    def start(self):
        self.enabled=True
        if not self._task or self._task.done(): self._task=asyncio.create_task(self._loop())

    def stop(self):
        self.enabled=False
        if self._task and not self._task.done(): self._task.cancel()

    async def _loop(self):
        while self.enabled:
            ev=await chat_queue.pop()
            audience.see(ev.platform,ev.user)
            lower=ev.text.lower()
            if self.require_mention and not any(n in lower for n in self.names):
                continue
            prompt=f"Сообщение из {ev.platform} от зрителя @{ev.user}: {ev.text}\nОтветь зрителю естественно и не слишком длинно."
            try: await respond(prompt,True)
            except Exception: pass

stream_chat=StreamChatController()
