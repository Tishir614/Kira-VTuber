from dataclasses import dataclass, asdict
from time import time

@dataclass
class Live2DState:
    emotion: str = "neutral"
    mouth_open: float = 0.0
    speaking: bool = False
    listening: bool = False
    angle_x: float = 0.0
    angle_y: float = 0.0
    angle_z: float = 0.0
    eye_x: float = 0.0
    eye_y: float = 0.0
    body_angle_x: float = 0.0
    breath: float = 0.5
    updated_at: float = 0.0

class Live2DBridge:
    def __init__(self): self.state = Live2DState(updated_at=time())
    def set_emotion(self, emotion: str): self.state.emotion=emotion; self.state.updated_at=time()
    def set_speaking(self, value: bool): self.state.speaking=value; self.state.updated_at=time()
    def set_mouth(self, value: float): self.state.mouth_open=max(0.0,min(1.0,value)); self.state.updated_at=time()
    def snapshot(self): return asdict(self.state)

live2d = Live2DBridge()
