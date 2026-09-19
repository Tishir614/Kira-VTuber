"""Automatic mouth calibration from a synthesized WAV."""
import math,wave
from pathlib import Path
from .lipsync import _pcm_rms
from .character_runtime import save,snapshot

def analyze_wav(path:Path,frame_ms:int=30):
 values=[]
 with wave.open(str(path),"rb") as w:
  width=w.getsampwidth();rate=w.getframerate();frames=max(1,int(rate*frame_ms/1000))
  while True:
   raw=w.readframes(frames)
   if not raw:break
   values.append(_pcm_rms(raw,width))
 if not values:raise RuntimeError("Calibration audio is empty")
 values.sort();n=len(values)
 noise=values[max(0,int(n*.15)-1)];speech=values[min(n-1,int(n*.88))]
 peak=max(1800.0,speech)
 gate=max(.006,min(.08,(noise/max(peak,1))*1.8))
 gain=max(.55,min(2.4,7600.0/peak))
 dynamic=max(0.0,min(1.0,(speech-noise)/max(speech,1)))
 return {"mouth_peak":round(peak,2),"mouth_gate":round(gate,4),"mouth_gain":round(gain,3),
 "mouth_attack":round(.48+dynamic*.22,3),"mouth_release":round(.22+dynamic*.14,3),
 "noise_rms":round(noise,2),"speech_rms":round(speech,2),"dynamic":round(dynamic,3)}
def calibrate(path:Path):
 result=analyze_wav(path);save({"voice":{k:v for k,v in result.items() if k.startswith("mouth_")}})
 return {"ok":True,"calibration":result,**snapshot()}
