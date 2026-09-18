"""Slow strategic game loop for Kira Cloud.
Designed for single-player/offline games, not competitive multiplayer automation.
"""
from __future__ import annotations
import asyncio, base64, json
import httpx
from .cloud_client import _url
from .llm import chat
from .vision import describe_game

ACTIONS={"move","look","click","wait","done"}
KEYS={"w","a","s","d","space","shift","ctrl","e","f","r","q","escape","enter","up","down","left","right"}

async def frame():
    async with httpx.AsyncClient(timeout=15) as c:
        r=await c.get(_url()+"/screen");r.raise_for_status();return r.json()

async def decide(goal:str, note:str=""):
    prompt=f"""You are Kira playing a single-player game in your isolated desktop.
Goal: {goal}
Game-state note: {note or 'No vision description is available yet.'}
Choose one small safe action. Return ONLY JSON:
{{"action":"move|look|click|wait|done","keys":[],"hold_ms":80,"dx":0,"dy":0,"reason":""}}
Allowed keys: {sorted(KEYS)}. Never interact with the host OS or automate competitive multiplayer."""
    raw=await chat(prompt,[])
    try: a=json.loads(raw[raw.find("{"):raw.rfind("}")+1])
    except Exception:return {"action":"wait","reason":"invalid planner output"}
    if a.get("action") not in ACTIONS:return {"action":"wait","reason":"blocked action"}
    a["keys"]=[k for k in a.get("keys",[]) if k in KEYS][:4]
    return a

async def execute(a):
    action=a.get("action")
    if action in {"done","wait"}:
        await asyncio.sleep(.25);return {"ok":True}
    path,payload=("/game/input",{"keys":a.get("keys",[]),"hold_ms":a.get("hold_ms",80)}) if action=="move" else ("/game/mouse",{"dx":a.get("dx",0),"dy":a.get("dy",0)}) if action=="look" else ("/game/click",{})
    async with httpx.AsyncClient(timeout=5) as c:
        r=await c.post(_url()+path,json=payload);r.raise_for_status();return r.json()

async def run(goal:str,steps:int=20):
    trace=[]
    for _ in range(max(1,min(steps,60))):
        try: note=await describe_game(goal)
        except Exception as exc: note=f"Vision unavailable: {exc}"
        a=await decide(goal,note);trace.append({"vision":note[:1200],"action":a})
        if a.get("action")=="done":return {"ok":True,"done":True,"trace":trace}
        await execute(a)
    return {"ok":True,"done":False,"trace":trace,"reason":"step limit reached"}
