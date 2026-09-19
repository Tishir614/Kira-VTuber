"""Automatic per-service network routing with direct/proxy failover."""
from __future__ import annotations
import asyncio,time
from dataclasses import dataclass,field,asdict
import httpx
from .proxy import proxy_for,client as proxy_client
CHECKS={"telegram":"https://api.telegram.org","twitch":"https://www.twitch.tv","youtube":"https://www.youtube.com"}
@dataclass
class Route:
    mode:str="direct";failures:int=0;successes:int=0;last_check:float=0;last_error:str=""
@dataclass
class NetworkState:
    running:bool=False;routes:dict[str,Route]=field(default_factory=lambda:{k:Route() for k in CHECKS})
class NetworkBrain:
    def __init__(self):self.state=NetworkState();self.task=None
    def snapshot(self):return {"running":self.state.running,"routes":{k:asdict(v) for k,v in self.state.routes.items()}}
    async def check(self,service:str):
        route=self.state.routes[service];url=CHECKS[service]
        async def ping(proxy=False):
            if proxy:
                async with proxy_client(service,8,follow_redirects=True) as c:r=await c.get(url)
            else:
                async with httpx.AsyncClient(timeout=8,follow_redirects=True) as c:r=await c.get(url)
            return r.status_code<500
        try:
            direct=await ping(False)
            if direct:route.mode="direct";route.successes+=1;route.failures=0;route.last_error=""
            elif proxy_for(service) and await ping(True):route.mode="proxy";route.successes+=1;route.failures=0
            else:route.failures+=1;route.last_error="direct and proxy unavailable"
        except Exception as exc:
            if proxy_for(service):
                try:
                    if await ping(True):route.mode="proxy";route.successes+=1;route.failures=0;route.last_error=""
                    else:route.failures+=1
                except Exception as pexc:route.failures+=1;route.last_error=str(pexc)[:180]
            else:route.failures+=1;route.last_error=str(exc)[:180]
        route.last_check=time.time();return asdict(route)
    async def check_all(self):
        for s in CHECKS:await self.check(s)
        return self.snapshot()
    def start(self):
        if self.task and not self.task.done():return
        self.state.running=True;self.task=asyncio.create_task(self._loop())
    def stop(self):
        self.state.running=False
        if self.task and not self.task.done():self.task.cancel()
    async def _loop(self):
        while self.state.running:
            try:await self.check_all()
            except asyncio.CancelledError:raise
            except Exception:pass
            await asyncio.sleep(60)
network_brain=NetworkBrain()
