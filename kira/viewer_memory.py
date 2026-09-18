import json
from pathlib import Path
from threading import Lock
from time import time

class ViewerMemory:
    def __init__(self,path="runtime/viewers.json"):
        self.path=Path(path); self.lock=Lock(); self.path.parent.mkdir(parents=True,exist_ok=True)
    def _load(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception: return {}
    def _save(self,data): self.path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    def see(self,platform,user):
        with self.lock:
            d=self._load(); key=f"{platform}:{user.lower()}"; v=d.get(key,{"platform":platform,"user":user,"messages":0,"events":{},"facts":[],"first_seen":time()})
            v["user"]=user; v["messages"]+=1; v["last_seen"]=time(); d[key]=v; self._save(d); return v
    def event(self,platform,user,kind):
        with self.lock:
            d=self._load(); key=f"{platform}:{user.lower()}"; v=d.get(key,{"platform":platform,"user":user,"messages":0,"events":{},"facts":[],"first_seen":time()})
            v["events"][kind]=v["events"].get(kind,0)+1; v["last_seen"]=time(); d[key]=v; self._save(d); return v
    def remember(self,platform,user,fact):
        fact=fact.strip()
        if not fact: return None
        with self.lock:
            d=self._load(); key=f"{platform}:{user.lower()}"; v=d.get(key,{"platform":platform,"user":user,"messages":0,"events":{},"facts":[],"first_seen":time()})
            if fact not in v["facts"]: v["facts"]=(v["facts"]+[fact])[-20:]
            d[key]=v; self._save(d); return v
    def get(self,platform,user): return self._load().get(f"{platform}:{user.lower()}")
    def forget(self,platform,user):
        with self.lock:
            d=self._load(); removed=d.pop(f"{platform}:{user.lower()}",None) is not None; self._save(d); return removed
    def list(self): return sorted(self._load().values(),key=lambda v:v.get("last_seen",0),reverse=True)[:200]

viewer_memory=ViewerMemory()
