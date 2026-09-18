"""Kira Cloud Agent: isolated browser/game workspace controller."""
from __future__ import annotations
import os, subprocess
from pathlib import Path
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

app=FastAPI(title="Kira Cloud Agent",version="0.1.0")
TOKEN=os.environ.get("KIRA_CLOUD_TOKEN","")
HOME=Path.home()
ALLOWLIST={x.strip() for x in os.environ.get("KIRA_GAME_ALLOWLIST","").split(",") if x.strip()}
_browser=None
_page=None

class UrlRequest(BaseModel): url: HttpUrl
class SearchRequest(BaseModel): query: str
class GameRequest(BaseModel): game: str
class ClickRequest(BaseModel):
    x: float
    y: float
    button: str = "left"
class TypeRequest(BaseModel):
    text: str
class KeyRequest(BaseModel):
    key: str
class ScrollRequest(BaseModel):
    dx: float = 0
    dy: float = 500

async def page():
    global _browser,_page
    if _page:return _page
    from playwright.async_api import async_playwright
    pw=await async_playwright().start()
    _browser=await pw.chromium.launch(headless=False)
    _page=await _browser.new_page(viewport={"width":1280,"height":720})
    return _page

@app.get("/health")
async def health(): return {"ok":True,"workspace":str(HOME),"games":sorted(ALLOWLIST)}

@app.get("/state")
async def state():
    p=await page()
    return {"url":p.url,"title":await p.title()}

@app.post("/browser/open")
async def browser_open(req:UrlRequest):
    p=await page(); await p.goto(str(req.url),wait_until="domcontentloaded",timeout=30000)
    return {"ok":True,"url":p.url,"title":await p.title()}

@app.post("/browser/search")
async def browser_search(req:SearchRequest):
    q=req.query.strip()
    if not q:raise HTTPException(400,"empty query")
    from urllib.parse import quote_plus
    p=await page(); await p.goto("https://www.google.com/search?q="+quote_plus(q),wait_until="domcontentloaded")
    return {"ok":True,"url":p.url,"title":await p.title()}

@app.post("/browser/screenshot")
async def screenshot():
    p=await page(); out=HOME/"kira-screen.png"; await p.screenshot(path=str(out),full_page=False)
    return {"ok":True,"path":str(out)}

@app.post("/games/launch")
async def launch(req:GameRequest):
    game=req.game.strip()
    if game not in ALLOWLIST:raise HTTPException(403,"game is not allow-listed")
    try: subprocess.Popen([game],cwd=str(HOME),start_new_session=True)
    except FileNotFoundError:raise HTTPException(404,"game executable not found")
    return {"ok":True,"game":game}

@app.get("/games")
async def games(): return {"games":sorted(ALLOWLIST)}


@app.get("/screen")
async def screen():
    p=await page()
    data=await p.screenshot(type="png",full_page=False)
    import base64
    return {"ok":True,"width":1280,"height":720,"png_base64":base64.b64encode(data).decode()}

@app.post("/input/click")
async def input_click(req:ClickRequest):
    if req.button not in {"left","right","middle"}:raise HTTPException(400,"invalid button")
    p=await page();await p.mouse.click(req.x,req.y,button=req.button)
    return {"ok":True}

@app.post("/input/type")
async def input_type(req:TypeRequest):
    if len(req.text)>4000:raise HTTPException(400,"text too long")
    p=await page();await p.keyboard.type(req.text,delay=12)
    return {"ok":True}

@app.post("/input/key")
async def input_key(req:KeyRequest):
    allowed={"Enter","Escape","Tab","ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Space","Backspace","Delete","Home","End","PageUp","PageDown"}
    if req.key not in allowed:raise HTTPException(403,"key is not allow-listed")
    p=await page();await p.keyboard.press(req.key)
    return {"ok":True}

@app.post("/input/scroll")
async def input_scroll(req:ScrollRequest):
    p=await page();await p.mouse.wheel(req.dx,req.dy)
    return {"ok":True}

@app.get("/browser/a11y")
async def browser_a11y():
    p=await page()
    # Compact semantic view for planning without OCR.
    items=await p.locator("a,button,input,textarea,select,[role=button]").evaluate_all("""els => els.slice(0,120).map((e,i)=>({i,tag:e.tagName.toLowerCase(),text:(e.innerText||e.value||e.getAttribute('aria-label')||'').slice(0,180),disabled:!!e.disabled}))""")
    return {"url":p.url,"title":await p.title(),"elements":items}
