import asyncio, httpx
from .base import ChatAdapter
from ..chat_events import chat_queue

class YouTubeAdapter(ChatAdapter):
    platform="youtube"
    def __init__(self,live_chat_id,access_token="",api_key=""):
        self.access_token=access_token;self.api_key=api_key;self.live_chat_id=live_chat_id;self.running=True;self.page=None
    async def run(self):
        async with httpx.AsyncClient(timeout=20) as c:
            while self.running:
                params={"part":"snippet,authorDetails","liveChatId":self.live_chat_id}
                headers={}
                if self.api_key:params["key"]=self.api_key
                if self.access_token:headers["Authorization"]=f"Bearer {self.access_token}"
                if self.page:params["pageToken"]=self.page
                r=await c.get("https://www.googleapis.com/youtube/v3/liveChat/messages",params=params,headers=headers);r.raise_for_status();d=r.json();self.page=d.get("nextPageToken")
                for item in d.get("items",[]):
                    sn=item.get("snippet",{});au=item.get("authorDetails",{});text=sn.get("displayMessage","")
                    if text:chat_queue.push("youtube",au.get("displayName","viewer"),text)
                await asyncio.sleep(max(1,d.get("pollingIntervalMillis",5000)/1000))
    async def stop(self):self.running=False
