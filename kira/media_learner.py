"""Study public web/video content through Kira Cloud by observing it in place."""
from __future__ import annotations
import asyncio
from .cloud_client import cloud_post
from .vision import analyze_game
from .learning_memory import learn

async def study_url(game:str,url:str,title:str="",samples:int=6,interval:float=5.0):
    await cloud_post("/browser/open",{"url":url})
    notes=[]
    for _ in range(max(1,min(samples,20))):
        try:
            v=await analyze_game(f"Study this public media/page for useful {game} gameplay knowledge.")
            notes.append(str(v))
        except Exception as exc:notes.append("observation error: "+str(exc))
        await asyncio.sleep(max(2,min(interval,30)))
    lessons=await learn(game,title or url,url,"\n".join(notes))
    return {"ok":True,"observations":len(notes),"lessons":lessons}
