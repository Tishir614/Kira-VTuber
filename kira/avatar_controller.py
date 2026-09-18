import asyncio
import math
from time import monotonic
from .live2d import live2d

class AvatarController:
    def __init__(self):
        self.running = False

    async def idle_loop(self):
        self.running = True
        start = monotonic()
        while self.running:
            t = monotonic() - start
            # Renderer can consume these generic normalized values later.
            live2d.state.angle_x = math.sin(t * 0.45) * 4.0
            live2d.state.angle_y = math.sin(t * 0.31) * 2.0
            live2d.state.body_angle_x = math.sin(t * 0.22) * 1.5
            live2d.state.breath = (math.sin(t * 1.7) + 1.0) / 2.0
            live2d.state.updated_at = monotonic()
            await asyncio.sleep(0.05)

avatar_controller = AvatarController()
