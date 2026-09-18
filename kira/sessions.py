import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

class SessionStore:
    def __init__(self, root="runtime/sessions"):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
    def new(self):
        sid=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+uuid4().hex[:6]
        self._write(sid,{"id":sid,"created_at":datetime.now(timezone.utc).isoformat(),"messages":[]})
        return sid
    def _path(self,sid): return self.root/(sid+".json")
    def _write(self,sid,data): self._path(sid).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    def add(self,sid,role,content):
        p=self._path(sid)
        data=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"id":sid,"messages":[]}
        data["messages"].append({"role":role,"content":content,"at":datetime.now(timezone.utc).isoformat()})
        data["messages"]=data["messages"][-200:]; self._write(sid,data)
    def get(self,sid):
        p=self._path(sid)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    def list(self):
        out=[]
        for p in sorted(self.root.glob("*.json"),reverse=True)[:50]:
            try:
                d=json.loads(p.read_text(encoding="utf-8")); out.append({"id":d["id"],"created_at":d.get("created_at"),"messages":len(d.get("messages",[]))})
            except Exception: pass
        return out
sessions=SessionStore()
