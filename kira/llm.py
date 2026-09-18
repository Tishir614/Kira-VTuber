import httpx
from .config import settings

SYSTEM_PROMPT = """Ты Кира, локальная ИИ-втуберша. Отвечай живо, естественно и по контексту. Не утверждай, что выполнила действие, если оно реально не было выполнено."""

async def chat(message: str, history: list[dict] | None = None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend((history or [])[-20:])
    messages.append({"role": "user", "content": message})
    payload = {"model": settings.llm_model, "messages": messages, "stream": False, "options": {"temperature": settings.temperature}}
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(f"{settings.llm_base_url}/api/chat", json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]
