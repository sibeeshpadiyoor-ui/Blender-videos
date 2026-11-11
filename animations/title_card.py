"""3D text on a wall that pops in letter by letter - for intros and outros.

    python render.py title_card --text "SUBSCRIBE"
"""
import bpy

from bvid import scene as S

SECONDS = 3.0

DEFAULT_TEXT = "HELLO"
LETTER_DELAY = 0.08   # seconds between letters
POP_TIME = 0.45       # seconds for one letter to pop in
BACKGROUND = (0.9, 0.25, 0.12)
CAP_HEIGHT = 0.7      # height of a capital letter in the default font


def build(scene, fmt, text=None):
    lines = (text or DEFAULT_TEXT).split("\\n")
    fps = fmt.fps

    S.set_background(scene, BACKGROUND, strength=0.3)
    S.add_wall(BACKGROUND, y=0.05)

    mat = S.material("Letters", (1.0, 0.97, 0.9), roughness=0.3)
    line_height = 1.25
    half_width = 0.5
    index = 0
    for row, line in enumerate(lines):
        # Lay the letters out left to right, then centre the line.
        letters, cursor = [], 0.0
        for ch in line:
            if ch.isspace():
                cursor += 0.45
                continue
            bpy.ops.object.text_add()
            obj = bpy.context.object
            obj.data.body = ch
            obj.data.extrude = 0.12
            obj.data.bevel_depth = 0.02
            obj.data.materials.append(mat)
            bpy.context.view_layer.update()
            width = obj.dimensions.x
            letters.append((obj, cursor))
            cursor += width + 0.08
        total = max(cursor - 0.08, 0.0)
        half_width = max(half_width, total / 2)

        z = (len(lines) - 1 - row) * line_height
        for obj, x in letters:
            # Stand upright against the wall, facing the camera (-Y).
            obj.rotation_euler = (1.5708, 0, 0)
            obj.location = (x - total / 2, 0, z)
            start = 1 + round(index * LETTER_DELAY * fps)
            pop_frames = round(POP_TIME * fps)
            S.key(obj, 1, scale=(0, 0, 0))
            for f in range(pop_frames + 1):
                s = S.ease_out_back(f / pop_frames)
                S.key(obj, start + f, scale=(s, s, s))
            index += 1

    centre = ((len(lines) - 1) * line_height + CAP_HEIGHT) / 2
    S.add_area_light((3, -7, centre + 4), energy=2500, size=8,
                     target=(0, 0, centre))
    S.add_area_light((-5, -5, centre - 1), energy=600, size=6,
                     target=(0, 0, centre))

    S.add_camera(scene, fmt, target=(0, 0, centre), direction=(0.12, -1, 0.05),
                 half_width=half_width + 0.2, half_height=centre + 0.2, lens=70)
