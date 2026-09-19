import httpx
from .proxy import routed_client as proxy_client
from .settings_store import settings_store

async def telegram_status():
    s=settings_store.load(); token=s.get("telegram_bot_token","")
    if not token: return {"connected":False}
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r=await c.get(f"https://api.telegram.org/bot{token}/getMe"); r.raise_for_status(); d=r.json()
        u=d.get("result",{})
        return {"connected":bool(d.get("ok")),"username":u.get("username")}
    except Exception as e: return {"connected":False,"error":str(e)[:200]}

async def telegram_post(text:str):
    s=settings_store.load(); token=s.get("telegram_bot_token",""); chat=s.get("telegram_channel","")
    if not token or not chat: raise RuntimeError("Telegram bot/channel not configured")
    async with proxy_client("telegram",timeout=20) as c:
        r=await c.post(f"https://api.telegram.org/bot{token}/sendMessage",json={"chat_id":chat,"text":text[:4096]}); r.raise_for_status(); return r.json()
