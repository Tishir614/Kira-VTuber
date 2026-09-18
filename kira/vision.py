"""Local multimodal vision through Ollama's image-capable chat API."""
from __future__ import annotations
import base64
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

async def describe_game(goal:str="")->str:
    image=base64.b64encode(await cloud_frame()).decode()
    prompt=("Describe the current single-player game screen for an autonomous player. "
            "Focus on player state, menus, interactable objects, threats, navigation, visible text and the next useful action. "
            "Do not guess invisible information.")
    if goal:prompt+=f" Current goal: {goal}"
    payload={"model":vision_model(),"stream":False,"messages":[{"role":"user","content":prompt,"images":[image]}]}
    async with httpx.AsyncClient(timeout=90) as c:
        r=await c.post(settings.llm_base_url.rstrip("/")+"/api/chat",json=payload)
        r.raise_for_status()
        return r.json().get("message",{}).get("content","").strip()

async def status():
    try:
        async with httpx.AsyncClient(timeout=4) as c:
            r=await c.get(settings.llm_base_url.rstrip("/")+"/api/tags");r.raise_for_status()
            names=[m.get("name","") for m in r.json().get("models",[])]
        model=vision_model()
        return {"available":any(n==model or n.startswith(model+"-") for n in names),"model":model,"installed":names}
    except Exception as e:return {"available":False,"model":vision_model(),"error":str(e)}
