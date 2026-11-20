"""Chapter 1, video 6: What is one second?

Script: scripts/ch01/06-what-is-one-second.md
"""
import math

import bpy

from bvid import scene as S
from bvid.brand import SERIES, Stage

NARRATION = [
    "One millimeter holds a thousand micrometers. Ten to the minus "
    "three, divided by ten to the minus six.",                          # 0
    "Your phone says one second has passed. "
    "But who decides how long a second is?",                            # 1
    "Time answers two questions. When did it happen? "
    "And how long did it last?",                                        # 2
    "To measure time, we need something that repeats, again and again. "
    "For centuries, people used the Earth's spin. "
    "One turn is one day.",                                             # 3
    "But the spin is not perfectly steady. The Moon's tides and big "
    "winds change the length of a day by a few thousandths of a "
    "second.",                                                          # 4
    "A better repeating thing is an atom. A cesium atom gives off "
    "light that wiggles at a fixed rate.",                              # 5
    "Since 1967, one second is the time taken by nine billion, one "
    "hundred ninety-two million, six hundred thirty-one thousand, "
    "seven hundred seventy wiggles of that light.",                     # 6
    "Atomic clocks are so steady that two of them could run for six "
    "thousand years before differing by even one second.",              # 7
    ("Next time: what is one kilogram? Its standard is a small metal "
     "cylinder, kept near Paris.", 0.5),                                # 8
]


def build(scene, fmt, timeline):
    tl = timeline
    st = Stage(scene, fmt)
    st.headline(["What is one"], "Second?",
                tag=f"{SERIES} • Ch 1 • 1-2 Time",
                start=tl.start(1) - 0.1, tag_start=0.1)
    st.subtitles(tl)

    def span(i):
        return tl.start(i), tl.end(i) - tl.start(i)

    def curve(points, color, bevel=0.04, name="Curve"):
        data = bpy.data.curves.new(name, "CURVE")
        data.dimensions = "3D"
        data.bevel_depth = bevel
        spline = data.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for point, co in zip(spline.points, points):
            point.co = (*co, 1)
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        data.materials.append(st.mat(color))
        return obj, data

    def draw_on(data, start, end):
        f0, f1 = 1 + round(start * st.fps), 1 + round(end * st.fps)
        S.key(data, 1, bevel_factor_end=0.0)
        S.key(data, f0, bevel_factor_end=0.0)
        S.key(data, f1, bevel_factor_end=1.0)

    def circle(cx, cz, radius):
        return [(cx + radius * math.cos(S.TAU * i / 96), 0,
                 cz + radius * math.sin(S.TAU * i / 96)) for i in range(97)]

    # 0: the answer to the last video's question (no new challenge here)
    t0, d = span(0)
    st.text("LAST VIDEO'S QUESTION", 0.82, 0.04, "muted", t0, tl.start(1))
    st.text("1 mm = ? μm", 0.75, 0.065, "fg", t0, tl.start(1), font="maths")
    for text, z, color, at in (("1 mm = 10⁻³ m", 1.7, "cyan", 0.15),
                               ("1 μm = 10⁻⁶ m", 0.8, "amber", 0.3),
                               ("10⁻³ ÷ 10⁻⁶ = 10³", -0.3, "fg", 0.5),
                               ("= 1000 μm", -1.4, "green", 0.7)):
        st.label(text, 0, z, 0.9 if color == "green" else 0.5, color,
                 t0 + d * at, tl.start(1), font="maths")

    # 1: hook, who decides how long a second is
    t0, d = span(1)
    st.label("1 s", 0, 1.2, 2.2, "gold", t0 + 0.5, tl.start(2), font="serif")
    st.label("who decides?", 0, -0.6, 0.6, "fg", t0 + d * 0.6, tl.start(2),
             font="body")
    st.label("?", 0, -1.8, 1.5, "pink", t0 + d * 0.75, tl.start(2),
             font="serif")

    # 2: two questions, "when?" and "how long?"
    t3, d = span(2)
    obj, _ = curve(circle(0, 1.1, 0.6), "cyan", 0.04, "Clock")
    st.show(obj, t3 + d * 0.1, tl.start(3))
    st.label("WHEN?", 0, 2.3, 0.7, "cyan", t3 + d * 0.1, tl.start(3))
    st.label("HOW LONG?", 0, -0.3, 0.7, "amber", t3 + d * 0.55, tl.start(3))
    for n in range(3):
        st.box(0.95, 0.2, -1.0 + n, -1.2, "amber", t3 + d * (0.7 + 0.08 * n),
               tl.start(3))
    for x in (-1.5, 1.5):
        st.box(0.05, 0.6, x, -1.2, "fg", t3 + d * 0.65, tl.start(3))

    # 3: the Earth's spin, one turn is a day
    t4, d = span(3)
    cx, cz, r = 0.0, 0.9, 1.2
    bpy.ops.mesh.primitive_circle_add(vertices=96, radius=r, fill_type="NGON",
                                      rotation=(math.pi / 2, 0, 0),
                                      location=(cx, 0.04, cz))
    disk = bpy.context.object
    disk.data.materials.append(st.mat("#13265F"))
    st.show(disk, t4 + 0.2, tl.start(4))
    ring, _ = curve(circle(cx, cz, r), "cyan", 0.03, "Earth")
    st.show(ring, t4 + 0.2, tl.start(4))
    angle0 = math.pi / 2
    dot = S.add_box(0.28, 0.28, (cx, -0.1, cz + r), st.mat("yellow"))
    start_turn, end_turn = t4 + d * 0.45, t4 + d * 0.9
    st.show(dot, t4 + d * 0.4, tl.start(4))
    steps = 12
    for k in range(1, steps + 1):
        a = angle0 - S.TAU * k / steps
        S.move(dot, start_turn + (end_turn - start_turn) * (k - 1) / steps,
               start_turn + (end_turn - start_turn) * k / steps,
               (cx + r * math.cos(a), -0.1, cz + r * math.sin(a)), st.fps)
    st.label("1 turn = 1 day", 0, -1.2, 0.5, "fg", t4 + d * 0.6, tl.start(4),
             font="body")

    # 4: the spin is not perfectly steady
    t5, d = span(4)
    st.label("not perfectly steady", 0, 1.9, 0.45, "pink", t5 + 0.3,
             tl.start(5), font="body")
    st.label("the length of a day changes by", 0, 0.5, 0.32, "fg",
             t5 + d * 0.35, tl.start(5), font="body")
    st.label("a few ms", 0, -0.6, 1.0, "amber", t5 + d * 0.6, tl.start(5),
             font="maths")
    st.label("(thousandths of a second)", 0, -1.5, 0.28, "muted",
             t5 + d * 0.7, tl.start(5), font="body")

    # 5: a cesium atom and its light
    t6, d = span(5)
    atom = st.box(0.7, 0.7, -1.8, 1.2, "yellow", t6 + 0.3, tl.start(6))
    st.label("cesium-133 atom", -1.0, 0.3, 0.3, "yellow", t6 + d * 0.3,
             tl.start(6), font="body")
    wave, wave_data = curve(
        [(-1.3 + 3.4 * i / 240, 0, 1.2 + 0.3 * math.sin(S.TAU * 6 * i / 240))
         for i in range(241)], "cyan", 0.045, "Light")
    st.show(wave, 0.0, tl.start(6))
    draw_on(wave_data, t6 + d * 0.4, t6 + d * 0.8)
    st.label("light that wiggles", 0.4, -0.5, 0.4, "cyan", t6 + d * 0.65,
             tl.start(6), font="body")
    st.label("at a fixed rate", 0.4, -1.1, 0.4, "fg", t6 + d * 0.8,
             tl.start(6), font="body")

    # 6: the 1967 definition
    t7, d = span(6)
    st.label("1967", 0, 2.4, 0.7, "gold", t7 + 0.2, tl.start(7), font="serif")
    wave2, wave2_data = curve(
        [(-2.0 + 4.0 * i / 480, 0,
          1.3 + 0.25 * math.sin(S.TAU * 30 * i / 480))
         for i in range(481)], "cyan", 0.035, "Wiggles")
    st.show(wave2, 0.0, tl.start(7))
    draw_on(wave2_data, t7 + 0.4, t7 + d * 0.8)
    st.label("9 192 631 770", 0, 0.1, 0.65, "gold", t7 + d * 0.5,
             tl.start(7), font="maths")
    st.label("wiggles", 0, -0.6, 0.4, "fg", t7 + d * 0.6, tl.start(7),
             font="body")
    st.label("= 1 second", 0, -1.5, 0.75, "green", t7 + d * 0.8, tl.start(7),
             font="maths")

    # 7: atomic clocks are very steady
    t8, d = span(7)
    st.label("6000 years", 0, 1.6, 1.0, "gold", t8 + 0.3, tl.start(8),
             font="serif")
    st.label("two atomic clocks", 0, 0.5, 0.4, "fg", t8 + d * 0.3,
             tl.start(8), font="body")
    st.label("less than 1 s apart", 0, -0.5, 0.5, "green", t8 + d * 0.55,
             tl.start(8), font="body")
    st.label("(in principle)", 0, -1.3, 0.26, "muted", t8 + d * 0.7,
             tl.start(8), font="body")

    # 8: next time
    t10 = tl.start(8)
    st.label("NEXT", 0, 0.8, 0.28, "muted", t10 + 0.3, font="body")
    st.label("One kilogram", 0, -0.1, 0.8, "gold", t10 + 0.6, font="serif")
    st.label("a small metal cylinder,", 0, -1.2, 0.34, "fg", t10 + 2.2,
             font="body")
    st.label("kept near Paris", 0, -1.8, 0.34, "fg", t10 + 2.7, font="body")
