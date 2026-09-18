from dataclasses import dataclass, asdict
from time import time

@dataclass
class SubtitleState:
    speaker: str="Kira"
    text: str=""
    visible: bool=True
    updated_at: float=0.0

class Subtitles:
    def __init__(self): self.state=SubtitleState(updated_at=time())
    def set(self,text,speaker="Kira"):
        self.state.text=text; self.state.speaker=speaker; self.state.updated_at=time()
    def clear(self): self.set("")
    def snapshot(self): return asdict(self.state)

subtitles=Subtitles()
