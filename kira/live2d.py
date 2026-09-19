from dataclasses import dataclass, asdict
from time import time

def clamp(v,lo=-1.0,hi=1.0):
    try:return max(lo,min(hi,float(v)))
    except (TypeError,ValueError):return 0.0

@dataclass
class Live2DState:
    emotion: str = "neutral"
    mouth_open: float = 0.0
    mouth_form: float = 0.0
    speaking: bool = False
    listening: bool = False
    angle_x: float = 0.0
    angle_y: float = 0.0
    angle_z: float = 0.0
    eye_x: float = 0.0
    eye_y: float = 0.0
    eye_l: float = 1.0
    eye_r: float = 1.0
    brow_l: float = 0.0
    brow_r: float = 0.0
    body_angle_x: float = 0.0
    breath: float = 0.5
    ear_l: float = 0.0
    ear_r: float = 0.0
    tail_x: float = 0.0
    tail_y: float = 0.0
    updated_at: float = 0.0

class Live2DBridge:
    def __init__(self): self.state=Live2DState(updated_at=time())
    def touch(self): self.state.updated_at=time()
    def set_emotion(self,emotion:str): self.state.emotion=emotion;self.touch()
    def set_speaking(self,value:bool): self.state.speaking=bool(value);self.touch()
    def set_mouth(self,value:float,form=None):
        self.state.mouth_open=clamp(value,0,1)
        if form is not None:self.state.mouth_form=clamp(form)
        self.touch()
    def set_face(self,**values):
        for key,value in values.items():
            if hasattr(self.state,key):
                if key in ("eye_l","eye_r"):value=clamp(value,0,1)
                else:value=clamp(value)
                setattr(self.state,key,value)
        self.touch()
    def snapshot(self): return asdict(self.state)

live2d=Live2DBridge()
