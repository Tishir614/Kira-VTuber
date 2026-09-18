import json
from pathlib import Path
from threading import Lock

class PersistentMemory:
    def __init__(self, path: str = "runtime/memory.json"):
        self.path = Path(path)
        self.lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = {"facts": [], "summary": ""}

    def load(self):
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return self.data

    def remember(self, fact: str):
        fact = fact.strip()
        if not fact:
            return
        with self.lock:
            self.load()
            if fact not in self.data["facts"]:
                self.data["facts"].append(fact)
                self.data["facts"] = self.data["facts"][-100:]
                self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def forget_all(self):
        with self.lock:
            self.data = {"facts": [], "summary": ""}
            self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

persistent_memory = PersistentMemory()
