import os
os.environ.setdefault("KIRA_HOST","127.0.0.1")
from fastapi.testclient import TestClient
from kira.main import app

def test_core_pages_and_status_endpoints():
    with TestClient(app) as client:
        for path in ("/studio","/health","/settings","/diagnostics","/watchdog","/show","/schedule","/autopilot","/integrations","/memory","/avatar/state","/live2d/status"):
            r=client.get(path)
            assert r.status_code==200, f"{path}: {r.status_code} {r.text[:300]}"

def test_studio_has_no_missing_core_routes():
    with TestClient(app) as client:
        html=client.get("/studio").text
        assert "Kira Studio" in html
        assert "Проверить всё" in html
