"""Self-calibration of conversational AI for spoken VTuber output."""
from __future__ import annotations
import re,time
from .llm import chat
from .character_runtime import load,save,capabilities

SAMPLES=("Привет! Представься зрителям одной короткой репликой.","Тебе написали смешное сообщение в чате. Ответь естественно.","Поблагодари зрителя за поддержку коротко и эмоционально.")

def _score(text,caps):
 words=len(re.findall(r"\\w+",text,re.U));sent=max(1,len(re.findall(r"[.!?]+",text)))
 target=24 if sum(bool(v) for v in caps.values())>=7 else 18
 length=max(0.0,1-abs(words-target)/max(target,1))
 speech=1.0 if 5<=words<=45 else .45
 return round((length*.7+speech*.3)*100,1),words,sent

async def calibrate_ai():
 caps=capabilities();results=[]
 for prompt in SAMPLES:
  t=time.monotonic();answer=await chat(prompt,[])
  score,words,sent=_score(answer,caps)
  results.append({"prompt":prompt,"answer":answer,"score":score,"words":words,"sentences":sent,"latency_ms":round((time.monotonic()-t)*1000)})
 avg=sum(x["score"] for x in results)/len(results);avg_words=sum(x["words"] for x in results)/len(results)
 current=load();ai=current.get("ai",{}).copy()
 temp=float(ai.get("temperature",.75))
 if avg_words>30:temp=max(.55,temp-.05)
 elif avg_words<12:temp=min(.9,temp+.04)
 ai.update({"temperature":round(temp,2),"target_spoken_words":24 if sum(bool(v) for v in caps.values())>=7 else 18,"calibration_score":round(avg,1),"calibrated":True})
 save({"ai":ai})
 return {"ok":True,"score":round(avg,1),"samples":results,"profile":load()}
