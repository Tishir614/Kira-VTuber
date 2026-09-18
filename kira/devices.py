import json
import shutil
import subprocess

def _run(args):
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL, timeout=4)
    except Exception:
        return ""

def audio_devices():
    result={"pipewire":bool(shutil.which("wpctl")),"inputs":[],"outputs":[]}
    if shutil.which("wpctl"):
        raw=_run(["wpctl","status","-n"])
        section=None
        for line in raw.splitlines():
            s=line.strip()
            if "Sources:" in s: section="inputs"; continue
            if "Sinks:" in s: section="outputs"; continue
            if section and s and any(ch.isdigit() for ch in s):
                clean=s.replace("│","").replace("├","").replace("└","").replace("─","").strip()
                if clean: result[section].append(clean)
    return result

def default_audio():
    if not shutil.which("wpctl"): return {"input":"","output":""}
    return {
        "input":_run(["wpctl","get-volume","@DEFAULT_AUDIO_SOURCE@"]).strip(),
        "output":_run(["wpctl","get-volume","@DEFAULT_AUDIO_SINK@"]).strip()
    }
