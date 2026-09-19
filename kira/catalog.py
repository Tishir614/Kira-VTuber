"""Installable catalog for Kira Studio. Installs one selected component at a time."""
from __future__ import annotations
import asyncio, json, os, shutil, tempfile, time, uuid
from pathlib import Path
from urllib.request import Request, urlopen

DATA=Path(os.environ.get("KIRA_DATA_DIR","runtime"))
JOBS={}
ENGINE_PACKAGES={
 "piper":{"name":"Piper","package":"piper-tts","description":"Лёгкий локальный TTS для ONNX-голосов."},
 "kokoro":{"name":"Kokoro","package":"kokoro>=0.9.4","description":"Локальный нейросетевой TTS для персонажных голосов."},
 "gpt-sovits":{"name":"GPT-SoVITS","package":None,"manual":True,"description":"Few-shot TTS. Требует отдельную установку Python 3.10 и системных зависимостей."}
}
def engine_state():
 st=installed(); return [{"id":k,**v,"installed":k in st.get("engines",[])} for k,v in ENGINE_PACKAGES.items()]
async def install_engine(engine_id):
 item=ENGINE_PACKAGES.get(engine_id)
 if not item: raise ValueError("Unknown engine")
 if item.get("manual"): raise RuntimeError("Этот движок требует отдельный установщик и пока не устанавливается одной кнопкой.")
 root=DATA/"engines"/engine_id; venv=root/"venv"
 root.mkdir(parents=True,exist_ok=True)
 import sys
 p=await asyncio.create_subprocess_exec(sys.executable,"-m","venv",str(venv)); rc=await p.wait()
 if rc: raise RuntimeError("Cannot create engine environment")
 pip=venv/("Scripts/pip.exe" if os.name=="nt" else "bin/pip")
 p=await asyncio.create_subprocess_exec(str(pip),"install","--upgrade","pip"); rc=await p.wait()
 if rc: raise RuntimeError("Cannot prepare engine environment")
 p=await asyncio.create_subprocess_exec(str(pip),"install",item["package"]); rc=await p.wait()
 if rc: raise RuntimeError("Engine installation failed")
 st=installed();st.setdefault("engines",[])
 if engine_id not in st["engines"]:st["engines"].append(engine_id)
 _save(st);return {"ok":True,"engines":engine_state()}
async def remove_engine(engine_id):
 if engine_id not in ENGINE_PACKAGES: raise ValueError("Unknown engine")
 shutil.rmtree(DATA/"engines"/engine_id,ignore_errors=True)
 st=installed()
 if engine_id in st.get("engines",[]):st["engines"].remove(engine_id)
 _save(st);return {"ok":True,"engines":engine_state()}

def jobs(): return list(JOBS.values())
def cancel_job(job_id):
 j=JOBS.get(job_id)
 if not j:return None
 if j.get("status") in ("done","error","cancelled"):return j
 j["cancel_requested"]=True;j["status"]="cancelling";return j
def job(job_id): return JOBS.get(job_id)
async def install_job(kind,item_id):
 jid=uuid.uuid4().hex[:12]; j={"id":jid,"kind":kind,"item_id":item_id,"status":"queued","progress":0,"created":time.time(),"error":""};JOBS[jid]=j
 async def run():
  try:
   j.update(status="installing",progress=1,bytes_done=0,bytes_total=0,speed_bps=0);await install(kind,item_id,j);j.update(status="cancelled" if j.get("cancel_requested") else "done",progress=j.get("progress",0) if j.get("cancel_requested") else 100)
  except asyncio.CancelledError:j.update(status="cancelled",error="",speed_bps=0)
  except Exception as exc:j.update(status="error",error=str(exc),progress=0)
 asyncio.create_task(run());return j
CATALOG={
 "voices":[
  {"id":"af_heart","name":"Kokoro Heart","gender":"female","lang":"en-US","engine":"kokoro","style":"тёплый / VTuber","preset":True,"note":"Встроенный голос Kokoro.","source":"hexgrad/Kokoro-82M"},
  {"id":"af_bella","name":"Kokoro Bella","gender":"female","lang":"en-US","engine":"kokoro","style":"яркий / эмоциональный","preset":True,"note":"Встроенный голос Kokoro.","source":"hexgrad/Kokoro-82M"},
  {"id":"af_nicole","name":"Kokoro Nicole","gender":"female","lang":"en-US","engine":"kokoro","style":"чёткий / спокойный","preset":True,"note":"Встроенный голос Kokoro.","source":"hexgrad/Kokoro-82M"},
  {"id":"af_sarah","name":"Kokoro Sarah","gender":"female","lang":"en-US","engine":"kokoro","style":"мягкий","preset":True,"note":"Встроенный голос Kokoro.","source":"hexgrad/Kokoro-82M"},
  {"id":"jf_alpha","name":"Kokoro Alpha JP","gender":"female","lang":"ja-JP","engine":"kokoro","style":"японский / персонажный","preset":True,"note":"Встроенный японский голос Kokoro.","source":"hexgrad/Kokoro-82M"},
  {"id":"jf_nezumi","name":"Kokoro Nezumi JP","gender":"female","lang":"ja-JP","engine":"kokoro","style":"японский / мягкий","preset":True,"note":"Встроенный японский голос Kokoro.","source":"hexgrad/Kokoro-82M"},
  {"id":"gpt-sovits-anime","name":"GPT-SoVITS Anime","gender":"female","lang":"ja/zh/en/ko","engine":"gpt-sovits","style":"аниме / персонажный","note":"Few-shot движок для создания оригинального аниме-голоса из разрешённых записей.","source":"GPT-SoVITS","installable":False},
  {"id":"ru_RU-irina-medium","name":"Ирина","gender":"female","lang":"ru-RU","engine":"piper","style":"спокойный, естественный","size_mb":65,"model":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx","config":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx.json"},
  {"id":"ru_RU-dmitri-medium","name":"Дмитрий","gender":"male","lang":"ru-RU","engine":"piper","model":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx","config":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/dmitri/medium/ru_RU-dmitri-medium.onnx.json"},
  {"id":"ru_RU-denis-medium","name":"Денис","gender":"male","lang":"ru-RU","engine":"piper","size_mb":64,"model":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx","config":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx.json"},
  {"id":"ru_RU-ruslan-medium","name":"Руслан","gender":"male","lang":"ru-RU","engine":"piper","size_mb":64,"model":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/ruslan/medium/ru_RU-ruslan-medium.onnx","config":"https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/ruslan/medium/ru_RU-ruslan-medium.onnx.json"},
  {"id":"stylebert-jp-female1","name":"Anime JP Female","gender":"female","lang":"ja-JP","engine":"style-bert-vits2","style":"аниме, эмоциональный","note":"Style-Bert-VITS2: Female1, японский, эмоции neutral/happy/sad/angry/surprised/fear/disgust","source":"tokusan2/style-bert-vits2-jp","installable":False},
  {"id":"rinne-elu-jp","name":"Rinne Elu JP","gender":"female","lang":"ja-JP","engine":"style-bert-vits2","style":"персонажный, аниме","note":"Персонажный японский Style-Bert-VITS2 голос. Отдельная лицензия модели, требуется проверка условий перед установкой.","source":"kokuren/RinneElu","installable":False}],
 "ai":[
  {"id":"qwen3.5:0.8b","name":"Qwen 3.5 0.8B","engine":"ollama","note":"Очень лёгкая мультимодальная модель","quality":"Базовая","speed":"Очень быстро"},
  {"id":"qwen3.5:2b","name":"Qwen 3.5 2B","engine":"ollama","note":"Лёгкая мультимодальная модель","quality":"Хорошая","speed":"Очень быстро"},
  {"id":"qwen3.5:9b","name":"Qwen 3.5 9B","engine":"ollama","note":"Более сильная мультимодальная модель","quality":"Высокая","speed":"Средне"},
  {"id":"phi4-mini-reasoning","name":"Phi-4 Mini Reasoning","engine":"ollama","note":"Компактная reasoning-модель 3.8B","quality":"Высокая","speed":"Быстро"},
  {"id":"qwen2.5vl:3b","name":"Qwen2.5-VL 3B","engine":"ollama","note":"Лёгкая модель для текста и изображений","quality":"Хорошая","speed":"Быстро"},
  {"id":"granite3.3:2b","name":"Granite 3.3 2B","engine":"ollama","note":"Компактная модель IBM с tools","quality":"Хорошая","speed":"Быстро"},
  {"id":"granite3.3:8b","name":"Granite 3.3 8B","engine":"ollama","note":"Более мощная IBM Granite","quality":"Высокая","speed":"Средне"},
  {"id":"gemma3n:e2b","name":"Gemma 3n E2B","engine":"ollama","note":"Оптимизирована для ноутбуков и мобильных устройств","quality":"Хорошая","speed":"Быстро"},
  {"id":"gemma3n:e4b","name":"Gemma 3n E4B","engine":"ollama","note":"Усиленная Gemma 3n для локальных устройств","quality":"Высокая","speed":"Средне"},
  {"id":"qwen3:4b","name":"Qwen3 4B","engine":"ollama","note":"Быстрая локальная модель","ram_gb":6,"quality":"Хорошая","speed":"Быстро"},
  {"id":"qwen3:8b","name":"Qwen3 8B","engine":"ollama","note":"Баланс качества и скорости","ram_gb":10,"quality":"Выше","speed":"Средне"},
  {"id":"qwen3:14b","name":"Qwen3 14B","engine":"ollama","note":"Более тяжёлая модель","ram_gb":18,"quality":"Высокая","speed":"Тяжелее"},
  {"id":"llama3.2:1b","name":"Llama 3.2 1B","engine":"ollama","note":"Очень лёгкая модель для слабых устройств","quality":"Базовая","speed":"Очень быстро"},
  {"id":"llama3.2:3b","name":"Llama 3.2 3B","engine":"ollama","note":"Компактная мультиязычная модель","quality":"Хорошая","speed":"Быстро"},
  {"id":"gemma3:1b","name":"Gemma 3 1B","engine":"ollama","note":"Лёгкая модель Google","quality":"Базовая","speed":"Очень быстро"},
  {"id":"gemma3:4b","name":"Gemma 3 4B","engine":"ollama","note":"Мультимодальная модель с поддержкой изображений","quality":"Хорошая","speed":"Быстро"},
  {"id":"qwen3.5:4b","name":"Qwen 3.5 4B","engine":"ollama","note":"Новая компактная мультимодальная модель","quality":"Хорошая","speed":"Быстро"},
  {"id":"qwen3-coder:30b","name":"Qwen3 Coder 30B","engine":"ollama","note":"Модель для кода и агентных задач","quality":"Высокая","speed":"Тяжелее"},
  {"id":"mistral-small3.2","name":"Mistral Small 3.2","engine":"ollama","note":"24B, инструменты и изображения","quality":"Высокая","speed":"Тяжелее"},
  {"id":"qwen3.5:0.8b","name":"Qwen 3.5 0.8B","engine":"ollama","note":"Очень лёгкая мультимодальная модель","quality":"Базовая","speed":"Очень быстро"},
  {"id":"qwen3.5:2b","name":"Qwen 3.5 2B","engine":"ollama","note":"Компактная мультимодальная модель","quality":"Хорошая","speed":"Очень быстро"},
  {"id":"qwen3.5:9b","name":"Qwen 3.5 9B","engine":"ollama","note":"Мультимодальная модель среднего размера","quality":"Высокая","speed":"Средне"},
  {"id":"qwen3.5:27b","name":"Qwen 3.5 27B","engine":"ollama","note":"Крупная мультимодальная модель","quality":"Высокая","speed":"Тяжелее"},
  {"id":"deepseek-r1:8b","name":"DeepSeek R1 8B","engine":"ollama","note":"Reasoning-модель","quality":"Высокая","speed":"Средне"},
  {"id":"deepseek-r1:14b","name":"DeepSeek R1 14B","engine":"ollama","note":"Более крупная reasoning-модель","quality":"Высокая","speed":"Тяжелее"},
  {"id":"gemma3:12b","name":"Gemma 3 12B","engine":"ollama","note":"Мультимодальная модель Gemma","quality":"Высокая","speed":"Средне"},
  {"id":"gemma3:27b","name":"Gemma 3 27B","engine":"ollama","note":"Крупная мультимодальная Gemma","quality":"Высокая","speed":"Тяжелее"},
  {"id":"glm-4.7-flash","name":"GLM 4.7 Flash","engine":"ollama","note":"30B-A3B MoE, инструменты и reasoning","quality":"Высокая","speed":"Средне"}],
 "plugins":[
  {"id":"twitch","name":"Twitch","kind":"integration","note":"Чат и события стрима","category":"Стрим"},
  {"id":"youtube","name":"YouTube","kind":"integration","note":"Чат и события трансляции","category":"Стрим"},
  {"id":"telegram","name":"Telegram","kind":"integration","note":"Канал и сообщения","category":"Соцсети"},
  {"id":"obs","name":"OBS","kind":"integration","note":"Управление эфиром","category":"Стрим"},
  {"id":"discord","name":"Discord","kind":"integration","note":"Чаты, события и сообщества","category":"Соцсети"},
  {"id":"web-search","name":"Web Search","kind":"integration","note":"Поиск актуальной информации в интернете","category":"Инструменты"},
  {"id":"memory","name":"Kira Memory","kind":"builtin","note":"Долговременная локальная память","category":"ИИ"},
  {"id":"vision","name":"Kira Vision","kind":"builtin","note":"Анализ изображений и экрана","category":"ИИ"},
  {"id":"stt","name":"Speech to Text","kind":"builtin","note":"Локальное распознавание речи","category":"Голос"},
  {"id":"live2d","name":"Live2D","kind":"builtin","note":"Управление аватаром Kira","category":"Аватар"}]}
def installed():
 p=DATA/"catalog-installed.json"
 try:return json.loads(p.read_text("utf-8"))
 except Exception:return {"voices":[],"ai":[],"plugins":[],"engines":[],"active_voice":"","active_ai":""}
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
   if progress:
    progress(done,total,max(time.time()-t0,.001))
 os.replace(part,target)
 return done,total

async def install(kind,item_id,job_state=None):
 item=next((x for x in CATALOG.get(kind,[]) if x["id"]==item_id),None)
 if not item:raise ValueError("Unknown catalog item")
 st=installed()
 if kind=="voices":
  if item.get("installable") is False:raise RuntimeError("Этот голос пока доступен только как описание/пресет и не имеет отдельного пакета модели")
  engine=item.get("engine","piper")
  if item.get("preset") and engine=="kokoro":
   if engine not in st.get("engines",[]):raise RuntimeError("Сначала установите движок kokoro")
   st.setdefault("voices",[])
   if item_id not in st["voices"]:st["voices"].append(item_id)
   st["active_voice"]="";st["active_voice_id"]=item_id;st["active_voice_engine"]="kokoro"
   _save(st);return {"ok":True,"installed":st,"item":item}
  if engine!="piper" and engine not in st.get("engines",[]):raise RuntimeError("Сначала установите движок "+engine)
  if "model" not in item or "config" not in item:raise RuntimeError("Для этого голоса требуется пакет модели, установка будет добавлена отдельно")
  d=DATA/"voices"/item_id;d.mkdir(parents=True,exist_ok=True)
  files=[("model",.94),("config",.06)]
  for key,weight in files:
   target=d/Path(item[key]).name
   base=0 if key=="model" else 94
   def report(done,total,elapsed,b=base,w=weight):
    if job_state is not None:
     if job_state.get("cancel_requested"): raise asyncio.CancelledError()
     pct=(done/total if total else 0);job_state.update(bytes_done=done,bytes_total=total,speed_bps=int(done/elapsed),progress=min(99,int(b+pct*w*100)))
   await asyncio.to_thread(_download,item[key],target,report)
  st["active_voice"]=str(d/Path(item["model"]).name);st["active_voice_id"]=item_id;st["active_voice_engine"]=engine
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
  item=next(x for x in CATALOG["voices"] if x["id"]==item_id);engine=item.get("engine","piper")
  if item.get("preset") and engine=="kokoro":st["active_voice"]="";st["active_voice_id"]=item_id;st["active_voice_engine"]="kokoro"
  else:
   d=DATA/"voices"/item_id;st["active_voice"]=str(d/Path(item["model"]).name);st["active_voice_id"]=item_id;st["active_voice_engine"]=engine
 elif kind=="ai":st["active_ai"]=item_id
 elif kind=="plugins":st["active_plugin"]=item_id
 _save(st);return {"ok":True,"installed":st}

async def remove(kind,item_id):
 st=installed()
 if kind=="voices":
  shutil.rmtree(DATA/"voices"/item_id,ignore_errors=True)
  if item_id in st.get("voices",[]):st["voices"].remove(item_id)
  if item_id==st.get("active_voice_id"):
   st["active_voice"]="";st["active_voice_id"]="";st["active_voice_engine"]=""
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
