import httpx
from .config import settings

async def ollama_models():
    async with httpx.AsyncClient(timeout=5) as client:
        r=await client.get(f"{settings.llm_base_url}/api/tags"); r.raise_for_status()
        return [m.get("name","") for m in r.json().get("models",[])]

async def model_exists(name: str):
    return name in await ollama_models()
