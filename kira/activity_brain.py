"""Autonomous day planner for Kira's bounded subsystems."""
from __future__ import annotations
import random,time
from dataclasses import dataclass,asdict
from .settings_store import settings_store
from .cloud_client import cloud_post,cloud_status
from .pipeline import respond
from .research_brain import research

@dataclass
class ActivityState:
    last_activity:str="idle"
    last_at:float=0
    completed:int=0
    last_error:str=""

state=ActivityState()

async def tick():
    s=settings_store.load()
    choices=["reflect","browse","learn"]
    games=[x.strip() for x in str(s.get("autonomous_games","")).split(",") if x.strip()]
    if games:choices.append("game")
    activity=random.choice(choices)
    try:
        if activity=="learn":
            topics=[x.strip() for x in str(s.get("learning_topics","resident evil")).split(",") if x.strip()]
            topic=random.choice(topics or ["resident evil"])
            await research(topic,"",limit=2)
        elif activity=="browse":
            topics=["новости технологий","новые инди-игры","интересные факты о космосе","цифровое искусство"]
            await cloud_post("/browser/search",{"query":random.choice(topics)})
        elif activity=="game":
            # Only launches games explicitly configured by the owner and allow-listed by Cloud Agent.
            await cloud_post("/games/launch",{"game":random.choice(games)})
        else:
            await respond("Сделай короткую внутреннюю заметку о том, какую тему тебе было бы интересно обсудить со зрителями позже. Не утверждай, что ты что-то сделала во внешнем мире.",False)
        state.last_activity=activity;state.last_at=time.time();state.completed+=1;state.last_error=""
    except Exception as exc:state.last_error=str(exc)[:400]
    return asdict(state)

def snapshot():return asdict(state)
