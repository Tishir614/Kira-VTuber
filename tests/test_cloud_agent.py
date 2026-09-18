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


def test_per_game_profile_tracks_progression():
    profile=Path("kira/game_profile.py").read_text()
    vision=Path("kira/vision.py").read_text()
    game=Path("kira/game_brain.py").read_text()
    for word in ("deaths","quests","inventory","places"): assert word in profile
    assert "death_detected" in vision
    assert "profile_death" in game and "update_world" in game


def test_master_autonomy_is_explicit_on_off():
    core=Path("kira/autonomy.py").read_text()
    studio=Path("web/studio.html").read_text()
    assert "master_autonomy_enabled" in core
    assert "/autonomy/start" in studio and "/autonomy/stop" in studio
    assert "autopilot.start()" in core and "watchdog.start()" in core


def test_autonomous_activity_stays_bounded():
    activity=Path("kira/activity_brain.py").read_text()
    assert "subprocess" not in activity
    assert 'cloud_post("/games/launch"' in activity
    assert "autonomous_games" in activity


def test_learning_memory_is_source_tagged_and_used_by_game_brain():
    learn=Path("kira/learning_memory.py").read_text()
    game=Path("kira/game_brain.py").read_text()
    media=Path("kira/media_learner.py").read_text()
    assert "source_url" in learn and "confidence" in learn
    assert "learned_guides" in game
    assert "study_url" in media
    assert "download" not in media.lower()


def test_research_brain_treats_web_as_untrusted():
    research=Path("kira/research_brain.py").read_text()
    assert "untrusted" in research
    assert "ads, downloads, login pages, purchases" in research
    assert "study_url" in research

def test_learning_can_be_verified_in_game():
    learn=Path("kira/learning_memory.py").read_text()
    assert "verified_in_game" in learn and "successes" in learn and "failures" in learn


def test_kira_researches_when_stuck_with_cooldown():
    adaptive=Path("kira/adaptive_learning.py").read_text()
    game=Path("kira/game_brain.py").read_text()
    assert "stagnant>=3" in adaptive
    assert "cooldown_seconds:int=600" in adaptive
    assert "learn_when_stuck" in game
    assert "research(game,mission,limit=2)" in adaptive


def test_experience_engine_reinforces_real_outcomes():
    exp=Path("kira/experience_engine.py").read_text()
    game=Path("kira/game_brain.py").read_text()
    assert 'return "death"' in exp and 'return "progress"' in exp
    assert "record_experience" in game
    assert "learning_feedback" in game
    assert "experience_summary" in game
