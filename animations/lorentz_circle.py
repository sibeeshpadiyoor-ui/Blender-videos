"""Plus Two physics: a charged particle in a uniform magnetic field.

The magnetic force qvB is always perpendicular to the velocity, so it acts
as the centripetal force and the path is a circle of radius r = mv / qB.
"""
import math

import bpy

from bvid import scene as S

SECONDS = 9.0

RADIUS = 2.0
PERIOD = 3.0        # seconds per revolution
HEIGHT = 1.0        # height of the orbit above the base of the field arrows
BACKGROUND = (0.012, 0.014, 0.035)

BLUE = (0.15, 0.4, 1.0)
GREEN = (0.2, 1.0, 0.35)
YELLOW = (1.0, 0.8, 0.1)
RED = (1.0, 0.25, 0.2)
WHITE = (1.0, 1.0, 1.0)


def build(scene, fmt):
    fps = fmt.fps
    S.set_background(scene, BACKGROUND)

    # Uniform field B pointing up: a grid of identical arrows.
    field = S.emissive("Field", BLUE, 0.6)
    for ix in range(-2, 3):
        for iy in range(-2, 3):
            x, y = ix * 1.5, iy * 1.5
            S.add_arrow((x, y, 0), (x, y, 2 * HEIGHT), field, radius=0.022)

    # Everything that moves with the particle hangs off one rotating empty.
    # For a positive charge with B up, F = qv x B makes it circle clockwise
    # when seen from above.
    pivot = bpy.data.objects.new("Pivot", None)
    scene.collection.objects.link(pivot)
    pivot.location = (0, 0, HEIGHT)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(RADIUS, 0, 0))
    particle = bpy.context.object
    bpy.ops.object.shade_smooth()
    particle.data.materials.append(S.emissive("Charge", RED, 3.0))
    particle.parent = pivot

    S.add_arrow((RADIUS, 0, 0), (RADIUS, -1.5, 0), S.emissive("V", GREEN, 2.0),
                radius=0.05, parent=pivot)       # velocity: along the tangent
    S.add_arrow((RADIUS, 0, 0), (RADIUS - 1.2, 0, 0),
                S.emissive("F", YELLOW, 2.0),
                radius=0.05, parent=pivot)       # force: towards the centre

    # The path, drawn as the particle completes its first revolution.
    curve = bpy.data.curves.new("Path", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.025
    spline = curve.splines.new("POLY")
    steps = 128
    spline.points.add(steps)
    for i, point in enumerate(spline.points):
        a = -S.TAU * i / steps
        point.co = (RADIUS * math.cos(a), RADIUS * math.sin(a), 0, 1)
    path = bpy.data.objects.new("Path", curve)
    scene.collection.objects.link(path)
    path.location = (0, 0, HEIGHT)
    curve.materials.append(S.emissive("PathMat", WHITE, 0.8))

    for frame in range(1, scene.frame_end + 1):
        turns = (frame - 1) / (PERIOD * fps)
        S.key(pivot, frame, rotation_euler=(0, 0, -S.TAU * turns))
        S.key(curve, frame, bevel_factor_end=min(turns, 1.0))

    S.add_camera(scene, fmt, target=(0, 0, HEIGHT), direction=(0, -1, 0.6),
                 half_width=3.6, half_height=2.6)

    # Captions. Vertical video has room above and below the scene;
    # horizontal video puts them down the sides.
    def caption(text, x, y, size, color, at, align="CENTER"):
        obj = S.add_screen_text(scene, fmt, text, x, y, size,
                                S.emissive(text, color, 1.5), align)
        S.pop_in(obj, 1 + round(at * fps), fps)

    if fmt.aspect < 1:
        caption("Charge in a", 0, 0.80, 0.085, WHITE, 0.2)
        caption("magnetic field", 0, 0.70, 0.085, WHITE, 0.2)
        caption("B  magnetic field", -0.8, 0.50, 0.05, BLUE, 0.8, "LEFT")
        caption("v  velocity", -0.8, 0.43, 0.05, GREEN, 1.3, "LEFT")
        caption("F  magnetic force", -0.8, 0.36, 0.05, YELLOW, 1.8, "LEFT")
        caption("F = qvB", 0, -0.42, 0.075, YELLOW, 3.0)
        caption("F is always at 90° to v", 0, -0.52, 0.045, WHITE, 3.6)
        caption("qvB = mv² / r", 0, -0.64, 0.075, WHITE, 5.0)
        caption("r = mv / qB", 0, -0.80, 0.1, GREEN, 6.5)
    else:
        caption("Charge in a magnetic field", 0, 0.82, 0.04, WHITE, 0.2)
        caption("B  magnetic field", -0.95, 0.45, 0.022, BLUE, 0.8, "LEFT")
        caption("v  velocity", -0.95, 0.30, 0.022, GREEN, 1.3, "LEFT")
        caption("F  magnetic force", -0.95, 0.15, 0.022, YELLOW, 1.8, "LEFT")
        caption("F = qvB", 0.72, 0.40, 0.032, YELLOW, 3.0)
        caption("F is always at 90° to v", 0.72, 0.25, 0.018, WHITE, 3.6)
        caption("qvB = mv² / r", 0.72, 0.0, 0.032, WHITE, 5.0)
        caption("r = mv / qB", 0.72, -0.3, 0.042, GREEN, 6.5)
