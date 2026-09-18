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


def test_game_vision_is_structured_and_low_temperature():
    vision=Path("kira/vision.py").read_text()
    assert '"format":"json"' in vision
    assert '"temperature":0.15' in vision
    assert "confidence" in vision and "interactables" in vision

def test_game_learning_and_stagnation_detection():
    game=Path("kira/game_brain.py").read_text()
    memory=Path("kira/game_memory.py").read_text()
    assert "stagnant>=3" in game
    assert "recall(game_id)" in game
    assert "runtime/game_memory.json" in memory


def test_game_reflex_is_bounded_and_llm_free():
    reflex=Path("kira/game_reflex.py").read_text()
    assert "from .llm" not in reflex
    assert 'hold_ms":90' in reflex
    assert "confidence<.35" in reflex

def test_game_brain_combines_reflex_and_strategy():
    game=Path("kira/game_brain.py").read_text()
    assert "reflex_choose" in game
    assert "await decide(goal,v,mem,recent)" in game
