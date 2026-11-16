"""3D model of the mutual induction + jumping ring kit, on a slow turntable.

The model is full size (metres). Circuit and values are in
kits/induction_kit/circuit.svg. Labelled stills come from
kits/induction_kit/render_views.py; this file also works with render.py:

    python render.py induction_kit --format youtube --quality preview --save-blend
"""
import math

import bpy

from bvid import scene as S
from bvid.model import ball, box, cable, empty, rod, tube

SECONDS = 8.0           # one full turn of the camera

# Sizes in metres.
BASE = (0.46, 0.28, 0.018)
TOP = BASE[2]                       # height of the base board's top face
CORE_XY = (-0.10, 0.03)
CORE_R, CORE_LEN = 0.013, 0.30
RING_IN, RING_OUT = 0.014, 0.021    # rings: 28 mm bore, 42 mm outside

# Coils: flange radius, winding radius, height.
L1 = dict(flange=0.045, winding=0.038, height=0.060)    # 300 turns, 1.2 mm
L2 = dict(flange=0.034, winding=0.028, height=0.030)    # 150 turns, 0.5 mm
L3 = dict(flange=0.036, winding=0.030, height=0.035)    # 300 turns, 0.4 mm
L4 = dict(flange=0.040, winding=0.035, height=0.045)    # 600 turns, 0.4 mm
L5 = dict(flange=0.030, winding=0.024, height=0.022)    # LED coil, 80 turns

SEG = 64


def materials():
    m = S.material
    copper = m("EnamelledCopper", (0.72, 0.27, 0.08), 0.35, metallic=0.9)
    # Fine horizontal banding so the windings read as wound wire.
    nodes, links = copper.node_tree.nodes, copper.node_tree.links
    coords = nodes.new("ShaderNodeTexCoord")
    wave = nodes.new("ShaderNodeTexWave")
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 90.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    bump.inputs["Distance"].default_value = 0.001
    links.new(coords.outputs["Object"], wave.inputs["Vector"])
    links.new(wave.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"],
              nodes["Principled BSDF"].inputs["Normal"])
    return {
        "wood": m("Wood", (0.50, 0.30, 0.13), 0.55),
        "copper": copper,
        "bobbin": m("Bobbin", (0.03, 0.03, 0.035), 0.4),
        "core": m("Core", (0.22, 0.22, 0.24), 0.45, metallic=0.8),
        "alu": m("Aluminium", (0.82, 0.83, 0.85), 0.3, metallic=1.0),
        "cu": m("CopperRing", (0.9, 0.45, 0.25), 0.3, metallic=1.0),
        "white": m("WhitePlastic", (0.85, 0.85, 0.82), 0.4),
        "red": m("Red", (0.75, 0.03, 0.03), 0.35),
        "black": m("Black", (0.02, 0.02, 0.02), 0.4),
        "yellow": m("Yellow", (0.95, 0.65, 0.02), 0.4),
        "case": m("SupplyCase", (0.25, 0.33, 0.42), 0.5),
        "brass": m("Brass", (0.8, 0.6, 0.25), 0.3, metallic=1.0),
        "dial": m("Dial", (0.9, 0.9, 0.86), 0.6),
        "lcd": m("Display", (0.55, 0.62, 0.52), 0.3),
        "cell": m("Cell", (0.05, 0.12, 0.45), 0.35),
        "bulb": S.emissive("BulbGlow", (1.0, 0.75, 0.35), 12.0),
        "led_r": S.emissive("LedRed", (1.0, 0.1, 0.05), 6.0),
        "led_g": S.emissive("LedGreen", (0.1, 1.0, 0.2), 6.0),
    }


def cyl(name, x, y, z0, z1, radius, mat, parent=None):
    return rod(name, (x, y, z0), (x, y, z1), radius, mat, parent, segments=SEG)


def coil(name, spec, location, m):
    """A wound bobbin with its base at `location`; returns its parent empty,
    so the whole coil can be moved as one piece in Blender."""
    root = empty(name, location=location)
    h, t = spec["height"], 0.003
    cyl(name + "Winding", 0, 0, t, h - t, spec["winding"], m["copper"], root)
    for z in (0, h - t):
        tube(name + "Flange", CORE_R + 0.001, spec["flange"], t, (0, 0, z),
             m["bobbin"], root)
    return root


def sockets(parent, radius, z, mat, spread=0.009):
    for sy in (-1, 1):
        cyl("Socket", radius, sy * spread, z, z + 0.008, 0.0045, mat, parent)


def lead(name, start, end, mat, m, lift=0.07):
    """A test lead with banana plugs, arcing from `start` down to `end`."""
    (x0, y0, z0), (x1, y1, z1) = start, end
    for x, y, z in (start, end):
        cyl(name + "Plug", x, y, z, z + 0.03, 0.005, mat)
    top = max(z0, z1) + lift
    cable(name, [(x0, y0, z0 + 0.03), (x0, y0, z0 + 0.06),
                 (x0 + (x1 - x0) * 0.3, y0 + (y1 - y0) * 0.3, top),
                 (x0 + (x1 - x0) * 0.75, y0 + (y1 - y0) * 0.75, top - 0.01),
                 (x1, y1, z1 + 0.06), (x1, y1, z1 + 0.03)], 0.0022, mat)


def build_kit(m):
    """Builds every part; returns {label: point to aim a callout at}."""
    cx, cy = CORE_XY
    parts = {}

    box("Base", BASE, (0, 0, TOP / 2), m["wood"])
    parts["Base board"] = (-0.215, -0.13, TOP)

    # Core and primary.
    cyl("Core", cx, cy, TOP, TOP + CORE_LEN, CORE_R, m["core"])
    parts["Soft-iron core, 25 x 300 mm"] = (cx, cy, TOP + CORE_LEN - 0.02)
    coil("L1_Primary", L1, (cx, cy, TOP), m)
    parts["L1 primary, 300 turns"] = (cx, cy - L1["winding"], TOP + 0.03)

    # Bulb coil resting on the primary, bulb mounted on its top flange.
    z2 = TOP + L1["height"] + 0.001
    l2 = coil("L2_BulbCoil", L2, (cx, cy, z2), m)
    arm = L2["flange"] + 0.010
    box("BulbTab", (0.020, 0.018, 0.003), (arm - 0.001, 0, L2["height"] - 0.0015),
        m["bobbin"], l2)
    cyl("BulbHolder", arm, 0, L2["height"], L2["height"] + 0.014, 0.0075,
        m["brass"], l2)
    ball("Bulb", (0.011, 0.011, 0.013), (arm, 0, L2["height"] + 0.024),
         m["bulb"], l2)
    for sx in (-0.009, 0.009):       # sockets for a meter, at the front
        cyl("Socket", sx, -(L2["flange"] - 0.008), L2["height"],
            L2["height"] + 0.008, 0.0045, m["yellow"], l2)
    parts["L2 bulb coil, 150 turns, 6 V bulb"] = (cx + arm, cy, z2 + L2["height"] + 0.024)

    # Supply input sockets and the push-to-on switch.
    for y, mat in ((-0.02, m["red"]), (0.02, m["black"])):
        cyl("InputCollar", -0.205, y, TOP, TOP + 0.004, 0.009, m["bobbin"])
        cyl("InputSocket", -0.205, y, TOP, TOP + 0.010, 0.006, mat)
    parts["24 V input sockets"] = (-0.205, -0.02, TOP + 0.01)
    cyl("SwitchBody", -0.17, -0.09, TOP, TOP + 0.014, 0.019, m["black"])
    cyl("SwitchButton", -0.17, -0.09, TOP + 0.014, TOP + 0.024, 0.013, m["red"])
    parts["S1 push-to-on switch"] = (-0.17, -0.09, TOP + 0.024)

    # Spare coils parked on pegs.
    for name, spec, x in (("L3_300turns", L3, 0.03), ("L4_600turns", L4, 0.115),
                          ("L5_LedCoil", L5, 0.195)):
        cyl(name + "Peg", x, 0.06, TOP, TOP + spec["height"] + 0.012,
            CORE_R - 0.001, m["black"])
        c = coil(name, spec, (x, 0.06, TOP), m)
        if spec is L5:
            for sy, mat in ((-1, m["led_r"]), (1, m["led_g"])):
                ball("Led", (0.004, 0.004, 0.005),
                     (0.022, sy * 0.008, spec["height"] + 0.004), mat, c)
        else:
            sockets(c, spec["flange"] - 0.008, spec["height"], m["yellow"])
    parts["L3 300 turns"] = (0.03, 0.06 - L3["winding"], TOP + 0.02)
    parts["L4 600 turns"] = (0.115, 0.06 - L4["winding"], TOP + 0.025)
    parts["LED coil"] = (0.195, 0.06 - L5["winding"], TOP + 0.012)

    # Rings, laid out along the front edge.
    rings = [("RingAluminium", m["alu"], 0.012, 0.0, "Aluminium ring"),
             ("RingSplit", m["alu"], 0.012, 0.35, "Split ring"),
             ("RingCopper", m["cu"], 0.012, 0.0, "Copper ring"),
             ("RingPlastic", m["white"], 0.012, 0.0, "Plastic ring"),
             ("RingTall", m["alu"], 0.025, 0.0, "Tall aluminium ring")]
    for i, (name, mat, height, gap, label) in enumerate(rings):
        x = 0.01 + i * 0.048
        ring = tube(name, RING_IN, RING_OUT, height, (x, -0.085, TOP), mat, gap=gap)
        ring.rotation_euler = (0, 0, -math.pi / 2)      # slot faces the front
        parts[label] = (x, -0.085 - RING_OUT, TOP + height)

    # Supply box, with leads across to the base.
    sx, sy, sh = -0.39, 0.02, 0.09
    box("SupplyBox", (0.15, 0.20, sh), (sx, sy, sh / 2), m["case"])
    box("SupplyLabel", (0.07, 0.05, 0.001), (sx - 0.02, sy + 0.04, sh), m["dial"])
    cyl("FuseHolder", sx - 0.01, sy - 0.06, sh, sh + 0.008, 0.008, m["black"])
    ball("PowerLamp", (0.005, 0.005, 0.004), (sx - 0.045, sy - 0.06, sh + 0.002),
         m["led_g"])
    for y, mat in ((-0.02, m["red"]), (0.02, m["black"])):
        cyl("SupplySocket", sx + 0.05, y, sh, sh + 0.008, 0.006, mat)
        lead("SupplyLead", (sx + 0.05, y, sh + 0.004), (-0.205, y, TOP + 0.006),
             mat, m)
    cable("MainsCable", [(sx, sy + 0.10, 0.03), (sx, sy + 0.16, 0.012),
                         (sx - 0.05, sy + 0.30, 0.004), (sx - 0.25, sy + 0.45, 0.004),
                         (sx - 0.6, sy + 0.5, 0.004)], 0.004, m["black"])
    parts["Supply box: isolating transformer, 24 V AC"] = (sx, sy - 0.10, sh * 0.6)

    # Multimeter in front of the base.
    mm = empty("Multimeter", location=(0.11, -0.24, 0))
    mm.rotation_euler = (0, 0, math.radians(-12))
    box("Body", (0.078, 0.15, 0.034), (0, 0, 0.017), m["yellow"], mm)
    box("Face", (0.064, 0.135, 0.002), (0, 0, 0.035), m["black"], mm)
    box("Display", (0.05, 0.026, 0.002), (0, 0.045, 0.0365), m["lcd"], mm)
    cyl("Dial", 0, -0.012, 0.035, 0.044, 0.02, m["bobbin"], mm)
    box("DialMark", (0.004, 0.03, 0.002), (0, -0.012, 0.045), m["dial"], mm)
    parts["Multimeter (AC volts)"] = (0.11, -0.24, 0.04)

    # Galvanometer, cell and tap key for the make-and-break experiment.
    g = empty("Galvanometer", location=(0.33, 0.05, 0))
    box("Body", (0.11, 0.055, 0.10), (0, 0, 0.05), m["black"], g)
    box("Face", (0.095, 0.002, 0.06), (0, -0.0285, 0.06), m["dial"], g)
    pivot = empty("NeedlePivot", g, (0, -0.030, 0.036))    # turn about Y
    box("Needle", (0.0015, 0.001, 0.045), (0, 0, 0.0225), m["red"], pivot)
    for x, mat in ((-0.03, m["red"]), (0.03, m["black"])):
        cyl("Terminal", x, 0, 0.10, 0.11, 0.006, mat, g)
    parts["Galvanometer"] = (0.33, 0.05 - 0.03, 0.09)

    # D cell on its side: dark body, copper band and raised cap at the + end.
    cy_, cz, cr = -0.09, 0.0165, 0.0165
    cell = rod("Cell_1V5", (0.295, cy_, cz), (0.341, cy_, cz), cr, m["black"],
               segments=SEG)
    rod("CellBand", (0.341, cy_, cz), (0.353, cy_, cz), cr, m["cu"], segments=SEG)
    rod("CellCap", (0.353, cy_, cz), (0.358, cy_, cz), 0.0055, m["alu"],
        segments=24)
    rod("CellBase", (0.2935, cy_, cz), (0.295, cy_, cz), cr * 0.8, m["alu"],
        segments=24)
    tilt = math.radians(50)            # labels face the viewer, up the curve
    for text, x, size in (("\u2212", 0.301, 0.014), ("1.5 V", 0.320, 0.011),
                          ("+", 0.347, 0.014)):
        bpy.ops.object.text_add()
        label = bpy.context.object
        label.name = "CellLabel"
        label.data.body = text
        label.data.align_x = label.data.align_y = "CENTER"
        label.data.size = size
        label.data.extrude = 0.0003
        label.data.materials.append(m["black"] if text == "+" else m["dial"])
        r = cr + 0.0004
        label.location = (x, cy_ - r * math.sin(tilt), cz + r * math.cos(tilt))
        label.rotation_euler = (tilt, 0, 0)
    k = empty("TapKey", location=(0.325, -0.19, 0))
    box("Plate", (0.035, 0.08, 0.008), (0, 0, 0.004), m["black"], k)
    arm = empty("KeyArm", k, (0, 0.036, 0.012))      # turn about X to press
    box("Strip", (0.01, 0.065, 0.0015), (0, -0.032, 0.004), m["brass"], arm,
        rotation=(math.radians(-9), 0, 0))
    cyl("Knob", 0, -0.062, 0.008, 0.020, 0.008, m["black"], arm)
    cyl("Contact", 0, -0.026, 0.008, 0.011, 0.004, m["brass"], k)
    parts["1.5 V cell and tap key"] = (0.325, -0.14, 0.02)
    return parts


def light(scene):
    S.set_background(scene, (0.8, 0.84, 0.9), 0.25)
    S.add_floor((0.42, 0.44, 0.47), size=30.0)
    S.add_area_light((-0.6, -0.9, 1.1), 60, size=0.9, target=(0, 0, 0.08))
    S.add_area_light((0.9, -0.3, 0.7), 12, size=0.8, target=(0, 0, 0.08))
    S.add_area_light((0.1, 0.8, 0.8), 12, size=0.8, target=(0, 0, 0.08))
    scene.cycles.max_bounces = 4


def build(scene, fmt):
    light(scene)
    parts = build_kit(materials())

    target = (-0.04, -0.06, 0.09)
    cam = S.add_camera(scene, fmt, target=target, direction=(0, -1, 0.62),
                       half_width=0.56, half_height=0.34, lens=70)
    cam.data.clip_start = 0.02
    pivot = empty("Turntable", location=target)
    cam.parent = pivot
    cam.matrix_parent_inverse = pivot.matrix_world.inverted()
    for frame in range(scene.frame_start, scene.frame_end + 2):
        turn = (frame - 1) / scene.frame_end
        S.key(pivot, frame, rotation_euler=(0, 0, math.tau * turn))
    return parts
