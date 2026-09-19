"""Per-character profiles for Kira Studio."""
from __future__ import annotations
import json,os,re,uuid
from pathlib import Path
DATA=Path(os.environ.get("KIRA_DATA_DIR","runtime"))
ROOT=DATA/"characters"; INDEX=ROOT/"index.json"
def _read(p,default):
 try:return json.loads(p.read_text("utf-8"))
 except Exception:return default
def _write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),"utf-8")
def _index():
 x=_read(INDEX,{"active":"kira","items":[]})
 if not x.get("items"):x={"active":"kira","items":[{"id":"kira","name":"Kira"}]};_write(INDEX,x)
 return x
def active_id():return _index().get("active") or "kira"
def path(cid=None):return ROOT/(cid or active_id())/"profile.json"
def get(cid=None):
 cid=cid or active_id();x=_read(path(cid),{})
 return {"id":cid,"name":x.get("name","Kira" if cid=="kira" else cid),**x}
def list_all():
 idx=_index();return {"active":idx["active"],"characters":[get(x["id"]) for x in idx["items"]]}
def create(name):
 name=(name or "Character").strip()[:64];base=re.sub(r"[^a-z0-9]+","-",name.lower()).strip("-") or "character";cid=base
 ids={x["id"] for x in _index()["items"]}
 if cid in ids:cid=base+"-"+uuid.uuid4().hex[:6]
 idx=_index();idx["items"].append({"id":cid,"name":name});_write(INDEX,idx);_write(path(cid),{"name":name})
 return get(cid)
def save_profile(cid,patch):
 if cid not in {x["id"] for x in _index()["items"]}:raise ValueError("Unknown character")
 x=get(cid)
 for k,v in patch.items():
  if k in {"id"}:continue
  if isinstance(v,dict) and isinstance(x.get(k),dict):x[k]={**x[k],**v}
  else:x[k]=v
 _write(path(cid),{k:v for k,v in x.items() if k!="id"});return get(cid)
def activate(cid):
 idx=_index()
 if cid not in {x["id"] for x in idx["items"]}:raise ValueError("Unknown character")
 idx["active"]=cid;_write(INDEX,idx)
 p=get(cid)
 try:
  from .catalog import installed,_save,CATALOG
  st=installed();vid=p.get("voice",{}).get("id")
  if vid and vid in st.get("voices",[]):
   item=next((x for x in CATALOG["voices"] if x["id"]==vid),None)
   if item:
    eng=item.get("engine","piper");st["active_voice_id"]=vid;st["active_voice_engine"]=eng
    st["active_voice"]="" if item.get("preset") else str(DATA/"voices"/vid/Path(item["model"]).name);_save(st)
 except Exception:pass
 return {"active":cid,"profile":p}
