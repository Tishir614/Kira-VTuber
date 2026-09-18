import asyncio
import math
import random
from time import monotonic
from .live2d import live2d

class AvatarController:
    def __init__(self):
        self.running=False
        self._next_glance=0.0
        self._glance_x=0.0
        self._glance_y=0.0

    async def idle_loop(self):
        self.running=True
        start=monotonic()
        while self.running:
            t=monotonic()-start
            speaking=live2d.state.speaking
            # Layered motion: slow posture drift + speech emphasis + tiny human-like corrections.
            drift_x=math.sin(t*.43)*4.2 + math.sin(t*.13)*1.2
            drift_y=math.sin(t*.29)*2.2
            nod=(math.sin(t*2.6)*2.4 if speaking else math.sin(t*.21)*.6)
            emphasis=(math.sin(t*1.35)*1.8 if speaking else 0.0)
            live2d.state.angle_x=drift_x+emphasis
            live2d.state.angle_y=drift_y+nod
            live2d.state.angle_z=math.sin(t*.19)*1.4
            live2d.state.body_angle_x=math.sin(t*.22)*1.8+(math.sin(t*.9)*.7 if speaking else 0)
            live2d.state.breath=(math.sin(t*1.65)+1)/2
            # Occasional gaze shifts make the avatar less mechanical.
            if t>=self._next_glance:
                self._glance_x=random.uniform(-.45,.45)
                self._glance_y=random.uniform(-.22,.22)
                self._next_glance=t+random.uniform(2.5,6.0)
            live2d.state.eye_x += (self._glance_x-live2d.state.eye_x)*.08
            live2d.state.eye_y += (self._glance_y-live2d.state.eye_y)*.08
            live2d.state.updated_at=monotonic()
            await asyncio.sleep(.05)

avatar_controller=AvatarController()
