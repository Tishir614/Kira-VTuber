"""Small persistent-ish mood model driven by Kira's activity."""
from dataclasses import dataclass,asdict
@dataclass
class Mood:
    energy:float=.72
    curiosity:float=.78
    social:float=.7
    focus:float=.68
mood=Mood()
def nudge(energy=0,curiosity=0,social=0,focus=0):
    for k,d in {"energy":energy,"curiosity":curiosity,"social":social,"focus":focus}.items():
        setattr(mood,k,max(0,min(1,getattr(mood,k)+d)))
    return asdict(mood)
def snapshot():return asdict(mood)
