import httpx
from .settings_store import settings_store

def _url():
    return settings_store.load().get("cloud_agent_url","http://127.0.0.1:8766").rstrip("/")

async def cloud_status():
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r=await c.get(_url()+"/health");r.raise_for_status();return {"connected":True,**r.json()}
    except Exception as e:return {"connected":False,"error":str(e)}

async def cloud_post(path,payload=None,timeout=35):
    async with httpx.AsyncClient(timeout=timeout) as c:
        r=await c.post(_url()+path,json=payload or {});r.raise_for_status();return r.json()
