from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import httpx, uvicorn
from .config import settings
from .llm import chat
from .emotion import state, detect_emotion

app = FastAPI(title="Kira VTuber Core", version="0.1.0")

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = Field(default_factory=list)

@app.get("/health")
async def health():
    ollama = False
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            ollama = (await client.get(f"{settings.llm_base_url}/api/tags")).is_success
    except Exception: pass
    return {"ok": True, "ollama": ollama, "model": settings.llm_model}

@app.get("/avatar/state")
async def avatar_state(): return state.__dict__

@app.post("/chat")
async def kira_chat(req: ChatRequest):
    if not req.message.strip(): raise HTTPException(400, "message is empty")
    try: answer = await chat(req.message, req.history)
    except httpx.HTTPError as exc: raise HTTPException(503, f"Local LLM unavailable: {exc}") from exc
    state.emotion = detect_emotion(answer)
    return {"answer": answer, "emotion": state.emotion}

if __name__ == "__main__":
    uvicorn.run("kira.main:app", host=settings.host, port=settings.port)
