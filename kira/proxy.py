"""Central outbound proxy configuration for Kira integrations."""
from __future__ import annotations
from urllib.parse import urlparse
import httpx
from .settings_store import settings_store

def config():
    s=settings_store.load();url=str(s.get("proxy_url","")).strip()
    enabled=bool(s.get("proxy_enabled",False) and url)
    services=s.get("proxy_services",["telegram","twitch","youtube","cloud"])
    if isinstance(services,str):services=[x.strip() for x in services.split(",") if x.strip()]
    return {"enabled":enabled,"url":url,"services":services}

def _valid(url:str)->bool:
    try:return urlparse(url).scheme in {"http","https","socks5","socks5h"} and bool(urlparse(url).hostname)
    except Exception:return False

def proxy_for(service:str)->str|None:
    c=config()
    if not c["enabled"] or service not in c["services"] or not _valid(c["url"]):return None
    return c["url"]

def client(service:str,timeout=20,force:bool=False,**kwargs):
    p=proxy_for(service) if not force else config().get("url")
    if p:kwargs["proxy"]=p
    return httpx.AsyncClient(timeout=timeout,**kwargs)

async def status():
    c=config();safe={**c,"url":""}
    if c["url"]:
        u=urlparse(c["url"]);safe["url"]=f"{u.scheme}://{u.hostname}:{u.port or ''}".rstrip(":")
    result={"configured":c["enabled"],"proxy":safe}
    if c["enabled"]:
        try:
            async with client("cloud",8) as h:
                r=await h.get("https://example.com");result["reachable"]=r.status_code<500
        except Exception as exc:result["reachable"]=False;result["error"]=str(exc)[:200]
    return result

def routed_client(service:str,timeout=20,**kwargs):
    try:
        from .network_brain import network_brain
        use_proxy=network_brain.state.routes.get(service) and network_brain.state.routes[service].mode=="proxy"
    except Exception:use_proxy=False
    return client(service,timeout,force=bool(use_proxy),**kwargs)
