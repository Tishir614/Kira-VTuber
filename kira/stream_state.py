from dataclasses import dataclass, asdict

@dataclass
class StreamState:
    scene: str = "chat"
    title: str = ""
    subtitle: str = ""
    show_subtitles: bool = True

state=StreamState()
def snapshot(): return asdict(state)
