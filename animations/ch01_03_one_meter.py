"""Chapter 1, video 3: What is one meter, exactly?

Script: scripts/ch01/03-what-is-one-meter.md
"""
import math

import bpy

from bvid import scene as S
from bvid.brand import SERIES, Stage

NARRATION = [
    "Answer to last time's challenge. "
    "Which one is not a base quantity?",                                # 0
    "Speed. It is length divided by time, so it is built from base "
    "quantities.",                                                      # 1
    "Now, today's topic: length. What is one meter, exactly?",          # 2
    ("Today, the meter is defined using light and time. "
     "Strange, for a length! How did we get there? Let's follow its "
     "story.", 0.4),                                                    # 3
    "In 1792, France defined it from the Earth: one ten-millionth of "
    "the distance from the North Pole to the equator.",                 # 4
    "But nobody can carry the Earth around. So the meter became the "
    "distance between two scratches on a metal bar, kept near Paris.",  # 5
    "In 1960, it was tied to light: about 1.65 million wavelengths of "
    "orange-red light from krypton atoms.",                             # 6
    "Since 1983, one meter is the distance light travels in a vacuum "
    "in one two hundred ninety-nine million, seven hundred ninety-two "
    "thousand, four hundred fifty-eighth of a second.",                 # 7
    ("Each new definition was chosen to match the old one. "
     "The meter never changed its length. "
     "Only the way we reproduce it got better.", 0.6),                  # 8
    "That fixes the speed of light, exactly. "
    "Light never changes, and anyone can use it.",                      # 9
    ("Challenge. How far does light travel in one billionth of a second?",
     1.5),                                                              # 10
    "Next time: how do we change units without mistakes?",              # 11
]

ORANGE = "#FF6A2B"
METAL = "soft"


def build(scene, fmt, timeline):
    tl = timeline
    st = Stage(scene, fmt)
    # The new topic's title appears only after the old challenge is answered.
    st.headline(["What is one"], "Meter?",
                tag=f"{SERIES} • Ch 1 • 1-1 Measuring Things",
                start=tl.start(2) - 0.1, tag_start=0.1)
    st.subtitles(tl)

    def span(i):
        return tl.start(i), tl.end(i) - tl.start(i)

    def curve(points, color, bevel=0.05, name="Curve"):
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

    def draw_on(obj, data, start, end):
        """Reveal a curve along its length between two times."""
        f0, f1 = 1 + round(start * st.fps), 1 + round(end * st.fps)
        S.key(data, 1, bevel_factor_end=0.0)
        S.key(data, f0, bevel_factor_end=0.0)
        S.key(data, f1, bevel_factor_end=1.0)

    # 0-1: the answer to the last video's challenge, before the new topic
    t0 = tl.start(0)
    st.text("LAST VIDEO'S", 0.80, 0.05, "muted", t0, tl.start(1))
    st.text("CHALLENGE", 0.73, 0.075, "amber", t0, tl.start(1))
    st.text("THE ANSWER", 0.77, 0.085, "green", tl.start(1), tl.start(2))
    for n, text in enumerate(("A   Length", "B   Speed", "C   Time",
                               "D   Mass")):
        st.label(text, -1.2, (1.6, 0.7, -0.2, -1.1)[n], 0.5, "fg",
                 t0 + 0.3, tl.start(2), align="LEFT")
    t1, d = span(1)
    st.label("B   Speed", -1.2, 0.7, 0.5, "green", t1 + 0.1,
             tl.start(2), align="LEFT", front=0.05)
    st.label("= length ÷ time", 0, -2.0, 0.42, "amber", t1 + d * 0.4,
             tl.start(2), font="maths")

    # 2: the meter stick and the question
    t1, d = span(2)
    stick_z = 0.2
    stick = [st.box(4.0, 0.22, 0, stick_z, "amber", t1 + 0.4, tl.start(3))]
    for n in range(11):
        stick.append(st.box(0.04, 0.4 if n % 5 == 0 else 0.26, -2.0 + 0.4 * n,
                            stick_z - 0.3, "amber", t1 + 0.5 + 0.05 * n,
                            tl.start(3)))
    st.label("?", 0, 1.9, 1.7, "gold", t1 + d * 0.55, tl.start(3),
             font="serif")
    st.label("1 m", 0, -1.2, 0.5, "amber", t1 + d * 0.45, tl.start(3))

    # 3: hook, today's meter is defined by light and time
    t3h, d = span(3)
    st.label("TODAY'S METER", 0, 2.2, 0.38, "muted", t3h + 0.2, tl.start(4),
             font="body")
    st.label("defined with", 0, 1.2, 0.42, "fg", t3h + d * 0.2, tl.start(4),
             font="body")
    st.label("light", -1.0, 0.1, 0.8, "yellow", t3h + d * 0.3, tl.start(4))
    st.label("+", 0.0, 0.1, 0.8, "fg", t3h + d * 0.4, tl.start(4))
    st.label("time", 1.0, 0.1, 0.8, "cyan", t3h + d * 0.45, tl.start(4))
    st.label("?", 0, -1.4, 1.7, "gold", t3h + d * 0.65, tl.start(4),
             font="serif")

    # 4: 1792, a ten-millionth of the pole-to-equator distance
    t2, d = span(4)
    c = (0.0, 0.7)
    gone = tl.start(5)
    disk_mat = st.mat("#13265F")
    bpy.ops.mesh.primitive_circle_add(vertices=96, radius=1.45,
                                      fill_type="NGON",
                                      rotation=(math.pi / 2, 0, 0),
                                      location=(c[0], 0.04, c[1]))
    disk = bpy.context.object
    disk.data.materials.append(disk_mat)
    st.show(disk, t2 + d * 0.1, gone)
    ring, _ = curve([(c[0] + 1.45 * math.cos(a), 0, c[1] + 1.45 * math.sin(a))
                     for a in [S.TAU * i / 96 for i in range(97)]], "cyan", 0.03)
    st.show(ring, t2 + d * 0.1, gone)
    arc, arc_data = curve(
        [(c[0] + 1.45 * math.cos(math.pi / 2 - (math.pi / 2) * i / 40), -0.02,
          c[1] + 1.45 * math.sin(math.pi / 2 - (math.pi / 2) * i / 40))
         for i in range(41)], "amber", 0.07, "Arc")
    st.show(arc, 0.0, gone)           # visible from the start; drawn on below
    draw_on(arc, arc_data, t2 + d * 0.5, t2 + d * 0.85)
    st.label("North Pole", 0, c[1] + 1.95, 0.3, "fg", t2 + d * 0.55, gone,
             font="body")
    st.label("equator", 2.25, c[1] - 0.1, 0.3, "fg", t2 + d * 0.8, gone,
             font="body")
    st.label("1792", 0, -1.4, 0.7, "gold", t2 + d * 0.1, gone, font="serif")
    st.label("1 meter = 1 / 10 000 000", 0, -2.2, 0.3, "amber", t2 + d * 0.45,
             gone, font="maths")

    # 5: the metal bar near Paris
    t3, d = span(5)
    bar_z = 0.8
    st.box(4.4, 0.5, 0, bar_z, METAL, t3 + d * 0.3, tl.start(6))
    for x in (-1.8, 1.8):
        st.box(0.05, 0.62, x, bar_z, "bg", t3 + d * 0.4, tl.start(6),
               front=0.08)
    st.box(3.6, 0.05, 0, bar_z - 0.6, "amber", t3 + d * 0.5, tl.start(6))
    st.label("1 m", 0, bar_z - 1.15, 0.45, "amber", t3 + d * 0.5, tl.start(6))
    st.label("metal bar, near Paris", 0, bar_z + 0.8, 0.32, "soft",
             t3 + d * 0.65, tl.start(6), font="body")

    # 6: 1960, wavelengths of orange-red light
    t4, d = span(6)
    wave, wave_data = curve(
        [(-2.0 + 4.0 * i / 240, 0, 1.0 + 0.32 * math.sin(S.TAU * 7 * i / 240))
         for i in range(241)], ORANGE, 0.045, "Wave")
    st.show(wave, 0.0, tl.start(7))
    draw_on(wave, wave_data, t4 + d * 0.3, t4 + d * 0.6)
    st.box(4.0, 0.05, 0, 0.35, "amber", t4 + d * 0.3, tl.start(7))
    st.label("1960", 0, 2.3, 0.7, "gold", t4 + 0.2, tl.start(7), font="serif")
    st.label("1 650 763.73", 0, -0.6, 0.7, "fg", t4 + d * 0.55, tl.start(7),
             font="maths")
    st.label("wavelengths of krypton light", 0, -1.3, 0.3, ORANGE,
             t4 + d * 0.65, tl.start(7), font="body")

    # 7: 1983, how far light goes in a tiny slice of a second
    t5, d = span(7)
    st.label("1983", 0, 2.3, 0.7, "gold", t5 + 0.2, tl.start(8), font="serif")
    st.box(4.0, 0.2, 0, 0.9, "green", t5 + 0.5, tl.start(8))
    for x in (-2.0, 2.0):
        st.box(0.07, 0.6, x, 0.9, "green", t5 + 0.5, tl.start(8))
    st.label("1 meter", 0, 1.65, 0.4, "green", t5 + d * 0.2, tl.start(8))
    for n in range(3):
        a = t5 + d * (0.25 + 0.22 * n)
        dot = S.add_box(0.3, 0.3, (-2.0, -0.1, 0.9), st.mat("yellow"))
        st.show(dot, a, a + 1.4)
        S.move(dot, a + 0.15, a + 1.2, (2.0, -0.1, 0.9), st.fps)
    st.label("in this time:", 0, -0.2, 0.3, "muted", t5 + d * 0.5,
             tl.start(8), font="body")
    st.label("1 / 299 792 458 s", 0, -1.0, 0.55, "yellow", t5 + d * 0.55,
             tl.start(8), font="maths")

    # 8: same length every time, only a better way to reproduce it
    t8s, d = span(8)
    st.box(4.0, 0.22, 0, 1.1, "green", t8s + 0.2, tl.start(9))
    st.label("1 m", 0, 1.75, 0.5, "green", t8s + 0.3, tl.start(9))
    st.label("SAME LENGTH", 0, 2.45, 0.5, "amber", t8s + d * 0.1,
             tl.start(9))
    for n, (text, color) in enumerate((("1792  Earth", "cyan"),
                                        ("Metal bar", "fg"),
                                        ("1960  Krypton light", ORANGE),
                                        ("1983  Speed of light", "yellow"))):
        st.label(text, 0, (0.3, -0.5, -1.3, -2.1)[n], 0.42, color,
                 t8s + d * (0.3 + 0.17 * n), tl.start(9), font="body")
    st.label("only the way we reproduce it improved", 0, -2.9, 0.26, "muted",
             t8s + d * 0.85, tl.start(9), font="body")

    # 9: the speed of light is now fixed
    t6, d = span(9)
    st.label("c = 299 792 458 m/s", 0, 1.4, 0.5, "gold", t6 + 0.2,
             tl.start(10), font="maths")
    st.label("EXACTLY", 0, 0.5, 0.7, "amber", t6 + d * 0.2, tl.start(10))
    for text, z, delay in (("✓  never changes", -0.8, 0.5),
                           ("✓  anyone can use it", -1.6, 0.75)):
        st.label(text, 0, z, 0.4, "green", t6 + d * delay, tl.start(10),
                 font="maths")

    # 10: challenge
    t7, d = span(10)
    st.label("CHALLENGE", 0, 2.4, 0.38, "amber", t7, tl.start(11))
    st.label("How far does light travel", 0, 1.5, 0.3, "fg", t7 + d * 0.3,
             tl.start(11), font="body")
    st.label("in one billionth of a second?", 0, 0.95, 0.3, "fg",
             t7 + d * 0.45, tl.start(11), font="body")
    st.label("1 ns", 0, -0.7, 1.6, "gold", t7 + d * 0.65, tl.start(11),
             font="serif")

    # 11: next
    t8 = tl.start(11)
    st.label("NEXT", 0, 0.8, 0.28, "muted", t8 + 0.3, font="body")
    st.label("Change units", 0, 0.0, 0.6, "fg", t8 + 0.6)
    st.label("without mistakes", 0, -1.0, 0.7, "gold", t8 + 1.0, font="serif")
