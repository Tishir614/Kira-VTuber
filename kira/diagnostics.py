import shutil
import httpx
from .config import settings

async def diagnostics():
    checks = {
        "python_core": True,
        "ollama_binary": bool(shutil.which("ollama")),
        "piper_binary": bool(shutil.which("piper")),
        "pipewire_playback": bool(shutil.which("pw-play") or shutil.which("aplay")),
        "microphone_recorder": bool(shutil.which("pw-record") or shutil.which("arecord")),
    }
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            checks["ollama_api"] = (await client.get(f"{settings.llm_base_url}/api/tags")).is_success
    except Exception:
        checks["ollama_api"] = False
    checks["ready_for_chat"] = checks["ollama_api"]
    checks["ready_for_voice"] = checks["piper_binary"] and checks["pipewire_playback"]
    checks["ready_for_mic"] = checks["microphone_recorder"]
    return checks
