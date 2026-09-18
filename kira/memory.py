from collections import deque
from dataclasses import dataclass, field

@dataclass
class LocalMemory:
    max_messages: int = 40
    messages: deque = field(default_factory=lambda: deque(maxlen=40))

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def history(self) -> list[dict]:
        return list(self.messages)

memory = LocalMemory()
