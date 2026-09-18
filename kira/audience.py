from dataclasses import dataclass
from time import time

@dataclass
class Viewer:
    name: str
    platform: str
    last_seen: float
    messages: int = 0

class Audience:
    def __init__(self): self.viewers={}
    def see(self,platform,name):
        key=f"{platform}:{name.lower()}"
        v=self.viewers.get(key) or Viewer(name,platform,time(),0)
        v.last_seen=time(); v.messages+=1; self.viewers[key]=v
        return v
    def snapshot(self):
        return [v.__dict__ for v in sorted(self.viewers.values(),key=lambda x:x.last_seen,reverse=True)[:100]]

audience=Audience()
