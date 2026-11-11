"""A ring of glossy balls bouncing in a travelling wave.

Loops seamlessly, which suits Reels/Shorts (they auto-replay).
"""
import math

import bpy

from bvid import scene as S

SECONDS = 4.0  # length of one loop

COUNT = 18
RING_RADIUS = 3.0
BALL_RADIUS = 0.42
WAVES = 2          # wave crests around the ring
JUMP_HEIGHT = 1.8
BACKGROUND = (0.035, 0.03, 0.09)


def build(scene, fmt):
    S.set_background(scene, BACKGROUND, strength=0.05)
    S.add_floor((0.05, 0.045, 0.12))

    balls = []
    for i in range(COUNT):
        angle = S.TAU * i / COUNT
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=BALL_RADIUS, segments=48, ring_count=24,
            location=(RING_RADIUS * math.cos(angle),
                      RING_RADIUS * math.sin(angle), BALL_RADIUS))
        ball = bpy.context.object
        bpy.ops.object.shade_smooth()
        ball.data.materials.append(
            S.material(f"Ball{i}", S.hsv(i / COUNT, 0.85), roughness=0.25))
        balls.append(ball)

    # One keyframe per frame; the last frame leads back into the first.
    frames = scene.frame_end
    for frame in range(1, frames + 1):
        t = (frame - 1) / frames
        for i, ball in enumerate(balls):
            phase = S.TAU * (t - i / COUNT * WAVES)
            bounce = abs(math.sin(phase / 2)) ** 1.5      # sharp floor contact
            squash = 1.0 - 0.25 * (1.0 - bounce) ** 6     # squash on landing
            x, y, _ = ball.location
            S.key(ball, frame,
                  location=(x, y, BALL_RADIUS * squash + JUMP_HEIGHT * bounce),
                  scale=(2 - squash, 2 - squash, squash))

    S.add_area_light((4, -5, 8), energy=2500, size=6)
    S.add_area_light((-6, 3, 5), energy=1200, size=8, color=(0.6, 0.7, 1.0))

    S.add_camera(scene, fmt, target=(0, 0, 0.9), direction=(0, -1, 0.4),
                 half_width=RING_RADIUS + 0.9, half_height=2.0)
