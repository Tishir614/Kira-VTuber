import json
from pathlib import Path

class OBSConfig:
    def __init__(self,path="runtime/obs.json"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def load(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception: return {"overlay_url":"http://127.0.0.1:8765/overlay","width":1920,"height":1080,"subtitles":True}
    def save(self,data):
        current=self.load(); current.update(data)
        self.path.write_text(json.dumps(current,ensure_ascii=False,indent=2),encoding="utf-8"); return current
obs_config=OBSConfig()
