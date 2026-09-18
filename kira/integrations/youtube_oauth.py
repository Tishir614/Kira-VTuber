import asyncio, json, secrets
from pathlib import Path
from time import time
from urllib.parse import urlencode
import httpx

AUTH="https://accounts.google.com/o/oauth2/v2/auth"
TOKEN="https://oauth2.googleapis.com/token"
SCOPE="https://www.googleapis.com/auth/youtube"
TOKEN_PATH=Path("runtime/youtube_oauth.json")

class YouTubeOAuth:
    def __init__(self): self.pending_state=""
    def authorize_url(self,client_id,redirect_uri):
        self.pending_state=secrets.token_urlsafe(24)
        return AUTH+"?"+urlencode({"client_id":client_id,"redirect_uri":redirect_uri,"response_type":"code","scope":SCOPE,"access_type":"offline","prompt":"consent","state":self.pending_state})
    def _save(self,t):
        TOKEN_PATH.parent.mkdir(parents=True,exist_ok=True); t["saved_at"]=int(time())
        TOKEN_PATH.write_text(json.dumps(t,indent=2),encoding="utf-8")
    def load(self):
        try:return json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
        except Exception:return None
    async def exchange(self,cid,secret,redirect,code,state):
        if not self.pending_state or not secrets.compare_digest(state,self.pending_state): raise RuntimeError("Invalid OAuth state")
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.post(TOKEN,data={"client_id":cid,"client_secret":secret,"code":code,"grant_type":"authorization_code","redirect_uri":redirect});r.raise_for_status();t=r.json()
        self.pending_state="";self._save(t);return t
    async def refresh(self,cid,secret):
        old=self.load()
        if not old or not old.get("refresh_token"): raise RuntimeError("No YouTube refresh token")
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.post(TOKEN,data={"client_id":cid,"client_secret":secret,"refresh_token":old["refresh_token"],"grant_type":"refresh_token"});r.raise_for_status();t=r.json()
        t["refresh_token"]=old["refresh_token"];self._save(t);return t
    async def access_token(self,cid,secret):
        t=self.load()
        if not t:return None
        if time()<t.get("saved_at",0)+t.get("expires_in",3600)-120:return t.get("access_token")
        return (await self.refresh(cid,secret)).get("access_token")
    async def active_broadcast(self,token):
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.get("https://www.googleapis.com/youtube/v3/liveBroadcasts",params={"part":"id,snippet,status","broadcastStatus":"active","mine":"true","maxResults":5},headers={"Authorization":f"Bearer {token}"});r.raise_for_status();d=r.json()
        items=d.get("items",[])
        if not items:return None
        b=items[0];return {"broadcast_id":b.get("id"),"title":b.get("snippet",{}).get("title"),"live_chat_id":b.get("snippet",{}).get("liveChatId")}
    async def create_broadcast(self,token,title,start_iso,privacy="unlisted",description=""):
        body={"snippet":{"title":title[:100],"description":description[:5000],"scheduledStartTime":start_iso},"status":{"privacyStatus":privacy,"selfDeclaredMadeForKids":False},"contentDetails":{"enableAutoStart":False,"enableAutoStop":False,"enableDvr":True,"recordFromStart":True,"monitorStream":{"enableMonitorStream":False}}}
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.post("https://www.googleapis.com/youtube/v3/liveBroadcasts",params={"part":"snippet,status,contentDetails"},headers={"Authorization":f"Bearer {token}"},json=body);r.raise_for_status();return r.json()
    async def streams(self,token):
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.get("https://www.googleapis.com/youtube/v3/liveStreams",params={"part":"id,snippet,cdn,status","mine":"true","maxResults":50},headers={"Authorization":f"Bearer {token}"});r.raise_for_status();return r.json().get("items",[])
    async def bind(self,token,broadcast_id,stream_id):
        async with httpx.AsyncClient(timeout=20) as c:
            r=await c.post("https://www.googleapis.com/youtube/v3/liveBroadcasts/bind",params={"id":broadcast_id,"streamId":stream_id,"part":"id,snippet,contentDetails,status"},headers={"Authorization":f"Bearer {token}"});r.raise_for_status();return r.json()
    async def transition(self,token,broadcast_id,status):
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.post("https://www.googleapis.com/youtube/v3/liveBroadcasts/transition",params={"broadcastStatus":status,"id":broadcast_id,"part":"id,snippet,status"},headers={"Authorization":f"Bearer {token}"});r.raise_for_status();return r.json()
    async def stream_status(self,token,stream_id):
        async with httpx.AsyncClient(timeout=15) as c:
            r=await c.get("https://www.googleapis.com/youtube/v3/liveStreams",params={"part":"status","id":stream_id},headers={"Authorization":f"Bearer {token}"});r.raise_for_status();items=r.json().get("items",[]);return items[0].get("status",{}).get("streamStatus") if items else None
    def disconnect(self):
        if TOKEN_PATH.exists():TOKEN_PATH.unlink()
youtube_oauth=YouTubeOAuth()
