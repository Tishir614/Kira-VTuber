from pathlib import Path
from .config import settings

def voice_models():
    roots=[Path("models/piper"),Path.home()/".local/share/kira/voices"]
    out=[]
    for root in roots:
        if root.exists():
            for p in root.rglob("*.onnx"):
                out.append({"name":p.stem,"path":str(p.resolve())})
    active=settings.piper_model
    return {"voices":out,"active":active}
