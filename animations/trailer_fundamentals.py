"""Trailer for the Fundamentals of Physics series.

Script: scripts/channel/trailer-fundamentals-of-physics.md
"""
import math
from pathlib import Path

import bpy

from bvid import scene as S
from bvid.brand import Stage

LOGO = Path(__file__).resolve().parent.parent / "assets/brand/logo_mark.png"

NARRATION = [
    "Force. Energy. Momentum. Heat.",                                    # 0
    "You have heard these words all your life. "
    "But can you explain them, clearly?",                                # 1
    "Most of us learn physics fast, and forget it faster.",              # 2
    "So here, we go slowly. One idea in every video. "
    "Chapter by chapter, from the very beginning.",                      # 3
    "Each video starts with a question, explains one idea with a "
    "picture you can see, and ends with a challenge, "
    "so you know you really understood.",                                # 4
    "This is Fundamentals of Physics, from Beyond the Obvious Physics.", # 5
    "We begin with Chapter 1: measurement. "
    "What does it even mean to measure something?",                      # 6
    ("Follow, and let us build physics from the ground up. "
     "One clear idea at a time.", 1.0),                                  # 7
]


def build(scene, fmt, timeline):
    tl = timeline
    st = Stage(scene, fmt)
    st.subtitles(tl)

    def span(i):
        return tl.start(i), tl.end(i) - tl.start(i)

    # 0-1: four everyday words, then the question
    t0, d = span(0)
    for n, (word, color) in enumerate((("Force", "cyan"), ("Energy", "pink"),
                                       ("Momentum", "amber"),
                                       ("Heat", "green"))):
        st.label(word, 0, 2.2 - n * 1.15, 0.7, color,
                 t0 + d * (0.03 + 0.24 * n), tl.start(1) + 1.2)
    t1, d = span(1)
    st.label("?", 0, 0.5, 5.0, "gold", t1 + 1.4, tl.start(2), font="serif")
    st.text("CAN YOU EXPLAIN THEM", -0.52, 0.06, "fg", t1 + d * 0.62,
            tl.start(2))
    st.text("CLEARLY?", -0.60, 0.08, "gold", t1 + d * 0.74, tl.start(2))

    # 2: learn fast, forget faster; a clock spins and slows to a stop
    t2, d = span(2)
    clock = bpy.data.objects.new("Clock", None)
    scene.collection.objects.link(clock)
    clock.location = (0, 0, 0.7)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.3, minor_radius=0.05,
                                     major_segments=72, minor_segments=12,
                                     rotation=(math.pi / 2, 0, 0))
    ring = bpy.context.object
    ring.data.materials.append(st.mat("fg"))
    ring.parent = clock
    pivot = bpy.data.objects.new("Hand", None)
    scene.collection.objects.link(pivot)
    pivot.parent = clock
    S.add_box(0.1, 1.05, (0, 0, 0.5), st.mat("amber"), depth=0.06,
              parent=pivot)
    S.add_box(0.22, 0.22, (0, 0, 0), st.mat("amber"), depth=0.07,
              parent=pivot)
    st.show(clock, t2, tl.start(3))
    f0, f1 = 1 + round(t2 * st.fps), 1 + round(tl.start(3) * st.fps)
    for f in range(f0, f1 + 1):
        u = (f - f0) / (f1 - f0)
        angle = 5.5 * S.TAU * (1 - (1 - u) ** 3)       # fast, then slows to rest
        S.key(pivot, f, rotation_euler=(0, -angle, 0))
    st.text("LEARN FAST", -0.46, 0.07, "fg", t2 + d * 0.15, tl.start(3))
    st.text("FORGET FASTER", -0.56, 0.07, "pink", t2 + d * 0.55, tl.start(3))

    # 3: one idea at a time, chapter by chapter
    t3, d = span(3)
    idea = st.box(2.8, 1.2, 0, 1.9, "gold", t3 + d * 0.3, t3 + d * 0.55)
    st.label("1 IDEA", 0, 1.72, 0.55, "bg", t3 + d * 0.3, t3 + d * 0.55,
             front=0.1)
    steps = (("CH 1", "cyan"), ("CH 2", "green"), ("CH 3", "amber"),
             ("CH 4", "pink"), ("…", "muted"))
    for n, (name, color) in enumerate(steps):
        x, z = -1.9 + n * 0.95, -1.9 + n * 0.75
        at = t3 + d * (0.58 + 0.07 * n)
        st.box(0.85, 0.5, x, z, color, at, tl.start(4))
        st.label(name, x, z - 0.1, 0.26, "bg", at, tl.start(4), front=0.1)

    # 4: question, picture, challenge
    t4, d = span(4)
    for n, (symbol, text, color) in enumerate((
            ("?", "A QUESTION", "amber"),
            ("◎", "ONE IDEA, SEEN", "cyan"),
            ("✓", "A CHALLENGE", "green"))):
        z = 1.9 - n * 1.5
        at = t4 + d * (0.12 + 0.28 * n)
        st.box(0.9, 0.9, -2.0, z, color, at, tl.start(5))
        st.label(symbol, -2.0, z - 0.2, 0.6, "bg", at, tl.start(5),
                 font="maths", front=0.1)
        st.label(text, -1.3, z - 0.15, 0.4, "fg", at + 0.2, tl.start(5),
                 align="LEFT")

    # 5: the series name
    t5, d = span(5)
    st.image(LOGO, 0, 1.4, 3.4, t5 + d * 0.05, tl.start(6))
    st.label("FUNDAMENTALS", 0, -1.0, 0.62, "fg", t5 + d * 0.3, tl.start(6))
    st.label("OF PHYSICS", 0, -1.75, 0.62, "fg", t5 + d * 0.36, tl.start(6))
    st.label("from Beyond the Obvious Physics", 0, -2.45, 0.27, "gold",
             t5 + d * 0.6, tl.start(6), font="serif")

    # 6: Chapter 1, the table from the first video
    t6, d = span(6)
    st.label("CH 1  •  MEASUREMENT", 0, 2.7, 0.36, "amber", t6 + 0.1,
             tl.start(7))
    for width, height, x, z in ((4.0, 0.18, 0, -0.09), (0.16, 1.5, -1.7, -0.93),
                                (0.16, 1.5, 1.7, -0.93)):
        st.box(width, height, x, z, "blue", t6 + d * 0.25, tl.start(7))
    st.label("2", -0.5, 1.4, 1.5, "fg", t6 + d * 0.45, tl.start(7))
    st.label("?", 0.6, 1.4, 1.5, "amber", t6 + d * 0.55, tl.start(7))

    # 7: follow, and the closing line
    t7, d = span(7)
    st.box(2.6, 0.8, 0, 1.4, "pink", t7 + 0.2)
    st.label("FOLLOW", 0, 1.25, 0.45, "bg", t7 + 0.2, front=0.1)
    st.label("One clear idea", 0, -0.2, 0.62, "gold", t7 + d * 0.55,
             font="serif")
    st.label("at a time.", 0, -1.1, 0.62, "gold", t7 + d * 0.6, font="serif")
