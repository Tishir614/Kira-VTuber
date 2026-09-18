import asyncio, shutil
from .hardware import hardware_info, recommended_model

async def setup_status():
    hw=hardware_info()
    return {"hardware":hw,"recommended_model":recommended_model(hw["ram_gb"]),
            "tools":{"ollama":bool(shutil.which("ollama")),"piper":bool(shutil.which("piper")),
                     "pw_record":bool(shutil.which("pw-record")),"pw_play":bool(shutil.which("pw-play"))}}

async def pull_ollama_model(model: str):
    if not shutil.which("ollama"): raise RuntimeError("Ollama executable not found")
    proc=await asyncio.create_subprocess_exec("ollama","pull",model,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT)
    out,_=await proc.communicate()
    if proc.returncode: raise RuntimeError(out.decode(errors="replace")[-2000:])
    return {"ok":True,"model":model}
