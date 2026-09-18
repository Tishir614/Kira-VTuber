import json, httpx
from .base import ChatAdapter
from ..chat_events import chat_queue

EVENTSUB_WS="wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=30"

class TwitchAdapter(ChatAdapter):
    platform="twitch"
    def __init__(self,client_id,access_token,broadcaster_user_id,bot_user_id):
        self.client_id=client_id; self.token=access_token; self.broadcaster=broadcaster_user_id; self.bot=bot_user_id; self.running=True
    async def _subscribe(self,session_id):
        body={"type":"channel.chat.message","version":"1","condition":{"broadcaster_user_id":self.broadcaster,"user_id":self.bot},"transport":{"method":"websocket","session_id":session_id}}
        async with httpx.AsyncClient(timeout=15) as c:
            r=await c.post("https://api.twitch.tv/helix/eventsub/subscriptions",json=body,headers={"Client-Id":self.client_id,"Authorization":f"Bearer {self.token}","Content-Type":"application/json"})
            r.raise_for_status()
    async def run(self):
        import websockets
        url=EVENTSUB_WS; need_subscribe=True
        while self.running:
            async with websockets.connect(url) as ws:
                async for raw in ws:
                    msg=json.loads(raw); meta=msg.get("metadata",{}); payload=msg.get("payload",{}); typ=meta.get("message_type")
                    if typ=="session_welcome":
                        if need_subscribe:
                            await self._subscribe(payload["session"]["id"]); need_subscribe=False
                    elif typ=="notification":
                        ev=payload.get("event",{}); text=ev.get("message",{}).get("text","")
                        if text: chat_queue.push("twitch",ev.get("chatter_user_name","viewer"),text)
                    elif typ=="session_reconnect":
                        url=payload["session"]["reconnect_url"]; break
                    elif typ=="revocation": raise RuntimeError("Twitch EventSub subscription revoked")
    async def stop(self): self.running=False
