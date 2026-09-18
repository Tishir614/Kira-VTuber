"""Local multimodal vision for Kira's isolated Cloud desktop."""
from __future__ import annotations
import base64, json
import httpx
from .config import settings
from .settings_store import settings_store
from .cloud_client import _url

def vision_model()->str:
    return settings_store.load().get("vision_model","qwen2.5vl:3b")

async def cloud_frame()->bytes:
    async with httpx.AsyncClient(timeout=15) as c:
        r=await c.get(_url()+"/screen");r.raise_for_status()
        return base64.b64decode(r.json()["png_base64"])

async def analyze_game(goal:str="", previous:str="")->dict:
    image=base64.b64encode(await cloud_frame()).decode()
    prompt="""Analyze this single-player game frame. Return ONLY JSON with:
scene (short description), ui_state (gameplay|menu|dialog|loading|unknown),
player_state, threats (array), interactables (array), visible_text (array),
navigation (array of useful directions), location, quests (array), inventory (array), death_detected (boolean), progress, suggested_action, confidence (0..1).
Use only visible evidence. Never invent hidden state."""
    if goal:prompt+=f"\nGoal: {goal}"
    if previous:prompt+=f"\nPrevious observation for change detection: {previous[:1200]}"
    payload={"model":vision_model(),"stream":False,"format":"json","options":{"temperature":0.15},
             "messages":[{"role":"user","content":prompt,"images":[image]}]}
    async with httpx.AsyncClient(timeout=90) as c:
        r=await c.post(settings.llm_base_url.rstrip("/")+"/api/chat",json=payload);r.raise_for_status()
        raw=r.json().get("message",{}).get("content","").strip()
    try:return json.loads(raw)
    except Exception:return {"scene":raw,"ui_state":"unknown","confidence":0.0,"suggested_action":""}

async def describe_game(goal:str="")->str:
    return json.dumps(await analyze_game(goal),ensure_ascii=False)

async def status():
    try:
        async with httpx.AsyncClient(timeout=4) as c:
            r=await c.get(settings.llm_base_url.rstrip("/")+"/api/tags");r.raise_for_status()
            names=[m.get("name","") for m in r.json().get("models",[])]
        model=vision_model()
        return {"available":any(n==model or n.startswith(model+"-") for n in names),"model":model,"installed":names}
    except Exception as e:return {"available":False,"model":vision_model(),"error":str(e)}
