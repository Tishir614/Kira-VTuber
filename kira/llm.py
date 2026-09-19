import httpx
from .config import settings
from .personality import personality
from .persistent_memory import persistent_memory
from .character_runtime import ai_context, load as character_profile

async def chat(message: str, history: list[dict] | None = None) -> str:
    saved = persistent_memory.load()
    facts = saved.get("facts", [])[-20:]
    memory_context = ""
    if facts:
        memory_context = "\n\nИзвестные факты из долговременной памяти:\n- " + "\n- ".join(facts)
    messages = [{"role": "system", "content": personality.system_prompt() + "\n\n" + ai_context() + memory_context}]
    messages.extend((history or [])[-20:])
    messages.append({"role": "user", "content": message})
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": character_profile().get("ai",{}).get("temperature",settings.temperature)},
    }
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(f"{settings.llm_base_url}/api/chat", json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]
