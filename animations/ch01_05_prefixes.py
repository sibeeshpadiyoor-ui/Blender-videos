"""Chapter 1, video 5: Powers of ten and prefixes.

Script: scripts/ch01/05-powers-of-ten-and-prefixes.md
"""
from bvid.brand import SERIES, Stage

NARRATION = [
    "Answer to last time's challenge. "
    "Thirty-six kilometers per hour. How many meters per second?",      # 0
    "Ten meters per second. Multiply by a thousand meters per kilometer, "
    "and by one hour per thirty-six hundred seconds. "
    "The kilometers and the hours cancel.",                             # 1
    "Now, today's topic: powers of ten, and prefixes.",                 # 2
    "Physics numbers can be huge, or tiny. "
    "All those zeros are slow to write, and easy to get wrong.",        # 3
    "So we count the zeros. Three billion meters is three times ten to "
    "the ninth meters. The small raised number counts the zeros.",      # 4
    "For tiny numbers, the power goes negative. This tiny time is two "
    "times ten to the minus seven seconds.",                            # 5
    "Even shorter: give each power of ten a name. Kilo is a thousand. "
    "Milli is a thousandth. Micro is a millionth. "
    "Nano is a billionth.",                                             # 6
    "A prefix is just a multiplier. Five kilometers means five times a "
    "thousand meters. Two nanoseconds means two times ten to the minus "
    "nine seconds.",                                                    # 7
    ("Challenge. How many micrometers are in one millimeter?", 1.5),    # 8
    "Next time: what is one second?",                                   # 9
]


def build(scene, fmt, timeline):
    tl = timeline
    st = Stage(scene, fmt)
    st.headline(["Powers of"], "Ten",
                tag=f"{SERIES} • Ch 1 • 1-1 Measuring Things",
                start=tl.start(2) - 0.1, tag_start=0.1)
    st.subtitles(tl)

    def span(i):
        return tl.start(i), tl.end(i) - tl.start(i)

    # 0: last video's challenge
    t0, d = span(0)
    st.text("LAST VIDEO'S", 0.80, 0.05, "muted", t0, tl.start(1))
    st.text("CHALLENGE", 0.73, 0.075, "amber", t0, tl.start(1))
    st.label("36 km/h", 0, 1.1, 1.0, "gold", t0 + d * 0.4, tl.start(1),
             font="maths")
    st.label("= ? m/s", 0, -0.3, 0.85, "fg", t0 + d * 0.65, tl.start(1),
             font="maths")

    # 1: the answer, with the units cancelling
    t1, d = span(1)
    st.text("THE ANSWER", 0.77, 0.085, "green", t1, tl.start(2))
    row, big = 1.4, 0.36
    on = tl.start(2)
    st.label("36", -2.3, row, 0.45, "fg", t1 + 0.3, on, font="maths")
    st.label("km", -1.5, row + 0.38, big, "fg", t1 + 0.3, on, font="maths")
    st.box(0.65, 0.035, -1.5, row, "fg", t1 + 0.3, on)
    st.label("h", -1.5, row - 0.42, big, "fg", t1 + 0.3, on, font="maths")
    st.label("×", -0.98, row, big, "muted", t1 + d * 0.2, on, font="maths")
    st.label("1000 m", -0.2, row + 0.38, big, "fg", t1 + d * 0.2, on,
             font="maths")
    st.box(1.35, 0.035, -0.2, row, "fg", t1 + d * 0.2, on)
    st.label("1", -0.5, row - 0.42, big, "fg", t1 + d * 0.2, on,
             font="maths")
    st.label("km", 0.1, row - 0.42, big, "fg", t1 + d * 0.2, on,
             font="maths")
    st.label("×", 0.75, row, big, "muted", t1 + d * 0.45, on, font="maths")
    st.label("1", 1.35, row + 0.38, big, "fg", t1 + d * 0.45, on,
             font="maths")
    st.label("h", 1.8, row + 0.38, big, "fg", t1 + d * 0.45, on,
             font="maths")
    st.box(1.1, 0.035, 1.6, row, "fg", t1 + d * 0.45, on)
    st.label("3600 s", 1.6, row - 0.42, big, "fg", t1 + d * 0.45, on,
             font="maths")
    cancel = t1 + d * 0.72
    for x, z, w in ((-1.5, row + 0.38, 0.55), (0.1, row - 0.42, 0.55),
                    (-1.5, row - 0.42, 0.28), (1.8, row + 0.38, 0.28)):
        st.box(w, 0.05, x, z, "pink", cancel, on, front=0.1)
    st.label("= 10 m/s", 0, -0.5, 1.0, "green", t1 + d * 0.85, on,
             font="maths")

    # 3: huge and tiny numbers
    t3, d = span(3)
    st.label("3 000 000 000 m", 0, 1.5, 0.45, "fg", t3 + 0.3, tl.start(4),
             font="maths")
    st.label("0.000 000 2 s", 0, 0.2, 0.45, "fg", t3 + d * 0.45,
             tl.start(4), font="maths")
    st.label("?", 0, -1.7, 1.7, "pink", t3 + d * 0.7, tl.start(4),
             font="serif")

    # 4: count the zeros, big numbers
    t4, d = span(4)
    st.label("3 000 000 000 m", 0, 1.7, 0.45, "fg", t4, tl.start(5),
             font="maths")
    st.label("9 zeros", 0, 0.8, 0.45, "amber", t4 + d * 0.3, tl.start(5),
             font="body")
    st.label("3 × 10⁹ m", 0, -0.6, 0.95, "gold", t4 + d * 0.55, tl.start(5),
             font="maths")

    # 5: tiny numbers, negative powers
    t5, d = span(5)
    st.label("0.000 000 2 s", 0, 1.7, 0.45, "fg", t5, tl.start(6),
             font="maths")
    st.label("7 places", 0, 0.8, 0.45, "amber", t5 + d * 0.3, tl.start(6),
             font="body")
    st.label("2 × 10⁻⁷ s", 0, -0.6, 0.95, "gold", t5 + d * 0.55,
             tl.start(6), font="maths")

    # 6: the four prefixes
    t6, d = span(6)
    rows = (("kilo", "10³", "a thousand", "cyan"),
            ("milli", "10⁻³", "a thousandth", "pink"),
            ("micro", "10⁻⁶", "a millionth", "amber"),
            ("nano", "10⁻⁹", "a billionth", "green"))
    for n, (name, power, words, color) in enumerate(rows):
        z = 1.9 - 1.15 * n
        at = t6 + d * (0.2 + 0.2 * n)
        st.label(name, -2.1, z, 0.5, color, at, tl.start(7), align="LEFT",
                 font="body")
        st.label(power, -0.3, z, 0.5, "fg", at + 0.2, tl.start(7),
                 align="LEFT", font="maths")
        st.label(words, 0.75, z, 0.28, "muted", at + 0.4, tl.start(7),
                 align="LEFT", font="body")

    # 7: a prefix is a multiplier
    t7, d = span(7)
    for n, (left, right) in enumerate((("5 km", "= 5 × 10³ m"),
                                         ("2 ns", "= 2 × 10⁻⁹ s"))):
        z = 1.5 - 1.6 * n
        at = t7 + d * (0.1 + 0.45 * n)
        st.label(left, -1.6, z, 0.46, "amber", at, tl.start(8),
                 font="maths")
        st.label(right, 0.7, z, 0.46, "fg", at + 1.0, tl.start(8),
                 font="maths")

    # 8: the challenge
    t8, d = span(8)
    st.label("CHALLENGE", 0, 2.4, 0.38, "amber", t8, tl.start(9))
    st.label("How many micrometers", 0, 1.5, 0.34, "fg", t8 + d * 0.2,
             tl.start(9), font="body")
    st.label("in one millimeter?", 0, 0.95, 0.34, "fg", t8 + d * 0.35,
             tl.start(9), font="body")
    st.label("1 mm = ? μm", 0, -0.5, 0.95, "gold", t8 + d * 0.55,
             tl.start(9), font="maths")

    # 9: next time
    t9 = tl.start(9)
    st.label("NEXT", 0, 0.8, 0.28, "muted", t9 + 0.3, font="body")
    st.label("One second", 0, -0.1, 0.9, "gold", t9 + 0.6, font="serif")
