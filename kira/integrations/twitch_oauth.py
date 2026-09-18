import json, secrets, asyncio
from pathlib import Path
from urllib.parse import urlencode
from time import time
import httpx

AUTH="https://id.twitch.tv/oauth2/authorize"
TOKEN="https://id.twitch.tv/oauth2/token"
VALIDATE="https://id.twitch.tv/oauth2/validate"
SCOPES="user:read:chat"
TOKEN_PATH=Path("runtime/twitch_oauth.json")

class TwitchOAuth:
    def __init__(self): self.pending_state=""; self._validator=None
    def authorize_url(self,client_id,redirect_uri):
        self.pending_state=secrets.token_urlsafe(24)
        return AUTH+"?"+urlencode({"response_type":"code","client_id":client_id,"redirect_uri":redirect_uri,"scope":SCOPES,"state":self.pending_state})
    def _save(self,token):
        TOKEN_PATH.parent.mkdir(parents=True,exist_ok=True)
        token["saved_at"]=int(time())
        TOKEN_PATH.write_text(json.dumps(token,indent=2),encoding="utf-8")
    async def exchange(self,client_id,client_secret,redirect_uri,code,state):
        if not self.pending_state or not secrets.compare_digest(state,self.pending_state): raise RuntimeError("Invalid OAuth state")
        data={"client_id":client_id,"client_secret":client_secret,"code":code,"grant_type":"authorization_code","redirect_uri":redirect_uri}
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.post(TOKEN,data=data); r.raise_for_status(); token=r.json()
        self.pending_state=""; self._save(token); return token
    async def refresh(self,client_id,client_secret):
        current=self.load()
        if not current or not current.get("refresh_token"): raise RuntimeError("No Twitch refresh token")
        data={"grant_type":"refresh_token","refresh_token":current["refresh_token"],"client_id":client_id,"client_secret":client_secret}
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.post(TOKEN,data=data); r.raise_for_status(); fresh=r.json()
        if not fresh.get("refresh_token"): fresh["refresh_token"]=current["refresh_token"]
        self._save(fresh); return fresh
    async def validate(self,access_token):
        if not access_token: return None
        async with httpx.AsyncClient(timeout=10) as c:
            r=await c.get(VALIDATE,headers={"Authorization":f"OAuth {access_token}"})
            if r.status_code==401: return None
            r.raise_for_status(); return r.json()
    async def ensure_valid(self,client_id,client_secret):
        token=self.load()
        if not token: return None
        info=await self.validate(token.get("access_token",""))
        if info: return token,info
        token=await self.refresh(client_id,client_secret)
        info=await self.validate(token.get("access_token",""))
        return (token,info) if info else None
    def start_hourly_validation(self,client_id,client_secret):
        if self._validator and not self._validator.done(): return
        async def loop():
            while True:
                try: await self.ensure_valid(client_id,client_secret)
                except Exception: pass
                await asyncio.sleep(3600)
        self._validator=asyncio.create_task(loop())
    def load(self):
        try: return json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
        except Exception: return None
    def disconnect(self):
        if self._validator and not self._validator.done(): self._validator.cancel()
        if TOKEN_PATH.exists(): TOKEN_PATH.unlink()

twitch_oauth=TwitchOAuth()
