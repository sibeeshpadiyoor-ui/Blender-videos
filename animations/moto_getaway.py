"""Motorcycle getaway: a 12 second previs shot to use as a video reference.

One continuous camera move over a simple city block:

    0.0 - 1.5 s   close-up of the spinning rear wheel as the bike launches
    1.5 - 4.0 s   pull back and up into a chase shot while it accelerates
    4.0 - 7.3 s   wide chase: the bike weaves right of car A, left of car B
    7.3 - 9.3 s   the camera drops, overtakes on the left and swings ahead
    9.3 - 12 s    low frontal shot: the rider leans through the right-hand
                  corner and accelerates at the camera, which backs away

Everything is driven by the tables below (seconds and metres), so timing,
the weave, the cars and the camera can be retuned without touching the
code. Built for 16:9:

    python render.py moto_getaway --format youtube --quality preview --save-blend
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

from bvid import scene as S

SECONDS = 12.0

# --- Street layout (metres). The bike starts at the origin heading +Y and
# turns right, onto a cross street heading +X. -------------------------------
ROAD_HALF = 7.0         # half the road width: four 3.5 m lanes
LANE = 3.5
KERB = 0.15
SETBACK = 3.0           # sidewalk between the kerb and the buildings
TURN_RADIUS = 18.0      # radius of the corner, measured on the road centre
T_TURN_IN = 8.9         # when the bike reaches the corner

# --- Motorcycle -------------------------------------------------------------
# Speed in m/s at given times; values in between are eased.
SPEED_KEYS = [(0.0, 1.5), (1.0, 7.0), (2.0, 13.5), (4.0, 24.0), (7.3, 28.0),
              (8.8, 13.5), (10.0, 13.0), (12.0, 27.0), (13.0, 30.0)]
# Sideways position, metres left of the road centre line (negative = right).
OFFSET_KEYS = [(0.0, 1.75), (3.3, 1.75),     # behind car A, in its lane
               (4.9, -1.5), (5.6, -1.5),     # pass car A on its right
               (7.1, 1.5),                   # pass car B on its left
               (8.7, 1.2), (12.5, 1.0)]      # hold that line round the corner
MAX_LEAN = math.radians(48)
WHEEL_R = 0.32
FRONT_Y, REAR_Y = 0.74, -0.70                # axle positions along the bike
WHEELSPIN = 6.5         # extra rear tyre speed (m/s) at launch, gone by 1.8 s

# --- Traffic: both cars drive straight on at a steady speed. `lane` uses
# the same left-of-centre convention as OFFSET_KEYS; `pass_at` is when the
# bike draws level. -----------------------------------------------------------
CAR_SPEED = 11.0
CARS = [
    dict(name="CarA", lane=1.75, pass_at=5.2, color=(0.75, 0.75, 0.78),
         cabin=(2.3, 0.55, -0.25)),
    dict(name="CarB", lane=-1.75, pass_at=7.3, color=(0.05, 0.2, 0.7),
         cabin=(3.0, 0.75, -0.45)),
]

# --- Camera -----------------------------------------------------------------
# The camera rides the road centre line `lead` metres ahead of the bike
# (negative = behind), `side` metres to the left, `height` above the road.
# `follow` is how much of the bike's own sideways weave it copies.
# It looks at a point `aim_fwd` ahead of the bike's centre, `aim_up` high.
CAMERA_KEYS = [
    # time  lead   side  follow height lens  aim_fwd aim_up
    (0.0,  -1.35,  1.35,  1.0,  0.30,  35,  -0.70,  0.32),   # rear wheel
    (1.3,  -1.45,  1.40,  1.0,  0.32,  35,  -0.70,  0.32),
    (2.6,  -4.5,   1.2,   1.0,  0.9,   30,   0.0,   0.75),   # pulling back
    (3.8,  -8.5,   0.0,   0.5,  2.3,   26,   2.0,   0.9),
    (4.8,  -8.5,   0.0,   0.35, 2.6,   28,   4.0,   0.8),    # wide chase
    (6.9,  -8.5,   0.0,   0.35, 2.6,   28,   4.0,   0.8),
    (7.4,  -8.0,   1.5,   0.5,  2.2,   27,   3.0,   0.8),
    (7.9,  -4.5,   3.6,   0.5,  1.6,   27,   1.5,   0.8),
    (8.4,  -0.5,   4.6,   0.5,  1.1,   28,   0.3,   0.8),    # alongside
    (8.9,   3.5,   3.6,   0.5,  0.75,  29,   0.0,   0.8),
    (9.4,   7.0,   1.8,   0.5,  0.5,   30,   0.0,   0.8),    # now ahead
    (10.2,  9.5,   0.6,   0.3,  0.4,   32,   0.0,   0.75),   # low frontal
    (12.0,  5.0,   0.0,   0.5,  0.45,  35,   0.0,   0.85),
]
SHOTS = [(0.0, "close: rear wheel"), (1.5, "pull back"),
         (4.0, "wide: weave"), (7.3, "swing ahead"),
         (9.3, "low frontal: corner")]

SKY = (0.55, 0.72, 0.95)
ASPHALT = (0.15, 0.15, 0.16)
SIDEWALK = (0.42, 0.41, 0.39)
PAINT = (0.85, 0.85, 0.8)
BUILDING_COLORS = [(0.55, 0.42, 0.33), (0.62, 0.6, 0.55), (0.4, 0.44, 0.5),
                   (0.66, 0.5, 0.38), (0.5, 0.52, 0.48), (0.7, 0.66, 0.58)]


# ---------------------------------------------------------------------------
# Motion: everything is worked out as arrays over time first, then keyed.
# ---------------------------------------------------------------------------
DT = 1 / 240
T0, T1 = -1.0, SECONDS + 1.0        # run past both ends so smoothing is clean


def eased(keys, t):
    """Smooth interpolation through (time, value) keys that never overshoots
    (monotone cubic); holds the end values outside the keyed range."""
    xk = np.array([k[0] for k in keys], float)
    yk = np.array([k[1] for k in keys], float)
    h = np.diff(xk)
    delta = np.diff(yk) / h
    d = np.zeros_like(yk)
    d[0], d[-1] = delta[0], delta[-1]
    for i in range(1, len(yk) - 1):
        if delta[i - 1] * delta[i] > 0:
            d[i] = 2 * delta[i - 1] * delta[i] / (delta[i - 1] + delta[i])
    t = np.clip(np.asarray(t, float), xk[0], xk[-1])
    i = np.clip(np.searchsorted(xk, t, side="right") - 1, 0, len(h) - 1)
    u = (t - xk[i]) / h[i]
    return ((2 * u**3 - 3 * u**2 + 1) * yk[i] + (u**3 - 2 * u**2 + u) * h[i] * d[i]
            + (-2 * u**3 + 3 * u**2) * yk[i + 1] + (u**3 - u**2) * h[i] * d[i + 1])


def smooth(a, seconds):
    """Gaussian blur along time."""
    n = max(int(round(seconds / DT)), 1)
    x = np.arange(-3 * n, 3 * n + 1)
    kernel = np.exp(-0.5 * (x / n) ** 2)
    kernel /= kernel.sum()
    a = np.asarray(a, float)
    if a.ndim == 1:
        return np.convolve(np.pad(a, 3 * n, mode="edge"), kernel, "valid")
    return np.stack([smooth(a[:, k], seconds) for k in range(a.shape[1])], 1)


class Plan:
    """The whole move as arrays sampled every DT seconds from T0 to T1."""

    def __init__(self):
        t = self.t = np.arange(T0, T1 + DT / 2, DT)
        self.speed_keyed = eased(SPEED_KEYS, t)
        s = np.concatenate([[0], np.cumsum(
            (self.speed_keyed[1:] + self.speed_keyed[:-1]) / 2 * DT)])
        self.s = s - np.interp(0.0, t, s)       # distance along the centre line
        self.turn_s = float(np.interp(T_TURN_IN, t, self.s))
        self.corner = (0.0, self.turn_s + TURN_RADIUS)   # centre of the junction

        # Bike: centre line + weave, rounded off a little so it turns in
        # progressively instead of snapping onto the arc.
        self.offset = eased(OFFSET_KEYS, t)
        pos, _, left = self.centre_line(self.s)
        self.pos = smooth(pos + left * self.offset[:, None], 0.12)
        vel = np.gradient(self.pos, DT, axis=0)
        acc = np.gradient(vel, DT, axis=0)
        self.speed = np.hypot(vel[:, 0], vel[:, 1])
        self.fwd = vel / self.speed[:, None]
        self.heading = np.unwrap(np.arctan2(vel[:, 1], vel[:, 0]))
        sideways = (vel[:, 0] * acc[:, 1] - vel[:, 1] * acc[:, 0]) / self.speed
        # Lean into the turn by the angle that balances the cornering force.
        self.lean = smooth(np.clip(-np.arctan(sideways / 9.81),
                                   -MAX_LEAN, MAX_LEAN), 0.1)
        # Squat under power, dive on the brakes.
        self.pitch = smooth(np.clip(np.gradient(self.speed, DT) * 0.006,
                                    -0.05, 0.05), 0.12)
        self.front_spin = -self.s / WHEEL_R
        slip = WHEELSPIN * (1 - np.clip(t / 1.8, 0, 1)) ** 2
        self.rear_spin = -np.cumsum((self.speed_keyed + slip) * DT) / WHEEL_R

        # Camera.
        k = np.array(CAMERA_KEYS, float)
        ch = [eased(list(zip(k[:, 0], k[:, i])), t) for i in range(1, 8)]
        lead, side, follow, height, self.lens, aim_fwd, aim_up = ch
        base, _, left = self.centre_line(self.s + lead)
        weave = smooth(self.offset, 0.3)
        cam = base + left * (side + follow * weave)[:, None]
        self.cam = smooth(np.column_stack([cam, height]), 0.12)
        aim = self.pos + self.fwd * aim_fwd[:, None]
        self.aim = smooth(np.column_stack([aim, aim_up]), 0.08)

    def centre_line(self, s):
        """Position, direction and left-hand normal of the route at `s`."""
        s = np.asarray(s, float)
        r, s0 = TURN_RADIUS, self.turn_s
        phi = np.clip((s - s0) / r, 0, math.pi / 2)
        before = np.minimum(s, s0)
        after = np.maximum(s - s0 - r * math.pi / 2, 0)
        pos = np.column_stack([r - r * np.cos(phi) + after,
                               before + r * np.sin(phi)])
        tangent = np.column_stack([np.sin(phi), np.cos(phi)])
        left = np.column_stack([-np.cos(phi), np.sin(phi)])
        return pos, tangent, left

    def index(self, seconds):
        return int(round((seconds - T0) / DT))

    def car_xy(self, car, seconds):
        y_pass = self.pos[self.index(car["pass_at"]), 1]
        return -car["lane"], y_pass + CAR_SPEED * (seconds - car["pass_at"])


# ---------------------------------------------------------------------------
# Modelling helpers: real-size meshes (no object scale), parented in place.
# ---------------------------------------------------------------------------
def _object(name, bm, mat, parent=None, location=(0, 0, 0), rotation=None,
            smooth_shading=False):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    if smooth_shading:
        for poly in mesh.polygons:
            poly.use_smooth = True
    if mat is not None:
        mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    if rotation is not None:
        obj.rotation_euler = rotation
    return obj


def box(name, size, location, mat, parent=None, rotation=None, taper=1.0):
    """A box `size` = (x, y, z); `taper` narrows the top face."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        k = taper if v.co.z > 0 else 1.0
        v.co = Vector((v.co.x * size[0] * k, v.co.y * size[1] * k,
                       v.co.z * size[2]))
    return _object(name, bm, mat, parent, location, rotation)


def ball(name, radii, location, mat, parent=None, rotation=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2]))
    return _object(name, bm, mat, parent, location, rotation, True)


def rod(name, start, end, radius, mat, parent=None, flatten=(1.0, 1.0)):
    """A cylinder from `start` to `end`."""
    start, end = Vector(start), Vector(end)
    axis = end - start
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=radius,
                          radius2=radius, depth=axis.length)
    for v in bm.verts:
        v.co.x *= flatten[0]
        v.co.y *= flatten[1]
    return _object(name, bm, mat, parent, (start + end) / 2,
                   axis.to_track_quat("Z", "Y").to_euler(), True)


def ring(name, major, minor, mat, parent=None, width=1.0):
    """A torus around the X axis (a tyre or rim)."""
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=32, minor_segments=10)
    obj = bpy.context.object
    obj.name = name
    for v in obj.data.vertices:
        v.co.z *= width
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.data.materials.append(mat)
    obj.parent = parent
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, math.pi / 2, 0)
    return obj


def empty(name, parent=None, location=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.empty_display_size = 0.3
    obj.parent = parent
    obj.location = location
    return obj


def slabs(name, boxes, mat):
    """Many boxes ((centre), (size)) merged into one object."""
    bm = bmesh.new()
    for centre, size in boxes:
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.LocRotScale(Vector(centre), None, Vector(size)))
    return _object(name, bm, mat)


# ---------------------------------------------------------------------------
# Models. Vehicles face +Y, with their origin on the road under the middle.
# ---------------------------------------------------------------------------
def build_wheel(name, y, width, mats, parent):
    hub = empty(name, parent, (0, y, WHEEL_R))
    ring(name + "Tyre", WHEEL_R - 0.075, 0.075, mats["rubber"], hub, width)
    ring(name + "Rim", 0.2, 0.022, mats["metal"], hub)
    for i in range(3):      # three spokes, so the spin is easy to read
        a = i * math.tau / 3
        box(f"{name}Spoke{i}", (0.035, 0.06, 0.2),
            (0, -0.1 * math.sin(a), 0.1 * math.cos(a)), mats["metal"], hub,
            rotation=(a, 0, 0))
    rod(name + "Disc", (0.045, 0, 0), (0.06, 0, 0), 0.12, mats["dark"], hub)
    # A paint mark on the tyre makes the rotation obvious in the close-up.
    box(name + "Mark", (0.16 * width, 0.11, 0.03), (0, 0, WHEEL_R - 0.04),
        mats["paint"], hub)
    return hub


def build_motorcycle(mats):
    """Returns (root, lean, front wheel, rear wheel). `root` carries position
    and heading; `lean` tips the bike and rider over about the tyre contact
    line."""
    root = empty("Bike")
    lean = empty("BikeLean", root)
    m, p = mats, lean
    front = build_wheel("FrontWheel", FRONT_Y, 1.0, m, p)
    rear = build_wheel("RearWheel", REAR_Y, 1.3, m, p)

    box("Engine", (0.30, 0.55, 0.36), (0, 0.05, 0.47), m["dark"], p)
    box("Belly", (0.34, 0.66, 0.2), (0, 0.12, 0.34), m["bike"], p, taper=0.8)
    ball("Tank", (0.17, 0.33, 0.15), (0, 0.15, 0.84), m["bike"], p)
    box("Seat", (0.26, 0.5, 0.09), (0, -0.33, 0.80), m["rubber"], p)
    box("Tail", (0.22, 0.44, 0.12), (0, -0.68, 0.90), m["bike"], p,
        rotation=(-0.25, 0, 0), taper=0.7)
    box("TailLight", (0.14, 0.03, 0.05), (0, -0.905, 0.95), m["tail"], p)
    ball("Fairing", (0.20, 0.30, 0.22), (0, 0.60, 0.88), m["bike"], p)
    ball("Screen", (0.15, 0.14, 0.12), (0, 0.60, 1.07), m["glass"], p)
    ball("Headlight", (0.10, 0.04, 0.06), (0, 0.885, 0.86), m["head"], p)
    ball("FrontFender", (0.075, 0.22, 0.05), (0, FRONT_Y, 0.68), m["bike"], p)
    for sx in (-1, 1):
        rod("Fork", (sx * 0.10, FRONT_Y, WHEEL_R), (sx * 0.10, 0.50, 1.0),
            0.025, m["metal"], p)
        rod("Swingarm", (sx * 0.09, REAR_Y, WHEEL_R), (sx * 0.09, -0.1, 0.42),
            0.03, m["dark"], p)
    rod("Handlebar", (-0.30, 0.47, 1.02), (0.30, 0.47, 1.02), 0.018, m["dark"], p)
    rod("Exhaust", (0.17, -0.15, 0.42), (0.19, -0.85, 0.62), 0.055, m["metal"], p)

    # Rider, fixed in a forward-leaning sport riding pose.
    ball("Hips", (0.18, 0.17, 0.14), (0, -0.28, 0.95), m["suit"], p)
    rod("Torso", (0, -0.27, 0.97), (0, 0.20, 1.32), 0.15, m["suit"], p,
        flatten=(1.35, 0.9))
    ball("Shoulders", (0.25, 0.13, 0.12), (0, 0.20, 1.32), m["suit"], p)
    ball("Helmet", (0.14, 0.16, 0.145), (0, 0.34, 1.49), m["helmet"], p)
    ball("Visor", (0.115, 0.06, 0.06), (0, 0.455, 1.485), m["glass"], p)
    for sx in (-1, 1):
        shoulder, elbow = (sx * 0.22, 0.20, 1.30), (sx * 0.29, 0.34, 1.12)
        hand = (sx * 0.28, 0.47, 1.04)
        rod("UpperArm", shoulder, elbow, 0.055, m["suit"], p)
        rod("Forearm", elbow, hand, 0.05, m["suit"], p)
        ball("Elbow", (0.058,) * 3, elbow, m["suit"], p)
        ball("Glove", (0.06,) * 3, hand, m["rubber"], p)
        hip, knee = (sx * 0.12, -0.26, 0.93), (sx * 0.21, 0.17, 0.74)
        foot = (sx * 0.20, -0.14, 0.40)
        rod("Thigh", hip, knee, 0.085, m["suit"], p)
        rod("Shin", knee, foot, 0.065, m["suit"], p)
        ball("Knee", (0.088,) * 3, knee, m["suit"], p)
        box("Boot", (0.10, 0.27, 0.09), (sx * 0.20, -0.08, 0.36), m["rubber"], p)
    return root, lean, front, rear


def build_car(spec, mats):
    length, width = 4.4, 1.8
    cabin_len, cabin_h, cabin_y = spec["cabin"]
    root = empty(spec["name"])
    paint = S.material(spec["name"] + "Paint", spec["color"], roughness=0.3)
    box("Body", (width, length, 0.62), (0, 0, 0.56), paint, root)
    box("Cabin", (width - 0.1, cabin_len, cabin_h),
        (0, cabin_y, 0.87 + cabin_h / 2), mats["glass"], root, taper=0.82)
    box("Roof", ((width - 0.1) * 0.82, cabin_len * 0.82, 0.05),
        (0, cabin_y, 0.87 + cabin_h + 0.025), paint, root)
    for sx in (-1, 1):
        for y in (-1.4, 1.4):
            rod("Wheel", (sx * 0.68, y, 0.33), (sx * 0.92, y, 0.33), 0.33,
                mats["rubber"], root)
        box("TailLight", (0.35, 0.04, 0.14), (sx * 0.6, -length / 2, 0.7),
            mats["tail"], root)
        box("HeadLight", (0.35, 0.04, 0.14), (sx * 0.6, length / 2, 0.7),
            mats["head"], root)
    return root


def window_material(name, wall):
    """A wall with a grid of dark windows, from a procedural texture."""
    mat = S.material(name, wall, roughness=0.8)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    coords = nodes.new("ShaderNodeTexCoord")
    split = nodes.new("ShaderNodeSeparateXYZ")
    along = nodes.new("ShaderNodeMath")     # x + y: runs along any wall
    join = nodes.new("ShaderNodeCombineXYZ")
    brick = nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.inputs["Color1"].default_value = (0.05, 0.07, 0.1, 1)
    brick.inputs["Color2"].default_value = (0.09, 0.12, 0.16, 1)
    brick.inputs["Mortar"].default_value = (*wall, 1)
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.55
    brick.inputs["Brick Width"].default_value = 2.6
    brick.inputs["Row Height"].default_value = 3.2
    links.new(coords.outputs["Object"], split.inputs[0])
    links.new(split.outputs["X"], along.inputs[0])
    links.new(split.outputs["Y"], along.inputs[1])
    links.new(along.outputs[0], join.inputs["X"])
    links.new(split.outputs["Z"], join.inputs["Y"])
    links.new(join.outputs[0], brick.inputs["Vector"])
    links.new(brick.outputs["Color"],
              mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    return mat


def build_city(corner_y):
    """A four-way junction at (0, corner_y) with buildings on every block."""
    rng = random.Random(7)
    south, north, west, east = -90.0, corner_y + 170.0, -170.0, 240.0
    inner = ROAD_HALF + SETBACK
    S.add_floor(ASPHALT, size=1500.0).location = (0, corner_y, 0)

    # Raised sidewalk slabs fill the four blocks.
    blocks = [(west, -ROAD_HALF, south, corner_y - ROAD_HALF),
              (ROAD_HALF, east, south, corner_y - ROAD_HALF),
              (west, -ROAD_HALF, corner_y + ROAD_HALF, north),
              (ROAD_HALF, east, corner_y + ROAD_HALF, north)]
    slabs("Sidewalks",
          [(((x0 + x1) / 2, (y0 + y1) / 2, KERB / 2), (x1 - x0, y1 - y0, KERB))
           for x0, x1, y0, y1 in blocks],
          S.material("Sidewalk", SIDEWALK, roughness=0.8))

    # Buildings: one row along each street frontage.
    walls = [window_material(f"Building{i}", c)
             for i, c in enumerate(BUILDING_COLORS)]
    depth = 28.0

    def row(start, end, place):
        a = start
        while a < end - 8:
            w = min(rng.uniform(14, 26), end - a)
            h = rng.uniform(10, 28)
            centre, size = place(a + w / 2, w)
            box("Building", (*size, h), (*centre, KERB + h / 2), rng.choice(walls))
            a += w

    for sx in (-1, 1):          # along the first street, both sides
        x = sx * (inner + depth / 2)
        row(south, corner_y - inner, lambda c, w: ((x, c), (depth, w)))
        row(corner_y + inner, north, lambda c, w: ((x, c), (depth, w)))
    for sy in (-1, 1):          # along the cross street, both sides
        y = corner_y + sy * (inner + depth / 2)
        row(west, -inner - depth, lambda c, w: ((c, y), (w, depth)))
        row(inner + depth, east, lambda c, w: ((c, y), (w, depth)))

    # Road paint: dashed lane lines, and zebra crossings to mark the corner.
    paint, z = [], 0.012
    clear = ROAD_HALF + 5.0     # lane lines stop short of the junction
    for lane in (-LANE, 0.0, LANE):
        for a in np.arange(south, north, 9.0):
            if abs(a + 1.5 - corner_y) > clear + 1.5:
                paint.append(((lane, a + 1.5, z), (0.15, 3.0, 0.02)))
        for a in np.arange(west, east, 9.0):
            if abs(a + 1.5) > clear + 1.5:
                paint.append(((a + 1.5, corner_y + lane, z), (3.0, 0.15, 0.02)))
    for a in np.arange(-ROAD_HALF + 0.75, ROAD_HALF, 1.2):
        for side in (-1, 1):
            d = side * (ROAD_HALF + 2.5)
            paint.append(((a, corner_y + d, z), (0.55, 3.0, 0.02)))
            paint.append(((d, corner_y + a, z), (3.0, 0.55, 0.02)))
    slabs("RoadPaint", paint, S.material("RoadPaint", PAINT, roughness=0.7))

    # Street lamps rush past and sell the speed.
    poles, pole_x = [], ROAD_HALF + 1.0

    def lamp(x, y, arm):
        poles.append(((x, y, 3.5), (0.16, 0.16, 7.0)))
        poles.append(((x + arm[0], y + arm[1], 6.95), (0.12 + abs(arm[0]) * 2,
                                                       0.12 + abs(arm[1]) * 2, 0.1)))

    for a in np.arange(south + 6, north, 24.0):
        if abs(a - corner_y) > pole_x + 2:
            lamp(-pole_x, a, (0.9, 0))
            lamp(pole_x, a + 12, (-0.9, 0))
    for a in np.arange(west + 6, east, 24.0):
        if abs(a) > pole_x + 2:
            lamp(a, corner_y - pole_x, (0, 0.9))
            lamp(a + 12, corner_y + pole_x, (0, -0.9))
    slabs("StreetLamps", poles, S.material("Lamp", (0.08, 0.09, 0.1), 0.5))


# ---------------------------------------------------------------------------
def build(scene, fmt):
    fps = fmt.fps
    plan = Plan()

    # Simple daylight; a few samples are enough for a layout preview.
    scene.cycles.samples = min(scene.cycles.samples, 16)
    scene.cycles.max_bounces = 3
    scene.render.use_motion_blur = True
    scene.render.motion_blur_shutter = 0.5
    scene.render.use_persistent_data = True
    S.set_background(scene, SKY, 1.3)
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    scene.collection.objects.link(sun)
    sun.data.energy = 3.5
    sun.data.angle = math.radians(3)
    # High in the south-south-west: lights the bike from behind the chase
    # camera and keeps building shadows off both streets.
    sun.rotation_euler = Vector((0.12, 0.32, -0.94)).to_track_quat(
        "-Z", "Y").to_euler()

    mats = {
        "rubber": S.material("Rubber", (0.025, 0.025, 0.025), roughness=0.6),
        "metal": S.material("Metal", (0.6, 0.6, 0.62), 0.3, metallic=1.0),
        "dark": S.material("DarkMetal", (0.06, 0.06, 0.07), 0.45, metallic=0.6),
        "bike": S.material("BikePaint", (0.85, 0.06, 0.03), roughness=0.25),
        "glass": S.material("Glass", (0.02, 0.03, 0.04), roughness=0.1),
        "suit": S.material("Suit", (0.03, 0.03, 0.035), roughness=0.55),
        "helmet": S.material("Helmet", (0.9, 0.9, 0.9), roughness=0.2),
        "paint": S.material("TyreMark", (0.9, 0.9, 0.85), roughness=0.6),
        "tail": S.emissive("TailLight", (1.0, 0.05, 0.03), 4.0),
        "head": S.emissive("HeadLight", (1.0, 0.95, 0.8), 6.0),
    }

    build_city(plan.corner[1])
    bike, lean, front, rear = build_motorcycle(mats)
    cars = [(spec, build_car(spec, mats)) for spec in CARS]

    cam_data = bpy.data.cameras.new("Camera")
    cam_data.clip_start, cam_data.clip_end = 0.05, 3000.0
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.rotation_mode = "QUATERNION"

    # Key every frame (plus one either side, for motion blur).
    last_quat = None
    for frame in range(scene.frame_start - 1, scene.frame_end + 2):
        seconds = (frame - 1) / fps
        i = plan.index(seconds)
        S.key(bike, frame,
              location=(plan.pos[i, 0], plan.pos[i, 1], 0.0),
              rotation_euler=(0, 0, plan.heading[i] - math.pi / 2))
        S.key(lean, frame, rotation_euler=(plan.pitch[i], plan.lean[i], 0))
        S.key(front, frame, rotation_euler=(plan.front_spin[i], 0, 0))
        S.key(rear, frame, rotation_euler=(plan.rear_spin[i], 0, 0))
        for spec, car in cars:
            S.key(car, frame, location=(*plan.car_xy(spec, seconds), 0.0))

        eye, aim = Vector(plan.cam[i]), Vector(plan.aim[i])
        quat = (aim - eye).to_track_quat("-Z", "Y")
        if last_quat is not None and quat.dot(last_quat) < 0:
            quat.negate()
        last_quat = quat
        S.key(cam, frame, location=eye, rotation_quaternion=quat)
        S.key(cam_data, frame, lens=float(plan.lens[i]))

    for seconds, name in SHOTS:
        scene.timeline_markers.new(name, frame=1 + round(seconds * fps))
    return plan
