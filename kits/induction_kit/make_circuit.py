#!/usr/bin/env python3
"""Draw the circuit diagram for the mutual induction / jumping ring kit.

    python kits/induction_kit/make_circuit.py

Writes circuit.svg next to this file.
"""
from pathlib import Path

W, H = 1400, 960
out = []


def add(s):
    out.append(s)


def line(*pts, **kw):
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    add(f'<path d="{d}" class="w"{extra}/>')


def text(x, y, s, size=15, anchor="start", weight="normal", fill="#222"):
    add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
        f'font-weight="{weight}" fill="{fill}">{s}</text>')


def lines(x, y, rows, size=13, anchor="start", gap=17, fill="#444"):
    for i, row in enumerate(rows):
        text(x, y + i * gap, row, size, anchor, fill=fill)


def coil(x, y0, n=7, r=10, side=1):
    """Vertical coil starting at (x, y0); bumps face right for side=1."""
    sweep = 1 if side > 0 else 0
    d = f"M{x},{y0}" + f" a{r},{r} 0 0 {sweep} 0,{2 * r}" * n
    add(f'<path d="{d}" class="w"/>')
    return y0 + 2 * r * n


def core(x, y0, y1):
    for dx in (0, 8):
        add(f'<path d="M{x + dx},{y0} L{x + dx},{y1}" class="core"/>')


def dot(x, y):
    add(f'<circle cx="{x}" cy="{y}" r="5" class="term"/>')


def fuse(x, y, label, sub):
    add(f'<rect x="{x}" y="{y - 9}" width="60" height="18" class="part"/>')
    line((x, y), (x + 60, y))
    text(x + 30, y - 20, label, 14, "middle", "bold")
    text(x + 30, y + 28, sub, 13, "middle", fill="#444")


def meter(x, y, letter):
    add(f'<circle cx="{x}" cy="{y}" r="22" class="part"/>')
    text(x, y + 7, letter, 20, "middle", "bold")


def bulb(x, y):
    add(f'<circle cx="{x}" cy="{y}" r="22" class="part"/>')
    line((x - 15, y - 15), (x + 15, y + 15))
    line((x - 15, y + 15), (x + 15, y - 15))


def led(x, y, down=True):
    s = 1 if down else -1
    add(f'<path d="M{x - 11},{y - 9 * s} L{x + 11},{y - 9 * s} L{x},{y + 9 * s} Z" '
        f'class="part"/>')
    line((x - 11, y + 9 * s), (x + 11, y + 9 * s))


add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f'width="{W}" height="{H}" font-family="DejaVu Sans, Arial, sans-serif">')
add("""<style>
.w{fill:none;stroke:#222;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
.core{fill:none;stroke:#8a5a2b;stroke-width:3.5;stroke-linecap:round}
.part{fill:#fff;stroke:#222;stroke-width:2.5;stroke-linejoin:round}
.term{fill:#fff;stroke:#c0392b;stroke-width:3}
.box{fill:#f6f3ea;stroke:#8a7f66;stroke-width:2;stroke-dasharray:9 6}
.panel{fill:#f7f9fb;stroke:#b9c3cf;stroke-width:1.5}
.ring{fill:none;stroke:#7d8791;stroke-width:9}
</style>""")
add(f'<rect width="{W}" height="{H}" fill="#fff"/>')
text(40, 44, "Mutual induction + jumping ring kit: circuit diagram", 26,
     weight="bold")
text(40, 68, "All values are calculated starting points. Confirm them on the "
     "prototype before winding a batch.", 14, fill="#555")

# ---- Supply box ------------------------------------------------------------
add('<rect x="40" y="92" width="476" height="380" rx="10" class="box"/>')
text(56, 116, "SUPPLY BOX (closed, no student access)", 14, weight="bold",
     fill="#6b6046")
top, bot = 180, 380
dot(76, top), dot(76, bot)
text(76, top - 16, "L", 15, "middle", "bold")
text(76, bot + 28, "N", 15, "middle", "bold")
lines(98, 272, ["230 V AC", "mains"], 15, gap=20, fill="#222")
line((81, top), (140, top))
fuse(140, top, "F1", "1 A")
line((200, top), (300, top), (300, 210))
end = coil(300, 210, side=1)
line((300, end), (300, bot), (81, bot))
core(322, 205, end + 5)
coil(352, 210, side=-1)
line((352, 210), (352, top), (400, top))
fuse(400, top, "F2", "8 A slow-blow")
line((460, top), (511, top))
line((352, end), (352, bot), (511, bot))
lines(326, 410, ["T1 isolating transformer", "230 V : 24 V, 150-200 VA"], 14,
      "middle", 19, "#222")
dot(516, top), dot(516, bot)
lines(532, 268, ["24 V AC", "4 mm shrouded", "sockets"], 14, gap=19, fill="#222")

# ---- Bench circuit ---------------------------------------------------------
line((521, top), (600, top))
line((660, top), (720, top))
add(f'<circle cx="600" cy="{top}" r="4" class="part"/>')
add(f'<circle cx="660" cy="{top}" r="4" class="part"/>')
line((604, top - 13), (656, top - 13))
line((630, top - 13), (630, top - 30))
line((620, top - 30), (640, top - 30))
lines(630, top - 62, ["S1", "push-to-on"], 14, "middle", 17, "#222")
add(f'<rect x="720" y="{top - 10}" width="60" height="20" class="part"/>')
text(750, top + 5, "t°", 14, "middle")
lines(750, top + 32, ["TH thermal cut-out", "fixed on L1"], 13, "middle")
line((780, top), (860, top), (860, 210))
end = coil(860, 210, side=1)
line((860, end), (860, bot), (521, bot))
lines(842, 262, ["L1 primary", "300 turns", "1.2 mm wire"], 14, "end", 19, "#222")
core(884, 130, 430)
lines(888, 108, ["soft-iron core, 25 mm x 300 mm"], 14, "middle", fill="#8a5a2b")
coil(916, 210, side=-1)
line((916, 210), (916, top), (1130, top), (1130, 258))
bulb(1130, 280)
line((1130, 302), (1130, bot), (916, bot), (916, end))
line((916, 310), (985, 310))
dot(990, 310)
text(1002, 315, "tap: 100 turns", 13, fill="#444")
lines(940, 238, ["L2 bulb coil", "150 turns, 0.5 mm wire"], 14, gap=19, fill="#222")
lines(1166, 268, ["6 V bulb, 0.3-0.5 A", "mounted on the bobbin"], 14, gap=19,
      fill="#222")
lines(940, 420, ["L2 slides on the core: brightest resting on L1,",
                 "dimmer as it is raised."], 13)

# ---- Swap-in panels --------------------------------------------------------
text(40, 524, "Swap these in place of L2", 19, weight="bold")
PW, PY, PH = 256, 544, 370


def panel(i, title):
    px = 40 + i * 268
    add(f'<rect x="{px}" y="{PY}" width="{PW}" height="{PH}" rx="10" class="panel"/>')
    text(px + 14, PY + 28, title, 15, weight="bold")
    return px


def loop(px, y0=620):
    """Core, a secondary coil and a wire loop out to the right branch."""
    core(px + 30, y0 - 25, y0 + 185)
    end = coil(px + 60, y0 + 10, side=-1)
    return px + 190, y0, end + 10


# A: measuring coils
px = panel(0, "A. Measuring coils")
x, y0, y1 = loop(px)
line((px + 60, y0 + 10), (px + 60, y0), (x, y0), (x, 688))
meter(x, 710, "V")
line((x, 732), (x, y1), (px + 60, y1), (px + 60, y1 - 10))
lines(px + 14, 840, ["L3 300 turns, L4 600 turns,", "0.4 mm wire.",
                     "Multimeter on AC volts.", "Ideal 24 V and 48 V; real lower."])

# B: LED coil
px = panel(1, "B. LED coil")
x, y0, y1 = loop(px)
line((px + 60, y0 + 10), (px + 60, y0), (px + 100, y0))
add(f'<rect x="{px + 100}" y="{y0 - 9}" width="50" height="18" class="part"/>')
text(px + 125, y0 - 16, "100 Ω", 13, "middle")
line((px + 150, y0), (px + 220, y0))
for bx, down in ((px + 180, True), (px + 220, False)):
    line((bx, y0), (bx, 701))
    led(bx, 710, down)
    line((bx, 719), (bx, y1))
line((px + 220, y1), (px + 60, y1), (px + 60, y1 - 10))
lines(px + 14, 840, ["60-100 turns, 0.4 mm wire.", "Two LEDs back to back.",
                     "Lights even held well above L1."])

# C: jumping ring
px = panel(2, "C. Jumping ring")
core(px + 124, 595, 805)
add(f'<path d="M{px + 73},668 a55,15 0 0 0 110,0" class="ring"/>')
add(f'<path d="M{px + 73},758 a55,15 0 0 0 46,14" class="ring"/>')
add(f'<path d="M{px + 139},772 a55,15 0 0 0 44,-14" class="ring"/>')
text(px + 196, 664, "whole", 13)
text(px + 196, 754, "split", 13)
lines(px + 14, 840, ["Aluminium ring = one shorted turn.",
                     "Induced current repels it from L1.",
                     "Split ring: no current, no jump."])

# D: make and break
px = panel(3, "D. Make and break (DC)")
bx, lx = px + 28, px + 96
line((bx, 620), (bx, 702))
line((bx - 14, 702), (bx + 14, 702))
add(f'<path d="M{bx - 7},714 L{bx + 7},714" class="w" stroke-width="5"/>')
line((bx, 714), (bx, 800), (lx, 800), (lx, 780))
line((bx, 620), (px + 44, 620))
line((px + 44, 620), (px + 72, 606))
add(f'<circle cx="{px + 44}" cy="620" r="4" class="part"/>')
add(f'<circle cx="{px + 76}" cy="620" r="4" class="part"/>')
text(px + 60, 598, "K", 14, "middle", "bold")
line((px + 80, 620), (lx, 620), (lx, 640))
coil(lx, 640, side=1)
core(px + 118, 600, 805)
coil(px + 148, 640, side=-1)
gx = px + 212
line((px + 148, 640), (px + 148, 620), (gx, 620), (gx, 688))
meter(gx, 710, "G")
line((gx, 732), (gx, 800), (px + 148, 800), (px + 148, 780))
text(bx + 20, 712, "1.5 V", 12)
text(lx - 6, 824, "L1", 12, "end")
text(px + 154, 824, "L4", 12)
lines(px + 14, 846, ["1.5 V D cell and tap key K replace",
                     "the 24 V supply. Centre-zero",
                     "galvanometer: kicks at ON and OFF."])

# E: notes
px = panel(4, "Notes")
lines(px + 14, PY + 58, [
    "Primary circuit is one series",
    "loop: T1, F2, S1, TH, L1.",
    "",
    "S1 is momentary, so L1 is only",
    "powered while it is pressed.",
    "",
    "Secondaries have no electrical",
    "connection to the supply; they",
    "are linked only by the core.",
    "",
    "Use only L1 as the primary.",
    "Never feed 24 V into L3 or L4.",
    "",
    "Brown double line = iron core.",
    "Red circles = 4 mm sockets."], 13, gap=18)
add("</svg>")
Path(__file__).with_name("circuit.svg").write_text("\n".join(out))
