"""Planner/executor for Kira's isolated Cloud desktop."""
from __future__ import annotations
import json
import httpx
from .cloud_client import _url
from .llm import chat

ALLOWED={"click","type","key","scroll","open","search","done"}

async def _get(path):
    async with httpx.AsyncClient(timeout=15) as c:
        r=await c.get(_url()+path);r.raise_for_status();return r.json()

async def observe():
    return await _get("/browser/a11y")

async def decide(goal:str, observation:dict):
    prompt=f"""You control only Kira's isolated browser desktop.
Goal: {goal}
Current page: {json.dumps(observation,ensure_ascii=False)[:9000]}
Return ONLY JSON: {{"action":"click|type|key|scroll|open|search|done","x":0,"y":0,"text":"","key":"","url":"","query":"","reason":""}}.
Never request shell commands, credentials, purchases, account changes, downloads of executables, or access to the host computer."""
    raw=await chat(prompt,[])
    try:
        obj=json.loads(raw[raw.find("{"):raw.rfind("}")+1])
    except Exception:return {"action":"done","reason":"planner returned invalid JSON"}
    if obj.get("action") not in ALLOWED:return {"action":"done","reason":"blocked action"}
    return obj

async def execute(action:dict):
    a=action.get("action")
    if a=="done":return {"ok":True,"done":True}
    mapping={"click":("/input/click",{"x":action.get("x",0),"y":action.get("y",0)}),
             "type":("/input/type",{"text":action.get("text","")}),
             "key":("/input/key",{"key":action.get("key","")}),
             "scroll":("/input/scroll",{"dy":action.get("dy",500)}),
             "open":("/browser/open",{"url":action.get("url","")}),
             "search":("/browser/search",{"query":action.get("query","")})}
    path,payload=mapping[a]
    async with httpx.AsyncClient(timeout=35) as c:
        r=await c.post(_url()+path,json=payload);r.raise_for_status();return r.json()

async def run_goal(goal:str,max_steps:int=12):
    trace=[]
    for _ in range(max(1,min(max_steps,20))):
        obs=await observe();act=await decide(goal,obs);trace.append({"page":obs.get("title"),"action":act})
        if act.get("action")=="done":return {"ok":True,"done":True,"trace":trace}
        await execute(act)
    return {"ok":True,"done":False,"trace":trace,"reason":"step limit reached"}
