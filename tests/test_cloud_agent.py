from pathlib import Path

def test_cloud_agent_has_safe_capabilities():
    text=Path("cloud/agent/main.py").read_text()
    for route in ("/screen","/input/click","/input/type","/input/key","/input/scroll","/browser/a11y"):
        assert route in text
    assert "shell=True" not in text

def test_cloud_brain_has_step_limit_and_allowlist():
    text=Path("kira/cloud_brain.py").read_text()
    assert "ALLOWED=" in text
    assert "min(max_steps,20)" in text


def test_game_brain_uses_real_vision_adapter():
    game=Path("kira/game_brain.py").read_text()
    vision=Path("kira/vision.py").read_text()
    assert "describe_game" in game
    assert '"/api/chat"' in vision
    assert '"images"' in vision
