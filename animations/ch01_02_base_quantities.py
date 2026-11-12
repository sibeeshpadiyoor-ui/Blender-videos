"""Chapter 1, video 2: Why only seven base quantities?

Script: scripts/ch01/02-seven-base-quantities.md
"""
from bvid.brand import SERIES, Stage

NARRATION = [
    "Speed. Force. Energy. Pressure.",                                 # 0
    "Physics has hundreds of quantities. "
    "Do we need a separate standard for each one?",                    # 1
    "No. We pick a few, and build all the others from them.",          # 2
    "These few are called base quantities. "
    "In 1971, the world agreed on seven.",                             # 3
    "Length, mass, and time.",                                         # 4
    "Electric current, temperature, amount of substance, "
    "and luminous intensity.",                                         # 5
    "Each one gets its own unit, and its own standard.",               # 6
    "Everything else is built from these. Speed is length divided by "
    "time, so it is measured in meters per second.",                   # 7
    "Power is built from three base units. One watt is one kilogram "
    "meter squared per second cubed.",                                 # 8
    "Seven base units. Every other unit is a combination of them.",    # 9
    "Challenge. Which of these is not a base quantity?",               # 10
    ("Length. Speed. Time. Mass.", 1.5),                               # 11
    "Next time: what is one meter, exactly?",                          # 12
]

QUANTITIES = [      # quantity, unit name, symbol, color
    ("Length", "meter", "m", "cyan"),
    ("Mass", "kilogram", "kg", "pink"),
    ("Time", "second", "s", "green"),
    ("Electric current", "ampere", "A", "amber"),
    ("Temperature", "kelvin", "K", "purple"),
    ("Amount of substance", "mole", "mol", "yellow"),
    ("Luminous intensity", "candela", "cd", "fg"),
]

CLOUD = ["Power", "Voltage", "Density", "Momentum", "Torque", "Frequency",
         "Charge", "Work", "Heat", "Acceleration", "Impulse", "Area",
         "Volume", "Resistance"]
ACCENTS = ["cyan", "pink", "amber", "green", "purple", "yellow"]


def build(scene, fmt, timeline):
    tl = timeline
    st = Stage(scene, fmt)
    st.headline(["Seven"], "Base Quantities",
                tag=f"{SERIES} • Ch 1 • 1-1 Measuring Things")
    st.subtitles(tl)

    def span(i):            # start and length of sentence i
        return tl.start(i), tl.end(i) - tl.start(i)

    # 0: four example quantities, one after another
    t0, d = span(0)
    for n, (word, color) in enumerate((("Speed", "cyan"), ("Force", "pink"),
                                       ("Energy", "amber"),
                                       ("Pressure", "green"))):
        st.label(word, 0, 1.9 - n * 1.0, 0.6, color,
                 t0 + d * (0.05 + 0.24 * n), tl.start(1) + 0.2)

    # 1: hundreds of quantities, and the question
    t1, d = span(1)
    for n, name in enumerate(CLOUD):
        col, row = n % 3, n // 3
        x = (-1.7, 0.0, 1.7)[col] + (0.15 if row % 2 else -0.15)
        st.label(name, x, 2.3 - row * 0.95, 0.28, ACCENTS[n % 6],
                 t1 + d * (0.05 + 0.5 * n / len(CLOUD)), tl.start(2))
    st.label("?", 0, -2.3, 1.1, "gold", t1 + d * 0.72, tl.start(2))

    # 2: pick a few, build the rest
    t2, d = span(2)
    st.text("PICK A FEW", -0.45, 0.075, "amber", t2 + d * 0.2, tl.start(4))
    st.text("BUILD THE REST", -0.55, 0.075, "green", t2 + d * 0.55,
            tl.start(4))
    for n in range(7):
        st.box(0.5, 0.5, -2.1 + n * 0.7, 0.6, QUANTITIES[n][3],
               t2 + d * (0.5 + 0.06 * n), tl.start(4))

    # 3: the number seven
    t3, d = span(3)
    st.label("7", 0, 1.9, 1.6, "gold", t3 + d * 0.5, tl.start(4),
             font="serif")
    st.label("1971", 0, -0.5, 0.34, "muted", t3 + d * 0.55, tl.start(4),
             font="body")

    # 4-6: the seven base quantities and their units
    def row_z(i):
        return 2.3 - 0.8 * i

    for i, (quantity, unit, symbol, color) in enumerate(QUANTITIES):
        z = row_z(i)
        if i < 3:
            t4, d4 = span(4)
            a = t4 + d4 * (0.05 + 0.3 * i)
        else:
            t5, d5 = span(5)
            a = t5 + d5 * (0.02 + 0.22 * (i - 3))
        gone = tl.start(7)
        st.box(0.12, 0.5, -2.55, z, color, a, gone)
        st.label(quantity, -2.35, z, 0.26, "fg", a, gone, font="body",
                 align="LEFT")
        st.label(unit, 0.6, z, 0.26, color, a + 0.15, gone, font="body",
                 align="LEFT")
        t6, d6 = span(6)
        st.label(symbol, 2.15, z, 0.34, color, t6 + d6 * (0.1 + 0.11 * i),
                 gone, align="RIGHT")

    # 7: speed = length / time
    t7, d = span(7)
    st.label("speed", -1.5, 0.95, 0.55, "amber", t7 + d * 0.28, tl.start(8))
    st.label("=", -0.45, 0.95, 0.55, "fg", t7 + d * 0.30, tl.start(8))
    st.label("length", 1.0, 1.65, 0.45, "cyan", t7 + d * 0.32, tl.start(8))
    st.box(2.0, 0.05, 1.0, 0.95, "fg", t7 + d * 0.40, tl.start(8))
    st.label("time", 1.0, 0.3, 0.45, "green", t7 + d * 0.45, tl.start(8))
    st.label("m / s", 0, -0.9, 0.9, "amber", t7 + d * 0.72, tl.start(8))
    st.label("meters per second", 0, -1.8, 0.3, "muted", t7 + d * 0.75,
             tl.start(8), font="body")

    # 8: a watt is made of three base units
    t8, d = span(8)
    st.label("POWER", 0, 2.2, 0.4, "amber", t8 + d * 0.05, tl.start(9))
    for n, (unit, color) in enumerate((("kg", "pink"), ("m", "cyan"),
                                        ("s", "green"))):
        x = (-1.5, 0.0, 1.5)[n]
        st.box(1.1, 1.1, x, 0.9, color, t8 + d * (0.2 + 0.08 * n),
               tl.start(9))
        st.label(unit, x, 0.72, 0.55, "bg", t8 + d * (0.2 + 0.08 * n),
                 tl.start(9), front=0.1)
    st.label("1 W = 1 kg · m² / s³", 0, -0.6, 0.42, "fg",
             t8 + d * 0.5, tl.start(9), font="maths")

    # 9: seven base units, every other unit a combination
    t9, d = span(9)
    st.label("7", -1.4, 0.7, 2.6, "gold", t9 + d * 0.05, tl.start(10),
             font="serif")
    st.label("base units", -1.4, -0.7, 0.34, "fg", t9 + d * 0.1,
             tl.start(10), font="body")
    for n, (word, color) in enumerate((("speed", "cyan"), ("force", "pink"),
                                       ("energy", "amber"),
                                       ("power", "green"),
                                       ("pressure", "purple"))):
        st.label(word, 1.5, 1.8 - n * 0.6, 0.32, color,
                 t9 + d * (0.45 + 0.09 * n), tl.start(10))
    st.label("every other unit", 1.5, -1.4, 0.28, "muted", t9 + d * 0.85,
             tl.start(10), font="body")

    # 10-11: challenge
    t10, d = span(10)
    st.label("CHALLENGE", 0, 2.4, 0.36, "amber", t10, tl.start(12))
    st.label("Which is NOT a base quantity?", 0, 1.6, 0.3, "fg",
             t10 + d * 0.3, tl.start(12), font="body")
    t11, d = span(11)
    for n, (letter, word) in enumerate((("A", "Length"), ("B", "Speed"),
                                         ("C", "Time"), ("D", "Mass"))):
        st.label(f"{letter}   {word}", -1.1, 0.6 - 0.9 * n, 0.5, "fg",
                 t11 + d * (0.05 + 0.24 * n), tl.start(12), align="LEFT")

    # 12: what comes next
    t12 = tl.start(12)
    st.label("NEXT", 0, 0.8, 0.28, "muted", t12 + 0.3, font="body")
    st.label("What is", 0, 0.0, 0.55, "fg", t12 + 0.6)
    st.label("one meter?", 0, -1.0, 0.8, "gold", t12 + 1.0, font="serif")
