import shutil
import subprocess
import tempfile
from pathlib import Path

def record(seconds: int = 6) -> Path:
    out = Path(tempfile.gettempdir()) / "kira_mic.wav"
    if shutil.which("pw-record"):
        cmd = ["pw-record", "--rate", "16000", "--channels", "1", str(out)]
    elif shutil.which("arecord"):
        cmd = ["arecord", "-q", "-f", "S16_LE", "-r", "16000", "-c", "1", str(out)]
    else:
        raise RuntimeError("Install PipeWire (pw-record) or ALSA (arecord)")
    try:
        subprocess.run(cmd, timeout=seconds, check=False)
    except subprocess.TimeoutExpired:
        pass
    if not out.exists():
        raise RuntimeError("Microphone recording failed")
    return out
