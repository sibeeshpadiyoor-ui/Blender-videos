"""Chapter 1, video 1: What does it mean to measure?

Script: scripts/ch01/01-what-is-measurement.md
Visuals are cued to the start of each narration sentence.
"""
from bvid import scene as S

NARRATION = [
    "This table is two long.",                                       # 0
    "Two... what?",                                                  # 1
    "A number alone tells us nothing.",                              # 2
    "To measure means to compare.",                                  # 3
    "We choose one length, and count how many times it fits.",       # 4
    "That chosen length is called a unit. But which unit?",          # 5
    "With my hand span, the table is ten spans long.",               # 6
    "My friend has a bigger hand, and gets only eight.",             # 7
    "Same table, two different answers.",                            # 8
    "So the whole world agrees on one standard for each unit.",      # 9
    "For length, it is the meter.",                                  # 10
    "A good standard never changes, and everyone can use it.",       # 11
    "Now the table is two meters. A number, and a unit.",            # 12
    "Anyone, anywhere, understands exactly the same length.",        # 13
    "Measurement is a number times a unit.",                         # 14
    "Next: why does physics need only seven base units?",            # 15
]

BACKGROUND = (0.006, 0.008, 0.02)
WHITE = (1.0, 1.0, 1.0)
GREY = (0.3, 0.33, 0.4)
WOOD = (0.45, 0.2, 0.06)
YELLOW = (1.0, 0.65, 0.02)
BLUE = (0.1, 0.4, 1.0)
ORANGE = (1.0, 0.3, 0.05)
GREEN = (0.1, 0.9, 0.2)

TABLE = 4.0     # table length in scene units; it stands for 2 meters


def build(scene, fmt, timeline):
    fps = fmt.fps
    tl = timeline
    S.flat_style(scene)
    S.set_background(scene, BACKGROUND)
    S.add_camera(scene, fmt, target=(0, 0, 0), direction=(0, -1, 0),
                 half_width=2.4, half_height=2.4 * 16 / 9, margin=1.1)

    mat = {name: S.emissive(name, color) for name, color in dict(
        white=WHITE, grey=GREY, wood=WOOD, yellow=YELLOW, blue=BLUE,
        orange=ORANGE, green=GREEN).items()}

    def shown(obj, start, end=None):
        S.show(obj, start, end, fps)
        return obj

    def label(text, x, z, size, color, start, end=None):
        return shown(S.add_world_text(text, (x, 0, z), size, mat[color]),
                     start, end)

    column = min(1.0, (9 / 16) / fmt.aspect)

    def caption(text, y, size, color, start, end=None):
        return shown(S.add_screen_text(scene, fmt, text, 0, y, size * column,
                                       mat[color]), start, end)

    # Always on screen
    caption("PHYSICS  •  MEASUREMENT", 0.92, 0.03, "grey", 0.1)
    caption("What is measuring?", 0.83, 0.075, "white", 0.2)
    S.add_box(TABLE, 0.16, (0, 0, -0.08), mat["wood"])
    for x in (-1.7, 1.7):
        S.add_box(0.14, 1.5, (x, 0, -0.91), mat["wood"])

    # 0-2: "two long... two what?"
    label("2", -0.45, 1.3, 1.3, "white", tl.start(0) + 1.0, tl.start(3))
    label("?", 0.55, 1.3, 1.3, "yellow", tl.start(1) + 0.2, tl.start(3))
    caption("A number alone", -0.50, 0.06, "white", tl.start(2), tl.start(3))
    caption("tells us nothing", -0.58, 0.06, "white", tl.start(2), tl.start(3))

    # 3-5: measuring is comparing with a chosen length
    caption("Measure = compare", -0.52, 0.08, "yellow", tl.start(3),
            tl.start(5))
    for n, x in enumerate((-1.0, 1.0)):
        at = tl.start(4) + 0.3 + n * 1.6
        shown(S.add_box(1.94, 0.16, (x, 0, 0.1), mat["yellow"]), at,
              tl.start(6))
        label(str(n + 1), x, 0.75, 0.6, "yellow", at + 0.2, tl.start(6))
    caption("The chosen length", -0.50, 0.06, "white", tl.start(5),
            tl.start(6))
    caption("is called a unit", -0.58, 0.06, "yellow", tl.start(5),
            tl.start(6))

    # 6-8: two hand spans, two different answers
    def count_blocks(n, row_z, color, sentence, text, text_x):
        width = TABLE / n
        first = tl.start(sentence) + 0.2
        step = (tl.end(sentence) - 0.6 - first) / (n - 1)
        for i in range(n):
            x = -TABLE / 2 + width * (i + 0.5)
            shown(S.add_box(width - 0.05, 0.22, (x, 0, row_z), mat[color]),
                  first + i * step, tl.start(9))
        label(text, text_x, 1.25, 0.34, color, tl.end(sentence) - 0.4,
              tl.start(9))

    count_blocks(10, 0.13, "blue", 6, "10 spans", -1.15)
    count_blocks(8, 0.42, "orange", 7, "8 spans", 1.15)
    caption("Same table,", -0.50, 0.065, "white", tl.start(8), tl.start(9))
    caption("different answers", -0.58, 0.065, "white", tl.start(8),
            tl.start(9))

    # 9-11: one agreed standard, the meter
    caption("One standard", -0.50, 0.065, "white", tl.start(9), tl.start(11))
    caption("for the whole world", -0.58, 0.065, "white", tl.start(9),
            tl.start(11))
    meter = shown(S.add_box(1.94, 0.18, (0, 0, 1.2), mat["green"]),
                  tl.start(10))
    label("1 meter", 0, 1.75, 0.42, "green", tl.start(10) + 0.3, tl.start(12))
    caption("✓  never changes", -0.50, 0.06, "green", tl.start(11) + 0.3,
            tl.start(12))
    caption("✓  everyone can use it", -0.60, 0.06, "green",
            tl.start(11) + 1.9, tl.start(12))

    # 12-13: the table is 2 meters, a number and a unit
    S.move(meter, tl.start(12), tl.start(12) + 0.8, (-1.0, 0, 0.11), fps)
    shown(S.add_box(1.94, 0.18, (1.0, 0, 0.11), mat["green"]),
          tl.start(12) + 0.9)
    label("2", -0.4, 1.55, 1.1, "white", tl.start(12) + 1.2)
    label("m", 0.5, 1.55, 1.1, "green", tl.start(12) + 1.2)
    half = tl.start(12) + 0.55 * (tl.end(12) - tl.start(12))
    label("number", -0.45, 0.8, 0.24, "white", half)
    label("unit", 0.5, 0.8, 0.24, "green", half + 0.8)
    caption("The same length,", -0.50, 0.06, "white", tl.start(13),
            tl.start(14))
    caption("anywhere in the world", -0.58, 0.06, "white", tl.start(13),
            tl.start(14))

    # 14-15: summary and what comes next
    caption("Measurement =", -0.48, 0.07, "white", tl.start(14))
    caption("number × unit", -0.58, 0.09, "green", tl.start(14) + 0.3)
    caption("Next: the 7 base units", -0.76, 0.045, "grey",
            tl.start(15) + 0.2)
