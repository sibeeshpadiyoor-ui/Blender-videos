"""Chapter 1, video 4: How do you change units without mistakes?

Script: scripts/ch01/04-changing-units.md
"""
import math

import bpy

from bvid import scene as S
from bvid.brand import SERIES, Stage

NARRATION = [
    "Answer to last time's challenge. "
    "How far does light travel in one billionth of a second?",          # 0
    "About thirty centimeters. Light moves about three hundred million "
    "meters each second, so in one billionth of a second it moves about "
    "zero point three meters.",                                         # 1
    "Now, today's topic: changing units.",                              # 2
    "The metric system was proposed in 1792. It even tried a ten-hour "
    "day! That part did not catch on.",                                 # 3
    "Today, science uses one system, S I. But other units are still "
    "around, so we need to change units without mistakes.",             # 4
    "Here is the trick. How many seconds are in two minutes? "
    "We know one minute is sixty seconds.",                             # 5
    "So one minute divided by sixty seconds is exactly one. "
    "Multiplying by one changes nothing. Only the unit changes.",       # 6
    "Two minutes times sixty seconds per minute. The minutes cancel, "
    "and we are left with one hundred twenty seconds.",                 # 7
    "If the units do not cancel, flip the fraction and try again.",     # 8
    ("Challenge. A car goes thirty-six kilometers per hour. "
     "How many meters per second is that?", 1.5),                       # 9
    "Next time: the prefixes. Kilo, milli, micro, nano.",               # 10
]


def build(scene, fmt, timeline):
    tl = timeline
    st = Stage(scene, fmt)
    st.headline(["Changing"], "Units",
                tag=f"{SERIES} • Ch 1 • 1-1 Measuring Things",
                start=tl.start(2) - 0.1, tag_start=0.1)
    st.subtitles(tl)

    def span(i):
        return tl.start(i), tl.end(i) - tl.start(i)

    def ring(cx, cz, radius, color, start, end, bevel=0.04):
        data = bpy.data.curves.new("Ring", "CURVE")
        data.dimensions = "3D"
        data.bevel_depth = bevel
        spline = data.splines.new("POLY")
        pts = [(cx + radius * math.cos(S.TAU * i / 96), 0,
                cz + radius * math.sin(S.TAU * i / 96)) for i in range(97)]
        spline.points.add(len(pts) - 1)
        for point, co in zip(spline.points, pts):
            point.co = (*co, 1)
        obj = bpy.data.objects.new("Ring", data)
        scene.collection.objects.link(obj)
        data.materials.append(st.mat(color))
        st.show(obj, start, end)

    # 0: last video's challenge
    t0, d = span(0)
    st.text("LAST VIDEO'S", 0.80, 0.05, "muted", t0, tl.start(1))
    st.text("CHALLENGE", 0.73, 0.075, "amber", t0, tl.start(1))
    st.label("How far does light travel", 0, 1.4, 0.34, "fg", t0 + d * 0.3,
             tl.start(2), font="body")
    st.label("in one billionth of a second?", 0, 0.85, 0.34, "fg",
             t0 + d * 0.45, tl.start(2), font="body")
    st.label("1 ns", 0, -0.9, 1.7, "gold", t0 + d * 0.65, tl.start(2),
             font="serif")

    # 1: the answer, 0.3 m = 30 cm
    t1, d = span(1)
    st.text("THE ANSWER", 0.77, 0.085, "green", t1, tl.start(2))
    st.label("0.3 m = 30 cm", 0, 2.0, 0.62, "gold", t1 + 0.3, tl.start(2),
             font="maths")
    st.box(4.0, 0.2, 0, 1.0, "soft", t1 + d * 0.15, tl.start(2))
    st.box(1.2, 0.2, -1.4, 1.0, "gold", t1 + d * 0.3, tl.start(2),
           front=0.05)
    st.label("1 m", 1.7, 1.45, 0.3, "soft", t1 + d * 0.15, tl.start(2),
             font="body")
    st.label("30 cm", -1.4, 1.45, 0.3, "gold", t1 + d * 0.3, tl.start(2),
             font="body")
    for text, z, at in (("300 000 000 m/s", -0.3, 0.45),
                        ("× 0.000 000 001 s", -0.9, 0.58),
                        ("≈ 0.3 m", -1.6, 0.72)):
        st.label(text, 0, z, 0.38, "green" if at > 0.7 else "fg",
                 t1 + d * at, tl.start(2), font="maths")

    # 3: the 1792 ten-hour day that did not catch on
    t3, d = span(3)
    cx, cz, r = 0.0, 0.9, 1.3
    ring(cx, cz, r, "cyan", t3 + 0.3, tl.start(4))
    for n in range(10):
        a = math.pi / 2 - S.TAU * (n + 1) / 10
        st.label(str(n + 1), cx + 1.0 * math.cos(a), cz + 1.0 * math.sin(a)
                 - 0.14, 0.3, "fg", t3 + 0.5 + 0.12 * n, tl.start(4),
                 font="body")
    st.label("1792", 0, -1.0, 0.7, "gold", t3 + 0.3, tl.start(4), font="serif")
    st.label("10-hour day", 0, -1.7, 0.4, "fg", t3 + d * 0.45, tl.start(4),
             font="body")
    st.label("✗", 0, cz - 0.3, 2.6, "pink", t3 + d * 0.7, tl.start(4),
             font="maths", front=0.1)
    st.label("did not catch on", 0, -2.3, 0.3, "pink", t3 + d * 0.75,
             tl.start(4), font="body")

    # 4: SI, but other units are still around
    t4, d = span(4)
    st.label("SI", -1.3, 1.5, 1.5, "gold", t4 + 0.3, tl.start(5),
             font="serif")
    st.label("other units", 1.2, 2.2, 0.28, "muted", t4 + d * 0.3,
             tl.start(5), font="body")
    for n, word in enumerate(("miles", "hours", "feet")):
        st.label(word, 1.2, 1.55 - 0.65 * n, 0.46, "fg", t4 + d * (0.35 + 0.08 * n),
                 tl.start(5), font="body")
    st.label("change them", 0, -0.5, 0.45, "fg", t4 + d * 0.6, tl.start(5),
             font="body")
    st.label("without mistakes", 0, -1.2, 0.5, "green", t4 + d * 0.7,
             tl.start(5), font="body")

    # 5: the question, 2 min = ? s
    t5, d = span(5)
    st.label("2 min = ? s", 0, 1.5, 0.75, "fg", t5 + 0.3, tl.start(6),
             font="maths")
    st.label("1 min = 60 s", 0, 0.2, 0.6, "green", t5 + d * 0.62, tl.start(6),
             font="maths")

    # 6: a fraction equal to one
    t6, d = span(6)
    st.label("1 min", -0.9, 1.45, 0.55, "fg", t6 + 0.3, tl.start(7),
             font="maths")
    st.box(1.9, 0.05, -0.9, 1.0, "fg", t6 + 0.4, tl.start(7))
    st.label("60 s", -0.9, 0.4, 0.55, "fg", t6 + 0.5, tl.start(7),
             font="maths")
    st.label("= 1", 1.4, 0.9, 0.9, "gold", t6 + d * 0.45, tl.start(7),
             font="maths")
    st.label("× 1 changes nothing", 0, -0.7, 0.34, "amber", t6 + d * 0.7,
             tl.start(7), font="body")

    # 7: the minutes cancel
    t7, d = span(7)
    row = 1.2
    st.label("2", -2.0, row, 0.7, "fg", t7 + 0.2, tl.start(8), font="maths")
    st.label("min", -1.25, row, 0.6, "fg", t7 + 0.2, tl.start(8),
             font="maths")
    st.label("×", -0.4, row, 0.6, "muted", t7 + d * 0.2, tl.start(8),
             font="maths")
    st.label("60 s", 0.8, row + 0.45, 0.55, "fg", t7 + d * 0.2, tl.start(8),
             font="maths")
    st.box(1.6, 0.05, 0.8, row, "fg", t7 + d * 0.2, tl.start(8))
    st.label("1", 0.35, row - 0.55, 0.55, "fg", t7 + d * 0.2, tl.start(8),
             font="maths")
    st.label("min", 1.05, row - 0.55, 0.55, "fg", t7 + d * 0.2, tl.start(8),
             font="maths")
    cancel = t7 + d * 0.5
    st.box(0.95, 0.07, -1.25, row + 0.06, "pink", cancel, tl.start(8),
           front=0.1)
    st.box(0.95, 0.07, 1.05, row - 0.5, "pink", cancel, tl.start(8),
           front=0.1)
    st.label("= 120 s", 0, -0.5, 1.0, "green", t7 + d * 0.72, tl.start(8),
             font="maths")

    # 8: if the units do not cancel, flip the fraction
    t8, d = span(8)
    st.label("✗  1 min / 60 s", 0, 1.7, 0.5, "pink", t8 + 0.2, tl.start(9),
             font="maths")
    st.label("units do not cancel", 0, 1.0, 0.3, "muted", t8 + d * 0.2,
             tl.start(9), font="body")
    st.label("flip it", 0, 0.1, 0.55, "amber", t8 + d * 0.4, tl.start(9),
             font="body")
    st.label("✓  60 s / 1 min", 0, -1.0, 0.6, "green", t8 + d * 0.65,
             tl.start(9), font="maths")

    # 9: the challenge
    t9, d = span(9)
    st.label("CHALLENGE", 0, 2.4, 0.38, "amber", t9, tl.start(10))
    st.label("A car goes", 0, 1.6, 0.34, "fg", t9 + d * 0.2, tl.start(10),
             font="body")
    st.label("36 km/h", 0, 0.5, 1.0, "gold", t9 + d * 0.3, tl.start(10),
             font="maths")
    st.label("= ? m/s", 0, -0.9, 0.85, "fg", t9 + d * 0.6, tl.start(10),
             font="maths")

    # 10: next time, the prefixes
    t10 = tl.start(10)
    st.label("NEXT", 0, 1.2, 0.28, "muted", t10 + 0.3, font="body")
    st.label("Prefixes", 0, 0.2, 0.9, "gold", t10 + 0.6, font="serif")
    st.label("kilo · milli · micro · nano", 0, -0.9, 0.34, "fg", t10 + 1.0,
             font="body")
