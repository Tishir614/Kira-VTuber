import os, platform, shutil, subprocess

def _cmd(args):
    try: return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL, timeout=3).strip()
    except Exception: return ""

def hardware_info():
    ram_gb = 0.0
    try:
        pages=os.sysconf("SC_PHYS_PAGES"); size=os.sysconf("SC_PAGE_SIZE")
        ram_gb=round(pages*size/1024**3,1)
    except Exception: pass
    gpu=_cmd(["sh","-lc","lspci | grep -Ei 'VGA|3D|Display'"]) or "unknown"
    cpu=platform.processor() or _cmd(["sh","-lc","lscpu | sed -n 's/^Model name:[[:space:]]*//p' | head -1"]) or "unknown"
    return {"os":platform.platform(),"cpu":cpu,"ram_gb":ram_gb,"gpu":gpu,"ollama":bool(shutil.which("ollama"))}

def recommended_model(ram_gb: float) -> str:
    if ram_gb >= 32: return "qwen3:14b"
    if ram_gb >= 16: return "qwen3:8b"
    return "qwen3:4b"
