import asyncio
import shutil
import subprocess
import time
import httpx
from .config import settings
from .settings_store import settings_store
from .watchdog import watchdog

async def _ollama_ok():
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            return (await c.get(f"{settings.llm_base_url}/api/tags")).is_success
    except Exception:
        return False

async def repair():
    """Conservative self-healing. Restarts safe local services and reports missing components.
    It never edits source code, installs arbitrary packages, or changes user credentials.
    """
    actions=[]; unresolved=[]
    if not await _ollama_ok():
        if shutil.which("ollama"):
            try:
                subprocess.Popen(["ollama","serve"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                for _ in range(12):
                    await asyncio.sleep(.5)
                    if await _ollama_ok():
                        actions.append("Ollama restarted"); break
                else: unresolved.append("Ollama API is still unavailable")
            except Exception as e: unresolved.append(f"Ollama restart failed: {e}")
        else: unresolved.append("Ollama is not installed")
    if not shutil.which("piper"): unresolved.append("Piper is not installed")
    if not (shutil.which("pw-play") or shutil.which("aplay")): unresolved.append("Audio playback tool is missing")
    if not (shutil.which("pw-record") or shutil.which("arecord")): unresolved.append("Microphone recorder is missing")
    if not watchdog.state.enabled:
        watchdog.start(); actions.append("Watchdog enabled")
    return {"ok":not unresolved,"actions":actions,"unresolved":unresolved,"checked_at":time.time()}
