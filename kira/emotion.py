from dataclasses import dataclass

@dataclass
class AvatarState:
    emotion: str = "neutral"
    speaking: bool = False
    listening: bool = False

state = AvatarState()

def detect_emotion(text: str) -> str:
    t = text.lower()
    if any(x in t for x in ("ха", "смеш", "😂", "😄")): return "happy"
    if any(x in t for x in ("груст", "жаль", "😢")): return "sad"
    if any(x in t for x in ("злю", "бесит", "😡")): return "angry"
    if any(x in t for x in ("ого", "вау", "удив", "😮")): return "surprised"
    return "neutral"
