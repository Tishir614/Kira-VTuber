"""Adaptive single-player game loop for Kira Cloud."""
from __future__ import annotations
import asyncio, json
import httpx
from .cloud_client import _url
from .llm import chat
from .vision import analyze_game
from .game_memory import recall, remember
from .game_reflex import choose as reflex_choose, record as reflex_record

ACTIONS={"move","look","click","wait","done"}
KEYS={"w","a","s","d","space","shift","ctrl","e","f","r","q","escape","enter","up","down","left","right"}

async def decide(goal:str, vision:dict, memory:dict, recent:list):
    prompt=f"""You are Kira playing a single-player game in your isolated desktop.
Goal: {goal}
Vision JSON: {json.dumps(vision,ensure_ascii=False)[:7000]}
Learned memory: {json.dumps(memory,ensure_ascii=False)[:2500]}
Recent actions: {json.dumps(recent[-5:],ensure_ascii=False)[:2000]}
Choose ONE small action. Prefer visible evidence, avoid repeating an action that caused no progress.
If confidence is low, look around or wait rather than committing to a long move.
Return ONLY JSON:
{{"action":"move|look|click|wait|done","keys":[],"hold_ms":80,"dx":0,"dy":0,"reason":""}}
Allowed keys: {sorted(KEYS)}. Never interact with the host OS or automate competitive multiplayer."""
    raw=await chat(prompt,[])
    try:a=json.loads(raw[raw.find("{"):raw.rfind("}")+1])
    except Exception:return {"action":"wait","reason":"invalid planner output"}
    if a.get("action") not in ACTIONS:return {"action":"wait","reason":"blocked action"}
    a["keys"]=[k for k in a.get("keys",[]) if k in KEYS][:4]
    a["hold_ms"]=max(20,min(int(a.get("hold_ms",80)),700))
    a["dx"]=max(-500,min(int(a.get("dx",0)),500));a["dy"]=max(-500,min(int(a.get("dy",0)),500))
    return a

async def execute(a):
    action=a.get("action")
    if action in {"done","wait"}:await asyncio.sleep(.25);return {"ok":True}
    path,payload=("/game/input",{"keys":a.get("keys",[]),"hold_ms":a["hold_ms"]}) if action=="move" else ("/game/mouse",{"dx":a["dx"],"dy":a["dy"]}) if action=="look" else ("/game/click",{})
    async with httpx.AsyncClient(timeout=5) as c:
        r=await c.post(_url()+path,json=payload);r.raise_for_status();return r.json()

def signature(v:dict)->str:
    return json.dumps({k:v.get(k) for k in ("scene","ui_state","player_state","progress")},ensure_ascii=False,sort_keys=True)[:1200]

async def run(goal:str,steps:int=20,game_id:str="default"):
    trace=[];recent=[];previous="";stagnant=0;mem=recall(game_id)
    for _ in range(max(1,min(steps,60))):
        try:v=await analyze_game(goal,previous)
        except Exception as exc:v={"scene":f"Vision unavailable: {exc}","confidence":0}
        sig=signature(v);stagnant=stagnant+1 if sig==previous else 0
        if stagnant>=3:
            remember(game_id,"failure",f"No visible progress after actions: {recent[-3:]}")
            recent=[];stagnant=0;mem=recall(game_id)
        reflex=reflex_choose(v)
        if reflex.get("action")!="wait":
            await execute(reflex);reflex_record(reflex);recent.append(reflex)
            await asyncio.sleep(.08)
            try:v=await analyze_game(goal,sig)
            except Exception:pass
        a=await decide(goal,v,mem,recent)
        trace.append({"vision":v,"action":a});recent.append(a)
        if a.get("action")=="done":
            remember(game_id,"note",f"Goal completed: {goal}. Final state: {sig}")
            return {"ok":True,"done":True,"trace":trace}
        await execute(a);previous=sig
    remember(game_id,"note",f"Session ended at step limit. Goal: {goal}")
    return {"ok":True,"done":False,"trace":trace,"reason":"step limit reached"}
