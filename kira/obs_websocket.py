import asyncio, base64, hashlib, json, uuid
import websockets
from .settings_store import settings_store

class OBSWebSocket:
    def __init__(self): self.ws=None; self.lock=asyncio.Lock()
    async def connect(self):
        s=settings_store.load(); url=s.get("obs_ws_url","ws://127.0.0.1:4455"); password=s.get("obs_ws_password","")
        self.ws=await websockets.connect(url)
        hello=json.loads(await self.ws.recv()); auth=hello.get("d",{}).get("authentication")
        identify={"rpcVersion":1}
        if auth:
            secret=base64.b64encode(hashlib.sha256((password+auth["salt"]).encode()).digest()).decode()
            identify["authentication"]=base64.b64encode(hashlib.sha256((secret+auth["challenge"]).encode()).digest()).decode()
        await self.ws.send(json.dumps({"op":1,"d":identify}))
        msg=json.loads(await self.ws.recv())
        if msg.get("op")!=2: raise RuntimeError("OBS WebSocket authentication failed")
    async def close(self):
        if self.ws: await self.ws.close(); self.ws=None
    async def request(self,kind,data=None):
        async with self.lock:
            if not self.ws: await self.connect()
            rid=str(uuid.uuid4()); await self.ws.send(json.dumps({"op":6,"d":{"requestType":kind,"requestId":rid,"requestData":data or {}}}))
            while True:
                m=json.loads(await self.ws.recv())
                if m.get("op")==7 and m.get("d",{}).get("requestId")==rid:
                    st=m["d"]["requestStatus"]
                    if not st.get("result"): raise RuntimeError(st.get("comment") or f"OBS request failed: {st.get('code')}")
                    return m["d"].get("responseData",{})
    async def stream_status(self): return await self.request("GetStreamStatus")
    async def start_stream(self): return await self.request("StartStream")
    async def stop_stream(self): return await self.request("StopStream")
    async def set_scene(self,name): return await self.request("SetCurrentProgramScene",{"sceneName":name})
obs_ws=OBSWebSocket()
