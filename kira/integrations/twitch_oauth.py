import json, secrets
from pathlib import Path
from urllib.parse import urlencode
import httpx

AUTH="https://id.twitch.tv/oauth2/authorize"
TOKEN="https://id.twitch.tv/oauth2/token"
VALIDATE="https://id.twitch.tv/oauth2/validate"
SCOPES="user:read:chat"
TOKEN_PATH=Path("runtime/twitch_oauth.json")

class TwitchOAuth:
    def __init__(self): self.pending_state=""
    def authorize_url(self,client_id,redirect_uri):
        self.pending_state=secrets.token_urlsafe(24)
        return AUTH+"?"+urlencode({"response_type":"code","client_id":client_id,"redirect_uri":redirect_uri,"scope":SCOPES,"state":self.pending_state})
    async def exchange(self,client_id,client_secret,redirect_uri,code,state):
        if not self.pending_state or not secrets.compare_digest(state,self.pending_state):
            raise RuntimeError("Invalid OAuth state")
        data={"client_id":client_id,"client_secret":client_secret,"code":code,"grant_type":"authorization_code","redirect_uri":redirect_uri}
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.post(TOKEN,data=data); r.raise_for_status(); token=r.json()
        self.pending_state=""
        TOKEN_PATH.parent.mkdir(parents=True,exist_ok=True)
        TOKEN_PATH.write_text(json.dumps(token,indent=2),encoding="utf-8")
        return token
    async def validate(self,access_token):
        async with httpx.AsyncClient(timeout=10) as c:
            r=await c.get(VALIDATE,headers={"Authorization":f"OAuth {access_token}"})
            if r.status_code==401: return None
            r.raise_for_status(); return r.json()
    def load(self):
        try: return json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
        except Exception: return None
    def disconnect(self):
        if TOKEN_PATH.exists(): TOKEN_PATH.unlink()

twitch_oauth=TwitchOAuth()
