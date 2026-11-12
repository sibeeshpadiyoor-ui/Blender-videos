"""Chapter 1, video 1: What does it mean to measure?

Script: scripts/ch01/01-what-is-measurement.md
Visuals are cued to the start of each narration sentence. A sentence
written as (text, seconds) is followed by that much extra silence.
"""
from bvid.brand import Stage

NARRATION = [
    "This table is two long.",                                       # 0
    ("Two... what?", 0.8),                                           # 1
    "A number alone tells us nothing.",                              # 2
    "To measure means to compare.",                                  # 3
    ("We choose one length, and count how many times it fits.", 0.6),  # 4
    "That chosen length is called a unit. But which unit?",          # 5
    "With my hand span, the table is ten spans long.",               # 6
    "My friend has a bigger hand, and gets only eight.",             # 7
    ("Same table, two different answers.", 0.8),                     # 8
    "So the whole world agrees on one standard for each unit.",      # 9
    "For length, it is the meter.",                                  # 10
    ("A good standard never changes, and everyone can use it.", 0.6),  # 11
    "Now the table is two meters. A number, and a unit.",            # 12
    ("Anyone, anywhere, understands exactly the same length.", 0.6),  # 13
    ("Measurement is a number times a unit.", 0.8),                  # 14
    "Here is a challenge. Your friend says the road is five long.",  # 15
    ("What would you ask?", 1.2),                                    # 16
    "Next time: why does physics need only seven units?",            # 17
]

TABLE = 4.0     # table length in scene units; it stands for 2 meters


def build(scene, fmt, timeline):
    tl = timeline
    st = Stage(scene, fmt)
    st.headline(["What is"], "Measuring?", tag="Ch 1 • Measurement")
    st.subtitles(tl)

    # The table stays until the challenge.
    for width, height, x, z in ((TABLE, 0.18, 0, -0.09),
                                (0.16, 1.5, -1.7, -0.93),
                                (0.16, 1.5, 1.7, -0.93)):
        st.box(width, height, x, z, "blue", 0.0, tl.start(15))

    # 0-2: "two long... two what?"
    st.label("2", -0.5, 1.4, 1.5, "fg", tl.start(0) + 1.0, tl.start(3))
    st.label("?", 0.6, 1.4, 1.5, "amber", tl.start(1) + 0.2, tl.start(3))
    st.text("A number alone", -0.46, 0.07, "fg", tl.start(2), tl.start(3))
    st.text("tells us nothing", -0.55, 0.07, "pink", tl.start(2), tl.start(3))

    # 3-5: measuring is comparing with a chosen length
    st.text("MEASURE = COMPARE", -0.50, 0.075, "amber", tl.start(3),
            tl.start(5))
    for n, x in enumerate((-1.0, 1.0)):
        at = tl.start(4) + 0.4 + n * 1.9
        st.box(1.94, 0.18, x, 0.11, "amber", at, tl.start(6))
        st.label(str(n + 1), x, 0.85, 0.7, "amber", at + 0.2, tl.start(6))
    st.text("The chosen length", -0.46, 0.065, "fg", tl.start(5), tl.start(6))
    st.text("is called a UNIT", -0.55, 0.075, "amber", tl.start(5),
            tl.start(6))

    # 6-8: two hand spans, two different answers
    def count_blocks(n, row_z, color, sentence, text, text_x):
        width = TABLE / n
        first = tl.start(sentence) + 0.3
        step = (tl.end(sentence) - 0.5 - first) / (n - 1)
        for i in range(n):
            x = -TABLE / 2 + width * (i + 0.5)
            st.box(width - 0.05, 0.24, x, row_z, color, first + i * step,
                   tl.start(9))
        st.label(text, text_x, 1.35, 0.38, color, tl.end(sentence) - 0.3,
                 tl.start(9))

    count_blocks(10, 0.14, "cyan", 6, "10 spans", -1.15)
    count_blocks(8, 0.45, "pink", 7, "8 spans", 1.15)
    st.text("Same table,", -0.46, 0.07, "fg", tl.start(8), tl.start(9))
    st.text("different answers", -0.55, 0.07, "pink", tl.start(8),
            tl.start(9))

    # 9-11: one agreed standard, the meter
    st.text("One standard", -0.46, 0.07, "fg", tl.start(9), tl.start(11))
    st.text("for the whole world", -0.55, 0.07, "green", tl.start(9),
            tl.start(11))
    meter = st.box(1.94, 0.2, 0, 1.2, "green", tl.start(10))
    st.label("1 meter", 0, 1.8, 0.48, "green", tl.start(10) + 0.3,
             tl.start(12))
    for text, y, delay in (("✓  never changes", -0.46, 0.4),
                           ("✓  everyone can use it", -0.55, 2.2)):
        st.text(text, y, 0.06, "green", tl.start(11) + delay, tl.start(12),
                font="maths")

    # 12-13: the table is 2 meters, a number and a unit
    from bvid import scene as S
    S.move(meter, tl.start(12), tl.start(12) + 0.8, (-1.0, 0, 0.12), st.fps)
    st.show(meter, tl.start(10), tl.start(15))
    st.box(1.94, 0.2, 1.0, 0.12, "green", tl.start(12) + 0.9, tl.start(15))
    st.label("2", -0.45, 1.65, 1.3, "fg", tl.start(12) + 1.2, tl.start(15))
    st.label("m", 0.6, 1.65, 1.3, "green", tl.start(12) + 1.2, tl.start(15))
    half = tl.start(12) + 0.55 * (tl.end(12) - tl.start(12))
    st.label("number", -0.5, 0.8, 0.26, "fg", half, tl.start(15), font="body")
    st.label("unit", 0.6, 0.8, 0.26, "green", half + 0.9, tl.start(15),
             font="body")
    st.text("The same length,", -0.46, 0.065, "fg", tl.start(13), tl.start(14))
    st.text("anywhere in the world", -0.55, 0.065, "green", tl.start(13),
            tl.start(14))
    st.text("MEASUREMENT =", -0.45, 0.07, "fg", tl.start(14), tl.start(15))
    st.text("number × unit", -0.55, 0.09, "green", tl.start(14) + 0.3,
            tl.start(15), font="maths")

    # 15-17: challenge, then the hook for the next video
    st.text("CHALLENGE", 0.30, 0.06, "amber", tl.start(15), tl.start(17))
    st.text("“The road is", 0.12, 0.1, "fg", tl.start(15) + 1.6,
            tl.start(17))
    st.text("5 long.”", 0.0, 0.1, "fg", tl.start(15) + 1.6, tl.start(17))
    st.text("What would you ask?", -0.2, 0.075, "pink", tl.start(16),
            tl.start(17))
    st.text("NEXT", 0.2, 0.05, "muted", tl.start(17))
    st.text("Why only", 0.08, 0.1, "fg", tl.start(17) + 0.3)
    st.text("7 units?", -0.05, 0.14, "gold", tl.start(17) + 0.6, font="serif")
