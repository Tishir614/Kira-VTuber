from dataclasses import dataclass

@dataclass
class VADConfig:
    enabled: bool = False
    threshold: float = 0.018
    silence_seconds: float = 0.8
    max_utterance_seconds: float = 20.0

vad_config = VADConfig()
