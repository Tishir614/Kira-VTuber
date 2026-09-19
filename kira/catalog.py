"""Installable catalog for Kira Studio. Installs one selected component at a time."""
from __future__ import annotations
import asyncio, json, os, shutil, tempfile, time, uuid
from pathlib import Path
from urllib.request import Request, urlopen

DATA=Path(os.environ.get("KIRA_DATA_DIR","runtime"))
JOBS={}

def jobs(): return list(JOBS.values())
def job(job_id): return JOBS.get(job_id)
async def install_job(kind,item_id):
 jid=uuid.uuid4().hex[:12]; j={"id":jid,"kind":kind,"item_id":item_id,"status":"queued","progress":0,"created":time.time(),"error":""};JOBS[jid]=j
 async def run():
  try:
   j.update(status="installing",progress=1,bytes_done=0,bytes_total=0,speed_bps=0);await install(kind,item_id,j);j.update(status="done",progress=100)
  except Exception as exc:j.update(status="error",error=str(exc),progress=0)
 asyncio.create_task(run());return j
CATALOG={
 "voices":[
  {"id":"ru_RU-irina-medium","name":"Ирина","gender":"female","lang":"ru-RU","engine":"piper","style":"спокойный, естественный","size_mb":65,"model":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx","config":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx.json"},
  {"id":"ru_RU-dmitri-medium","name":"Дмитрий","gender":"male","lang":"ru-RU","engine":"piper","model":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx","config":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx.json"}],
 "ai":[
  {"id":"qwen3:4b","name":"Qwen3 4B","engine":"ollama","note":"Быстрая локальная модель","ram_gb":6,"quality":"Хорошая","speed":"Быстро"},
  {"id":"qwen3:8b","name":"Qwen3 8B","engine":"ollama","note":"Баланс качества и скорости","ram_gb":10,"quality":"Выше","speed":"Средне"},
  {"id":"qwen3:14b","name":"Qwen3 14B","engine":"ollama","note":"Более тяжёлая модель","ram_gb":18,"quality":"Высокая","speed":"Тяжелее"}],
 "plugins":[
  {"id":"twitch","name":"Twitch","kind":"integration","note":"Чат и события стрима","category":"Стрим"},
  {"id":"youtube","name":"YouTube","kind":"integration","note":"Чат и события трансляции","category":"Стрим"},
  {"id":"telegram","name":"Telegram","kind":"integration","note":"Канал и сообщения","category":"Соцсети"},
  {"id":"obs","name":"OBS","kind":"integration","note":"Управление эфиром","category":"Стрим"}]}
def installed():
 p=DATA/"catalog-installed.json"
 try:return json.loads(p.read_text("utf-8"))
 except Exception:return {"voices":[],"ai":[],"plugins":[],"active_voice":"","active_ai":""}
def _save(x):
 DATA.mkdir(parents=True,exist_ok=True);(DATA/"catalog-installed.json").write_text(json.dumps(x,ensure_ascii=False,indent=2),"utf-8")
def _download(url: str, target: Path, progress=None):
 target.parent.mkdir(parents=True,exist_ok=True); part=target.with_suffix(target.suffix+".part")
 req=Request(url,headers={"User-Agent":"KiraStudio/1.0"})
 with urlopen(req,timeout=90) as r, part.open("wb") as out:
  total=int(r.headers.get("Content-Length") or 0);done=0;t0=time.time()
  while True:
   chunk=r.read(1024*512)
   if not chunk:break
   out.write(chunk);done+=len(chunk)
   if progress:progress(done,total,max(time.time()-t0,.001))
 os.replace(part,target)
 return done,total

async def install(kind,item_id,job_state=None):
 item=next((x for x in CATALOG.get(kind,[]) if x["id"]==item_id),None)
 if not item:raise ValueError("Unknown catalog item")
 st=installed()
 if kind=="voices":
  d=DATA/"voices"/item_id;d.mkdir(parents=True,exist_ok=True)
  files=[("model",.94),("config",.06)]
  for key,weight in files:
   target=d/Path(item[key]).name
   base=0 if key=="model" else 94
   def report(done,total,elapsed,b=base,w=weight):
    if job_state is not None:
     pct=(done/total if total else 0);job_state.update(bytes_done=done,bytes_total=total,speed_bps=int(done/elapsed),progress=min(99,int(b+pct*w*100)))
   await asyncio.to_thread(_download,item[key],target,report)
  st["active_voice"]=str(d/Path(item["model"]).name)
 elif kind=="ai":
  ollama=shutil.which("ollama")
  if not ollama:raise RuntimeError("Ollama is not installed")
  p=await asyncio.create_subprocess_exec(ollama,"pull",item_id,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT)
  if job_state is not None:job_state.update(progress=25)
  while True:
   line=await p.stdout.readline()
   if not line:break
   if job_state is not None:
    txt=line.decode("utf-8","ignore");job_state["message"]=txt.strip()[-160:]
    import re
    m=re.search(r"(\d{1,3})%",txt)
    if m:job_state["progress"]=min(99,int(m.group(1)))
  if await p.wait():raise RuntimeError("Ollama pull failed")
  st["active_ai"]=item_id
 elif kind=="plugins":
  st.setdefault("plugins",[])
  if job_state is not None:job_state.update(progress=95)
 st.setdefault(kind,[])
 if item_id not in st[kind]:st[kind].append(item_id)
 _save(st);return {"ok":True,"installed":st,"item":item}

async def use(kind,item_id):
 st=installed()
 if item_id not in st.get(kind,[]):raise ValueError("Item is not installed")
 if kind=="voices":
  item=next(x for x in CATALOG["voices"] if x["id"]==item_id);d=DATA/"voices"/item_id
  st["active_voice"]=str(d/Path(item["model"]).name)
 elif kind=="ai":st["active_ai"]=item_id
 elif kind=="plugins":st["active_plugin"]=item_id
 _save(st);return {"ok":True,"installed":st}

async def remove(kind,item_id):
 st=installed()
 if kind=="voices":
  shutil.rmtree(DATA/"voices"/item_id,ignore_errors=True)
  if item_id in st.get("voices",[]):st["voices"].remove(item_id)
  if item_id in st.get("active_voice",""):st["active_voice"]=""
 elif kind=="ai":
  ollama=shutil.which("ollama")
  if ollama:
   p=await asyncio.create_subprocess_exec(ollama,"rm",item_id);await p.wait()
  if item_id in st.get("ai",[]):st["ai"].remove(item_id)
  if st.get("active_ai")==item_id:st["active_ai"]=""
 elif kind=="plugins":
  if item_id in st.get("plugins",[]):st["plugins"].remove(item_id)
 _save(st);return {"ok":True,"installed":st}

async def voice_preview(item_id,text="Привет! Я Кира. Так будет звучать мой голос."):
 item=next((x for x in CATALOG["voices"] if x["id"]==item_id),None)
 if not item:raise ValueError("Unknown voice")
 st=installed()
 if item_id not in st.get("voices",[]):await install("voices",item_id)
 model=DATA/"voices"/item_id/Path(item["model"]).name
 piper=shutil.which("piper")
 if not piper:raise RuntimeError("Piper is not installed")
 out=Path(tempfile.gettempdir())/("kira-preview-"+item_id+".wav")
 p=await asyncio.create_subprocess_exec(piper,"--model",str(model),"--output_file",str(out),stdin=asyncio.subprocess.PIPE)
 await p.communicate(text.encode("utf-8"))
 if p.returncode:raise RuntimeError("Voice preview failed")
 return out
