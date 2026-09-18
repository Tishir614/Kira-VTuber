import json
from pathlib import Path
from threading import Lock

DEFAULTS = {
    "wake_word": "кира",
    "voice_enabled": True,
    "handsfree_enabled": False,
    "volume": 1.0,
    "personality": {"warmth": 0.8, "humor": 0.7, "energy": 0.75, "verbosity": 0.55}
}

class SettingsStore:
    def __init__(self, path="runtime/settings.json"):
        self.path=Path(path); self.lock=Lock(); self.path.parent.mkdir(parents=True,exist_ok=True)
    def load(self):
        data=DEFAULTS.copy()
        if self.path.exists():
            try: data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except (OSError,json.JSONDecodeError): pass
        return data
    def save(self, patch: dict):
        with self.lock:
            data=self.load(); data.update(patch)
            self.path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
            return data
settings_store=SettingsStore()
