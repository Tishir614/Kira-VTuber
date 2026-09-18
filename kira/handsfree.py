import asyncio
from dataclasses import dataclass
from .config import settings
from .live2d import live2d
from .microphone import record
from .pipeline import respond
from .stt import stt

@dataclass
class HandsFreeState:
    enabled: bool = False
    wake_word: str = "кира"
    listen_seconds: int = 5
    cooldown_seconds: float = 0.7
    last_heard: str = ""

class HandsFreeController:
    def __init__(self):
        self.state = HandsFreeState()
        self._task: asyncio.Task | None = None

    def snapshot(self):
        return self.state.__dict__.copy()

    def start(self, wake_word: str = "кира"):
        self.state.wake_word = wake_word.strip().lower() or "кира"
        self.state.enabled = True
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self._loop())

    def stop(self):
        self.state.enabled = False
        if self._task and not self._task.done():
            self._task.cancel()

    async def _loop(self):
        while self.state.enabled:
            if live2d.state.speaking:
                await asyncio.sleep(0.2)
                continue
            try:
                live2d.state.listening = True
                audio = await asyncio.to_thread(record, self.state.listen_seconds)
                text = await asyncio.to_thread(stt.transcribe, str(audio), settings.stt_language)
                self.state.last_heard = text
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1.0)
                continue
            finally:
                live2d.state.listening = False

            normalized = text.lower().strip() if text else ""
            wake = self.state.wake_word
            if wake and wake in normalized:
                query = normalized.split(wake, 1)[1].strip(" ,.!?:;-")
                if query:
                    try:
                        await respond(query, True)
                    except Exception:
                        pass
            await asyncio.sleep(self.state.cooldown_seconds)

handsfree = HandsFreeController()
