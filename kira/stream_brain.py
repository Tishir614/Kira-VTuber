from dataclasses import dataclass, asdict
from time import time
import random

@dataclass
class StreamBrainConfig:
    mode: str = "active"
    global_cooldown: float = 8.0
    per_viewer_cooldown: float = 20.0
    mention_required: bool = True
    max_reply_chars: int = 280

class StreamBrain:
    def __init__(self):
        self.config=StreamBrainConfig(); self.last_reply=0.0; self.viewer_last={}
    def snapshot(self): return asdict(self.config)
    def configure(self,**patch):
        for k,v in patch.items():
            if hasattr(self.config,k) and v is not None: setattr(self.config,k,v)
    def should_reply(self,ev):
        now=time(); text=ev.text.lower()
        if now-self.last_reply < self.config.global_cooldown: return False
        if now-self.viewer_last.get((ev.platform,ev.user.lower()),0)<self.config.per_viewer_cooldown: return False
        mentioned=any(n in text for n in ("кира","kira"))
        if self.config.mention_required and not mentioned: return False
        if self.config.mode=="quiet" and not mentioned: return False
        if self.config.mode=="chaos" and not mentioned and random.random()>0.18: return False
        return True
    def mark_reply(self,ev):
        now=time(); self.last_reply=now; self.viewer_last[(ev.platform,ev.user.lower())]=now

stream_brain=StreamBrain()
