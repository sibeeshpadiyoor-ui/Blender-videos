"""Induction kit, video 1: the bulb with no battery.

Script: scripts/induction_kit/01-mutual-induction-and-jumping-ring.md
Model:  animations/induction_kit.py
Every action is cued to the start of a narration sentence.

    python render.py induction_kit_video --format youtube --quality preview
"""
import math

import bpy
from mathutils import Vector

from animations import induction_kit as kit
from bvid import scene as S
from bvid.model import box, cable, empty

NARRATION = [
    "This bulb has no battery.",                                          # 0
    "No wire joins it to the supply.",                                    # 1
    "So why is it glowing?",                                              # 2
    "The lower coil carries alternating current, which goes back and "
    "forth fifty times a second.",                                        # 3
    "So its magnetic field keeps growing, shrinking and reversing.",      # 4
    "The iron core carries that changing field upward.",                  # 5
    "A changing magnetic field through a coil pushes a current around it.",  # 6
    "That is electromagnetic induction.",                                 # 7
    "One coil drives the other without touching it: mutual induction.",   # 8
    "With a steady current from a cell, nothing happens.",                # 9
    "The needle kicks only at the moment we switch on, and again when "
    "we switch off.",                                                     # 10
    "No change, no current.",                                             # 11
    "Lift the coil and the bulb dims, because less of the field "
    "reaches it.",                                                        # 12
    "Double the turns, and the voltage roughly doubles.",                 # 13
    "That is how a transformer works.",                                   # 14
    "Now an aluminium ring.",                                             # 15
    "It is a coil with just one turn.",                                   # 16
    "The induced current makes the ring a magnet that opposes the coil, "
    "and it jumps.",                                                      # 17
    "Cut a slot in the ring and it stays put.",                           # 18
    "No complete path, no current, no force.",                            # 19
    "Chargers, transformers and induction cooktops all use this.",        # 20
    "Next: why does the ring get hot?",                                   # 21
]

WHITE, YELLOW = (1.0, 1.0, 1.0), (1.0, 0.62, 0.0)
BLUE, GREEN = (0.15, 0.45, 1.0), (0.2, 1.0, 0.35)

CX, CY = kit.CORE_XY
ON_CORE = (CX, CY, kit.TOP + kit.L1["height"] + 0.001)    # resting on L1
CLEAR = kit.TOP + kit.CORE_LEN + 0.02                     # above the core top
BULB_PARK = (-0.075, -0.085, kit.TOP)                     # bulb coil set aside
FLICKER = 1.2       # visible field reversals per second (the real 50 is a blur)
BULB_FULL = 12.0
BULB_OFF = 0.3      # unlit glass still shows pale, not black
LIFT = 0.14          # how far the bulb coil is raised up the core

# Camera positions: (eye, look-at).
VIEW = {
    "bulb_a": ((-0.05, -0.34, 0.21), (CX + 0.02, CY, 0.125)),
    "bulb_b": ((0.14, -0.27, 0.23), (CX + 0.02, CY, 0.125)),
    "coils": ((-0.10, -0.82, 0.37), (CX, CY, 0.15)),
    "dc": ((0.12, -0.84, 0.46), (0.12, -0.04, 0.05)),
    "measure": ((0.0, -0.74, 0.43), (0.0, 0.03, 0.12)),
    "ring": ((-0.06, -0.80, 0.34), (CX, CY, 0.15)),
    "wide": ((-0.04, -1.20, 0.78), (-0.04, -0.05, 0.11)),
    "wide_b": ((-0.04, -1.10, 0.70), (-0.04, -0.05, 0.11)),
}


def screen_text(scene, fmt, text, x, y, size, color, backing=True):
    """Caption fixed to the screen, close to the lens so nothing covers it."""
    cam, depth = scene.camera, 0.12
    tan_h = cam.data.sensor_width / 2 / cam.data.lens
    tan_v = tan_h / fmt.aspect
    bpy.ops.object.text_add()
    obj = bpy.context.object
    obj.data.body = text
    obj.data.font = S.maths_font() or obj.data.font
    obj.data.align_x = obj.data.align_y = "CENTER"
    obj.data.size = size * 2 * tan_h * depth
    obj.data.materials.append(S.emissive("Caption", color, 1.0))
    obj.parent = cam
    obj.location = (x * tan_h * depth, y * tan_v * depth, -depth)
    parts = [obj]
    if backing:     # a dark outline keeps the words readable, hiding nothing
        h = obj.data.size
        dark = S.emissive("CaptionEdge", (0.005, 0.006, 0.01))
        data = obj.data.copy()
        data.materials.clear()
        data.materials.append(dark)
        for i in range(8):      # eight shifted dark copies make the outline
            a = math.tau * i / 8
            edge = bpy.data.objects.new("CaptionEdge", data)
            scene.collection.objects.link(edge)
            edge.parent = obj
            edge.location = (0.055 * h * math.cos(a), 0.055 * h * math.sin(a),
                             -h * 0.03)
            parts.append(edge)
    for part in parts:
        part.visible_shadow = part.visible_diffuse = part.visible_glossy = False
    return obj


def glow(name, color):
    mat = S.emissive(name, color, 1.0)
    return mat, mat.node_tree.nodes["Emission"].inputs["Strength"]


def cone(name, location, direction, mat, parent, size=0.006):
    bpy.ops.mesh.primitive_cone_add(radius1=size, depth=size * 2.6, vertices=16)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.parent = parent
    obj.location = location
    obj.rotation_euler = Vector(direction).to_track_quat("Z", "Y").to_euler()
    return obj


def field_lines(mat):
    """Closed loops of magnetic field: up the core, round and back down.
    The arrowheads flip as the current reverses."""
    root = empty("Field", location=(CX, CY, 0))
    arrows = []
    for i in range(6):
        spoke = empty("FieldSpoke", root)
        spoke.rotation_euler = (0, 0, i * math.tau / 6)
        for width, height in (((0.040, 0.135), (0.070, 0.150))[i % 2],):
            mid, zc = kit.CORE_R + 0.004 + width, 0.185
            pts = [(mid + width * math.cos(a), 0, zc + height * math.sin(a))
                   for a in [k * math.tau / 24 for k in range(25)]]
            loop = cable("FieldLine", pts, 0.0012, mat)
            loop.parent = spoke
            # Outer side of the loop: field comes down when it goes up the core.
            arrows.append(cone("FieldArrow", (mid + width, 0, zc), (0, 0, -1),
                               mat, spoke))
    return root, arrows


def current_loop(name, radius, z, mat, parent):
    """A ring of current with arrowheads; returns the empty to spin."""
    spin = empty(name, parent, (0, 0, z))
    pts = [(radius * math.cos(a), radius * math.sin(a), 0)
           for a in [k * math.tau / 32 for k in range(33)]]
    cable(name + "Line", pts, 0.0014, mat).parent = spin
    for i in range(3):
        a = i * math.tau / 3
        cone(name + "Arrow", (radius * math.cos(a), radius * math.sin(a), 0),
             (-math.sin(a), math.cos(a), 0), mat, spin, size=0.005)
    return spin


def ease(u):
    return S.smoothstep(u)


def build(scene, fmt, timeline):
    fps, tl = fmt.fps, timeline
    last = scene.frame_end

    def frame(t):
        return 1 + round(t * fps)

    def frames(t0, t1):
        return range(max(frame(t0), 1), min(frame(t1), last + 1) + 1)

    kit.light(scene)
    scene.cycles.samples = min(scene.cycles.samples, 8)
    scene.cycles.max_bounces = 3
    scene.render.use_persistent_data = True
    kit.build_kit(kit.materials())
    obj = bpy.data.objects
    bulb_coil, l3, l4 = obj["L2_BulbCoil"], obj["L3_300turns"], obj["L4_600turns"]
    ring, split = obj["RingAluminium"], obj["RingSplit"]
    bulb_glow = bpy.data.materials["BulbGlow"].node_tree.nodes["Emission"] \
        .inputs["Strength"]

    # --- Story times ---------------------------------------------------------
    s = tl.start
    key_down, key_up = s(10) + 1.3, s(10) + 3.6
    lift0, lift1 = s(12) + 0.3, s(12) + 2.6        # bulb coil slides up
    park0, park1 = s(12) + 3.5, s(13) - 0.2        # ... and is set aside
    m1_on, m1_off = (s(13), s(13) + 1.0), (s(13) + 2.1, s(13) + 3.0)
    m2_on, m2_off = (s(13) + 3.1, s(13) + 4.0), (s(15), s(15) + 0.9)
    ring_on = (s(15) + 1.0, s(15) + 2.2)
    jump = tl.end(17) - 0.9                        # "... and it jumps"
    ring_off = (s(18) + 0.2, s(18) + 1.1)
    split_on = (s(18) + 1.2, s(18) + 2.3)
    split_power = s(19) - 0.4
    supply = [(0, s(9)), (s(12), s(15)), (jump, s(18)), (split_power, s(20))]

    def powered(t):
        return any(a <= t < b for a, b in supply)

    # --- Camera --------------------------------------------------------------
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens, cam_data.clip_start = 50, 0.02
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.rotation_mode = "QUATERNION"
    moves = [(0, "bulb_a"), (s(3), "bulb_b"), (s(3) + 1.8, "coils"),
             (s(9) - 0.2, "coils"), (s(9) + 1.5, "dc"), (s(12) - 0.3, "dc"),
             (s(12) + 1.2, "coils"), (s(13) - 0.3, "coils"),
             (s(13) + 0.9, "measure"), (s(15), "measure"),
             (s(15) + 1.3, "ring"), (s(20), "ring"), (s(20) + 1.8, "wide"),
             (tl.total, "wide_b")]
    prev = None
    for f in range(1, last + 2):
        t = (f - 1) / fps
        i = max(k for k, (at, _) in enumerate(moves) if at <= t or k == 0)
        i = min(i, len(moves) - 2)
        (t0, a), (t1, b) = moves[i], moves[i + 1]
        u = ease((t - t0) / (t1 - t0))
        eye = Vector(VIEW[a][0]).lerp(Vector(VIEW[b][0]), u)
        aim = Vector(VIEW[a][1]).lerp(Vector(VIEW[b][1]), u)
        quat = (aim - eye).to_track_quat("-Z", "Y")
        if prev is not None and quat.dot(prev) < 0:
            quat.negate()
        prev = quat
        S.key(cam, f, location=eye, rotation_quaternion=quat)

    # --- Moving parts --------------------------------------------------------
    def hop(part, when, dest):
        """Lift `part` clear of the core, carry it across, set it down."""
        t0, t1 = when
        a, d = Vector(part.location), Vector(dest)
        up_a, up_d = Vector((a.x, a.y, CLEAR)), Vector((d.x, d.y, CLEAR))
        for f in frames(t0, t1):
            u = (f - frame(t0)) / max(frame(t1) - frame(t0), 1)
            if u < 0.35:
                p = a.lerp(up_a, ease(u / 0.35))
            elif u < 0.65:
                p = up_a.lerp(up_d, ease((u - 0.35) / 0.3))
            else:
                p = up_d.lerp(d, ease((u - 0.65) / 0.35))
            S.key(part, f, location=p)

    homes = {p: tuple(p.location) for p in (l3, l4, ring, split)}
    for part in (bulb_coil, l3, l4, ring, split):
        S.key(part, 1, location=tuple(part.location))

    lifted = Vector(ON_CORE) + Vector((0, 0, LIFT))
    for f in frames(lift0, lift1):
        u = ease((f - frame(lift0)) / (frame(lift1) - frame(lift0)))
        S.key(bulb_coil, f, location=Vector(ON_CORE).lerp(lifted, u))
    hop(bulb_coil, (park0, park1), BULB_PARK)
    hop(l3, m1_on, ON_CORE), hop(l3, m1_off, homes[l3])
    hop(l4, m2_on, ON_CORE), hop(l4, m2_off, homes[l4])
    ring_rest = (CX, CY, kit.TOP + kit.L1["height"])
    hop(ring, ring_on, ring_rest)

    # The jump: shoot up the core, then float, bobbing, while the supply is on.
    peak, hover, z0 = 0.285, 0.165, ring_rest[2]
    for f in frames(jump, s(18) + 0.2):
        t = (f - 1) / fps - jump
        if t < 0.2:
            z = z0 + (peak - z0) * (1 - (1 - t / 0.2) ** 2)
        else:
            z = hover + (peak - hover) * math.exp(-2.5 * (t - 0.2)) \
                * math.cos(math.tau * 1.5 * (t - 0.2))
        off = (f - 1) / fps - s(18)
        if off > 0:                                 # supply off: it drops
            z = z0 + (z - z0) * (1 - min(off / 0.2, 1) ** 2)
        S.key(ring, f, location=(CX, CY, z))
    hop(ring, ring_off, homes[ring])
    hop(split, split_on, ring_rest)

    # Bulb brightness: needs the supply on and the coil on the core, and
    # fades as the coil is lifted.
    for f in range(1, last + 2):
        t = (f - 1) / fps
        scene.frame_set(f)
        height = bulb_coil.location.z - ON_CORE[2]
        on_core = abs(bulb_coil.location.x - CX) < 1e-4 and height < 0.2
        bulb_glow.default_value = (BULB_FULL * (1 - 0.9 * ease(height / LIFT))
                                   if powered(t) and on_core else 0.0) + BULB_OFF
        bulb_glow.keyframe_insert("default_value", frame=f)
    scene.frame_set(1)

    # Galvanometer needle and tap key (make-and-break).
    needle, arm = obj["NeedlePivot"], obj["KeyArm"]
    for f in frames(s(9), s(12)):
        t = (f - 1) / fps
        down = ease((t - key_down) / 0.12) - ease((t - key_up) / 0.12)
        S.key(arm, f, rotation_euler=(math.radians(8) * down, 0, 0))
        kick = 0.0
        for at, sign in ((key_down, 1), (key_up, -1)):
            if t >= at:
                dt = t - at
                kick += sign * 0.6 * (1 - math.exp(-dt / 0.03)) * math.exp(-dt / 0.3) \
                    * math.cos(dt * 9)
        S.key(needle, f, rotation_euler=(0, kick, 0))

    # --- Leads for the cell experiment ----------------------------------------
    # Cell and tap key feed the primary through the input sockets (the AC
    # leads come out); the galvanometer is joined to the coil on top.
    m = {n: bpy.data.materials[n] for n in ("Red", "Black")}
    before = set(bpy.data.objects)
    top, plug = kit.TOP, kit.TOP + 0.006
    cable("CellToKey", [(0.357, -0.09, 0.0165), (0.385, -0.10, 0.03),
                        (0.39, -0.20, 0.035), (0.35, -0.235, 0.025),
                        (0.325, -0.216, 0.011)], 0.0022, m["Red"])
    for name, mat, y, pts in (
            ("KeyToCoil", m["Red"], -0.02,
             [(0.325, -0.154, 0.017), (0.30, -0.135, 0.035), (0.20, -0.14, 0.05),
              (0.0, -0.145, 0.05), (-0.13, -0.13, 0.06), (-0.205, -0.07, 0.09)]),
            ("CellToCoil", m["Black"], 0.02,
             [(0.295, -0.09, 0.0165), (0.275, -0.08, 0.035), (0.25, -0.035, 0.05),
              (0.0, -0.03, 0.06), (-0.15, -0.04, 0.07), (-0.19, 0.0, 0.10)])):
        kit.cyl(name + "Plug", -0.205, y, plug, plug + 0.03, 0.005, mat)
        cable(name, pts + [(-0.205, y, plug + 0.07), (-0.205, y, plug + 0.03)],
              0.0022, mat)
    sock_y, sock_z = CY - (kit.L2["flange"] - 0.008), ON_CORE[2] + kit.L2["height"]
    for name, mat, gx, sx, lift in (("MeterLeadA", m["Red"], 0.30, 0.009, 0.025),
                                    ("MeterLeadB", m["Black"], 0.36, -0.009, 0.045)):
        kit.lead(name, (gx, 0.05, 0.108), (CX + sx, sock_y, sock_z + 0.004),
                 mat, m, lift=lift)
    dc_leads = [o for o in bpy.data.objects if o not in before]
    ac_leads = [o for o in bpy.data.objects if o.name.startswith("SupplyLead")]
    dc_on, dc_off = frame(s(9) + 0.1), frame(s(12) - 0.2)
    for part, shown in [(o, True) for o in dc_leads] + [(o, False) for o in ac_leads]:
        for f, on in ((1, False), (dc_on - 1, False), (dc_on, True),
                      (dc_off, True), (dc_off + 1, False)):
            vis = on if shown else not on
            S.key(part, f, scale=(1, 1, 1) if vis else (0, 0, 0))

    # --- Field lines and induced currents ------------------------------------
    field_mat, field_strength = glow("FieldGlow", BLUE)
    field, arrows = field_lines(field_mat)
    amp_mat, amp_strength = glow("CurrentGlow", YELLOW)
    coil_current = current_loop("CoilCurrent", kit.L2["flange"] + 0.004,
                                kit.L2["height"] / 2, amp_mat, bulb_coil)
    ring_current = current_loop("RingCurrent", kit.RING_OUT + 0.005, 0.006,
                                amp_mat, ring)
    for f in range(1, last + 2):
        t = (f - 1) / fps
        wave = math.sin(math.tau * FLICKER * t)
        show_field = powered(t) and t >= s(4)
        S.key(field, f, scale=(1, 1, 1) if show_field else (0, 0, 0))
        for arrow in arrows:
            S.key(arrow, f, scale=(1, 1, wave))
        field_strength.default_value = 0.6 + 3.0 * abs(wave)
        field_strength.keyframe_insert("default_value", frame=f)
        amp_strength.default_value = 1.0 + 3.0 * abs(math.cos(math.tau * FLICKER * t))
        amp_strength.keyframe_insert("default_value", frame=f)
        swing = (0, 0, 1.0 * math.cos(math.tau * FLICKER * t))
        on_coil = s(6) <= t < s(9)
        S.key(coil_current, f, scale=(1, 1, 1) if on_coil else (0, 0, 0),
              rotation_euler=swing)
        on_ring = jump <= t < s(18)
        S.key(ring_current, f, scale=(1, 1, 1) if on_ring else (0, 0, 0),
              rotation_euler=swing)

    # --- Captions ------------------------------------------------------------
    def caption(text, start, end, color=WHITE, y=-0.82, size=0.05, x=0.0,
                backing=True):
        S.show(screen_text(scene, fmt, text, x, y, size, color, backing),
               start, end, fps)

    caption("?", s(2), s(3), YELLOW, y=0.34, size=0.09, x=0.55)
    caption("Alternating current: back and forth 50 times a second", s(3) + 1.0, s(4))
    caption("Its magnetic field keeps changing", s(4), s(5))
    caption("The iron core carries the field upward", s(5), s(6))
    caption("A changing field pushes a current round the coil", s(6), s(7))
    caption("Electromagnetic induction", s(7), s(8))
    caption("Mutual induction", s(8), s(9), YELLOW, size=0.058)
    caption("Steady current from a cell: nothing", s(9) + 1.0, s(10), y=0.88)
    caption("The needle kicks only at ON and OFF", s(10), s(11), y=0.88)
    caption("No change, no current", s(11), s(12), YELLOW, y=0.88, size=0.058)
    caption("Further from the coil: dimmer", s(12) + 0.5, s(13))
    caption("300 turns: about 10 V", s(13) + 1.1, s(15), y=-0.62)
    caption("600 turns: about 20 V", s(13) + 4.1, s(15), YELLOW)
    caption("An aluminium ring", s(15) + 1.0, s(16))
    caption("A coil with just one turn", s(16), s(17))
    caption("Its induced current opposes the coil", s(17), jump)
    caption("...and it jumps", jump, s(18), YELLOW, size=0.058)
    caption("Cut a slot in the ring", s(18) + 0.3, s(19))
    caption("No loop, no current", s(19), s(20), YELLOW, size=0.058)
    for i, text in enumerate(("Phone chargers", "Transformers",
                              "Induction cooktops")):
        caption(text, s(20) + 1.2 + i * 0.7, s(21), y=0.80 - i * 0.16, size=0.046)
    caption("Next: why does the ring get hot?", s(21), None, YELLOW, size=0.058)
    for a, b in supply:
        caption("24 V AC: ON", a + 0.01, min(b, tl.total), GREEN, y=0.86,
                size=0.024, x=0.74)
