from abc import ABC, abstractmethod

class ChatAdapter(ABC):
    platform="unknown"
    @abstractmethod
    async def run(self): ...
    @abstractmethod
    async def stop(self): ...
