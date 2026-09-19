"""PUBG Mobile training-specific visual perception."""
from __future__ import annotations
import base64,json,httpx
from .vision import cloud_frame,vision_model
from .config import settings
PROMPT="""Analyze this PUBG Mobile TRAINING/NON-COMPETITIVE frame only.
Return ONLY JSON:
{"mode":"training|lobby|unknown","health":0,"armor":0,"weapon_primary":"","weapon_secondary":"",
"ammo_current":0,"ammo_reserve":0,"scope":"","attachments":[],"nearby_loot":[],
"training_targets":[],"target_offset":{"x":0,"y":0},"crosshair_target":false,"reload_needed":false,"interact_available":false,
"minimap":{"visible":false,"heading":"","markers":[]},"movement":{"blocked":false},"shot_feedback":{"hit":false,"vertical_drift":0},
"visible_text":[],"confidence":0.0}
Use only visible evidence. Unknown numbers should be -1 and unknown strings empty.
Never infer hidden players, targets or game state."""
async def observe()->dict:
    image=base64.b64encode(await cloud_frame()).decode()
    payload={"model":vision_model(),"stream":False,"format":"json","options":{"temperature":0.05},
      "messages":[{"role":"user","content":PROMPT,"images":[image]}]}
    async with httpx.AsyncClient(timeout=90) as c:
        r=await c.post(settings.llm_base_url.rstrip("/")+"/api/chat",json=payload);r.raise_for_status()
        raw=r.json().get("message",{}).get("content","").strip()
    try:return json.loads(raw)
    except Exception:return {"mode":"unknown","confidence":0.0,"raw":raw[:1000]}
