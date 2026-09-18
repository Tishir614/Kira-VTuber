import asyncio
from .audience import audience
from .chat_events import chat_queue
from .pipeline import respond
from .stream_brain import stream_brain
from .viewer_memory import viewer_memory
from .director import director

class StreamChatController:
    def __init__(self): self.enabled=False; self._task=None
    def start(self):
        self.enabled=True
        if not self._task or self._task.done(): self._task=asyncio.create_task(self._loop())
    def stop(self):
        self.enabled=False
        if self._task and not self._task.done(): self._task.cancel()
    async def _loop(self):
        while self.enabled:
            ev=await chat_queue.pop(); audience.see(ev.platform,ev.user); director.note_chat()
            profile=viewer_memory.see(ev.platform,ev.user)
            if ev.kind != "message":
                viewer_memory.event(ev.platform,ev.user,ev.kind)
                try: await director.react_event(ev.kind,ev.user,ev.platform,ev.text)
                except Exception: pass
                continue
            if ev.kind=="message" and not stream_brain.should_reply(ev): continue
            if ev.kind=="message":
                prompt=f"Сообщение из {ev.platform} от зрителя @{ev.user}: {ev.text}\nОтветь зрителю естественно, максимум {stream_brain.config.max_reply_chars} символов."
            else:
                prompt=f"Событие стрима {ev.kind} на {ev.platform}, зритель @{ev.user}: {ev.text}. Коротко и естественно отреагируй."
            try:
                await respond(prompt,True); stream_brain.mark_reply(ev)
            except Exception: pass

stream_chat=StreamChatController()
