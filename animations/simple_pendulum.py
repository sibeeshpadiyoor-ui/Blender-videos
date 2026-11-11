"""Simple pendulum: parts, forces, the period formula, and what the period
does and does not depend on. One minute, laid out for vertical video.

The swing uses the real period T = 2*pi*sqrt(L/g) for a 1 m string, so the
pendulum on screen keeps real time (about 2 s per swing).
"""
import math

import bpy

from bvid import scene as S

SECONDS = 60.0

G = 9.8
LENGTH_M = 1.0            # real length of the main pendulum
UNITS_PER_M = 3.0         # how big 1 m is drawn
AMPLITUDE = math.radians(20)
PIVOT_Z = 2.3

BACKGROUND = (0.006, 0.008, 0.02)
WHITE = (1.0, 1.0, 1.0)
GREY = (0.35, 0.38, 0.45)
RED = (1.0, 0.08, 0.05)
BLUE = (0.1, 0.35, 1.0)
GREEN = (0.1, 0.9, 0.2)
YELLOW = (1.0, 0.65, 0.02)


def period(length_m):
    return math.tau * math.sqrt(length_m / G)


def angle(length_m, seconds):
    return AMPLITUDE * math.cos(math.tau * seconds / period(length_m))


def add_pendulum(scene, x, length_m, bob_radius, mats):
    """Returns the pivot empty; rotating it about Y swings the pendulum."""
    length = length_m * UNITS_PER_M
    pivot = bpy.data.objects.new("Pivot", None)
    scene.collection.objects.link(pivot)
    pivot.location = (x, 0, PIVOT_Z)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=length,
                                        location=(0, 0, -length / 2))
    string = bpy.context.object
    string.data.materials.append(mats["string"])
    string.parent = pivot

    bpy.ops.mesh.primitive_uv_sphere_add(radius=bob_radius,
                                         location=(0, 0, -length))
    bob = bpy.context.object
    bpy.ops.object.shade_smooth()
    bob.data.materials.append(mats["bob"])
    bob.parent = pivot

    # A round peg at the pivot looks the same at any swing angle.
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0, 0, 0))
    peg = bpy.context.object
    peg.data.materials.append(mats["support"])
    peg.parent = pivot
    return pivot


def build(scene, fmt):
    fps = fmt.fps
    S.flat_style(scene)
    S.set_background(scene, BACKGROUND)

    mats = {
        "string": S.emissive("String", WHITE, 0.9),
        "bob": S.emissive("Bob", RED),
        "support": S.emissive("Support", GREY),
        "white": S.emissive("White", WHITE),
        "blue": S.emissive("Blue", BLUE),
        "green": S.emissive("Green", GREEN),
        "yellow": S.emissive("Yellow", YELLOW),
        "grey": S.emissive("Grey", GREY),
    }
    length = LENGTH_M * UNITS_PER_M

    # Ceiling
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, PIVOT_Z + 0.1))
    ceiling = bpy.context.object
    ceiling.scale = (2.3, 0.05, 0.035)
    ceiling.data.materials.append(mats["support"])

    S.add_camera(scene, fmt, target=(0, 0, 0), direction=(0, -1, 0),
                 half_width=2.4, half_height=2.4 * 16 / 9, margin=1.1)

    # --- Pendulums -------------------------------------------------------
    main = add_pendulum(scene, 0.0, LENGTH_M, 0.22, mats)       # 0 - 40 s
    left = add_pendulum(scene, -1.2, LENGTH_M, 0.2, mats)       # 40 - 56.5 s
    heavy = add_pendulum(scene, 1.2, LENGTH_M, 0.36, mats)      # 40 - 50 s
    short = add_pendulum(scene, 1.2, LENGTH_M / 4, 0.2, mats)   # 50 - 56.5 s
    S.show(main, 0.0, 40.0, fps)
    S.show(left, 40.0, 56.5, fps)
    S.show(heavy, 40.0, 50.0, fps)
    S.show(short, 50.0, 56.5, fps)

    # Things that follow the main bob.
    follow = bpy.data.objects.new("BobFollow", None)   # moves, never rotates
    scene.collection.objects.link(follow)
    restoring = bpy.data.objects.new("Restoring", None)  # tangent to the arc
    scene.collection.objects.link(restoring)
    restoring.parent = main
    restoring.location = (0, 0, -length)

    for frame in range(1, scene.frame_end + 1):
        t = (frame - 1) / fps
        a = angle(LENGTH_M, t)
        for pend in (main, left, heavy):
            S.key(pend, frame, rotation_euler=(0, a, 0))
        S.key(short, frame, rotation_euler=(0, angle(LENGTH_M / 4, t), 0))
        S.key(follow, frame, location=(-length * math.sin(a), 0,
                                       PIVOT_Z - length * math.cos(a)))
        # Restoring force is mg sin(theta), pointing back to the centre.
        S.key(restoring, frame,
              scale=(math.sin(a) / math.sin(AMPLITUDE), 1, 1))

    def group(parent, start, end, location=(0, 0, 0)):
        """An empty used to show/hide several objects together."""
        holder = bpy.data.objects.new("Group", None)
        scene.collection.objects.link(holder)
        holder.parent = parent
        holder.location = location
        S.show(holder, start, end, fps)
        return holder

    # Labels for the parts (6 - 16 s)
    g = group(main, 6.5, 16.0, (0, 0, -length / 2))
    S.add_world_text("L", (0.3, 0, 0), 0.4, mats["white"], parent=g)
    g = group(main, 8.5, 16.0, (0, 0, -length))
    S.add_world_text("m", (0.48, 0, 0), 0.4, mats["white"], parent=g)
    g = group(None, 10.5, 16.0, (0, 0.02, PIVOT_Z))
    for i in range(10):                                  # dashed vertical
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.012, depth=0.18, location=(0, 0, -0.15 - i * 0.32))
        dash = bpy.context.object
        dash.data.materials.append(mats["grey"])
        dash.parent = g

    # Forces (16 - 28 s)
    g = group(follow, 16.5, 28.0)
    S.add_arrow((0, 0, 0), (0, 0, -1.3), mats["blue"], 0.035, parent=g)
    S.add_world_text("mg", (0.42, 0, -1.15), 0.3, mats["blue"], parent=g)
    g = group(main, 18.0, 28.0, (0, 0, -length))
    S.add_arrow((0, 0, 0), (0, 0, 1.2), mats["green"], 0.035, parent=g)
    g = group(None, 20.5, 28.0)
    g.parent = restoring
    S.add_arrow((0, 0, 0), (1.0, 0, 0), mats["yellow"], 0.035, parent=g)

    # Labels for the comparisons
    g = group(None, 40.5, 50.0)
    S.add_world_text("m", (-1.2, 0, PIVOT_Z + 0.5), 0.36, mats["white"], g)
    S.add_world_text("4m", (1.2, 0, PIVOT_Z + 0.5), 0.36, mats["white"], g)
    g = group(None, 50.5, 56.5)
    S.add_world_text("L", (-1.2, 0, PIVOT_Z + 0.5), 0.36, mats["white"], g)
    S.add_world_text("L / 4", (1.2, 0, PIVOT_Z + 0.5), 0.36, mats["white"], g)

    # --- Captions --------------------------------------------------------
    # Positions are for a 9:16 column; wider formats keep that column
    # centred so the same layout still fits.
    column = min(1.0, (9 / 16) / fmt.aspect)

    def caption(text, y, size, color, start, end):
        obj = S.add_screen_text(scene, fmt, text, 0, y, size * column,
                                mats[color])
        S.show(obj, start, end, fps)

    caption("Simple Pendulum", 0.86, 0.085, "white", 0.2, None)

    caption("A mass on a string,", -0.50, 0.055, "white", 0.8, 6.0)
    caption("swinging under gravity", -0.58, 0.055, "white", 0.8, 6.0)

    caption("L = length of the string", -0.46, 0.05, "white", 6.5, 16.0)
    caption("m = mass of the bob", -0.56, 0.05, "white", 8.5, 16.0)
    caption("\u03b8 = angle from the vertical", -0.66, 0.05, "white", 10.5, 16.0)

    caption("Gravity mg", -0.42, 0.05, "blue", 16.5, 28.0)
    caption("Tension in the string", -0.50, 0.05, "green", 18.0, 28.0)
    caption("Restoring force", -0.58, 0.05, "yellow", 20.5, 28.0)
    caption("F = \u2212mg sin \u03b8", -0.68, 0.075, "yellow", 21.5, 28.0)
    caption("small \u03b8:  F \u2248 \u2212mg\u03b8  \u2192  SHM", -0.80, 0.05,
            "white", 24.0, 28.0)

    caption("Time period", -0.42, 0.055, "white", 28.5, 40.0)
    caption("T = 2\u03c0\u221a(L/g)", -0.54, 0.09, "green", 29.5, 40.0)
    caption("L = 1 m,  g = 9.8 m/s\u00b2", -0.68, 0.05, "white", 33.0, 40.0)
    caption("T \u2248 2 s  (this one is real time)", -0.78, 0.045, "white",
            35.0, 40.0)

    caption("Heavier bob?", -0.46, 0.06, "white", 40.5, 50.0)
    caption("Same period!", -0.58, 0.085, "green", 43.0, 50.0)
    caption("T does not depend on mass", -0.72, 0.05, "white", 45.0, 50.0)

    caption("Shorter string?", -0.46, 0.06, "white", 50.5, 56.5)
    caption("It swings faster", -0.58, 0.075, "yellow", 52.5, 56.5)
    caption("\u00bc length  \u2192  \u00bd period", -0.72, 0.055, "white",
            54.5, 56.5)

    caption("T = 2\u03c0\u221a(L/g)", -0.10, 0.12, "green", 56.8, None)
    caption("depends on length and gravity,", -0.26, 0.045, "white", 57.3, None)
    caption("not on mass", -0.33, 0.045, "white", 57.3, None)
