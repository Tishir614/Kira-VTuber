import asyncio
import math
import wave
from pathlib import Path
from .live2d import live2d
from .character_runtime import load as character_profile, capabilities

def _pcm_rms(raw: bytes, width: int) -> float:
    if not raw or width not in (1,2,3,4): return 0.0
    count=len(raw)//width
    if count<=0:return 0.0
    total=0.0
    for i in range(0,count*width,width):
        chunk=raw[i:i+width]
        sample=chunk[0]-128 if width==1 else int.from_bytes(chunk,"little",signed=True)
        total+=sample*sample
    return math.sqrt(total/count)

async def drive_from_wav(path:Path,frame_ms:int=30):
    """Character-aware RMS lip sync with noise gate, gain, attack/release smoothing."""
    cfg=character_profile().get("voice",{});caps=capabilities()
    gain=max(.2,min(3.0,float(cfg.get("mouth_gain",1.0))))
    attack=max(.05,min(.95,float(cfg.get("mouth_attack",.58))))
    release=max(.03,min(.95,float(cfg.get("mouth_release",.28))))
    gate=max(0.0,min(.2,float(cfg.get("mouth_gate",.018))))
    peak=max(1000.0,float(cfg.get("mouth_peak",9000.0)))
    current=0.0
    try:
        with wave.open(str(path),"rb") as w:
            width=w.getsampwidth();rate=w.getframerate();frames=max(1,int(rate*frame_ms/1000))
            while True:
                raw=w.readframes(frames)
                if not raw:break
                target=max(0.0,min(1.0,(_pcm_rms(raw,width)/peak)*gain))
                if target<gate:target=0.0
                alpha=attack if target>current else release
                current+=(target-current)*alpha
                # Mouth form adds a tiny speech-shaped variation only when the model supports it.
                form=math.sin(w.tell()/max(rate,1)*11.0)*.12*current if caps.get("mouth_form") else 0.0
                live2d.set_mouth(current,form)
                await asyncio.sleep(frame_ms/1000)
    finally:
        live2d.set_mouth(0.0,0.0)
