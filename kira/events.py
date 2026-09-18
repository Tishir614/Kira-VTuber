import asyncio
from dataclasses import asdict, dataclass
from time import time

@dataclass
class KiraEvent:
    type: str
    payload: dict
    at: float

class EventBus:
    def __init__(self):
        self._listeners: set[asyncio.Queue] = set()

    def subscribe(self):
        q = asyncio.Queue(maxsize=50)
        self._listeners.add(q)
        return q

    def unsubscribe(self, q):
        self._listeners.discard(q)

    def emit(self, event_type: str, **payload):
        event = asdict(KiraEvent(event_type, payload, time()))
        for q in tuple(self._listeners):
            if not q.full():
                q.put_nowait(event)

events = EventBus()
