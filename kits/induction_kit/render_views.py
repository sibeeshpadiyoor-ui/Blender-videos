#!/usr/bin/env python3
"""Render stills of the kit model and save the Blender project.

    python kits/induction_kit/render_views.py [--quality preview]

Writes kit_labelled.png, kit_top.png, kit_coils.png and induction_kit.blend
next to this file. The labelled view numbers each part and lists them below.
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Vector  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from animations import induction_kit as kit  # noqa: E402
from bvid import scene as S  # noqa: E402
from bvid.formats import FORMATS, QUALITIES  # noqa: E402

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# name: (camera position, look-at point, lens in mm)
VIEWS = {
    "kit_labelled": ((-0.04, -1.30, 0.86), (-0.04, -0.05, 0.09), 52),
    "kit_top": ((-0.04, -0.081, 1.9), (-0.04, -0.08, 0.0), 58),
    "kit_coils": ((-0.42, -0.50, 0.36), (-0.09, 0.02, 0.12), 60),
}


def render(scene, cam, name, eye, aim, lens):
    cam.location = eye
    cam.data.lens = lens
    S.look_at(cam, aim)
    bpy.context.view_layer.update()
    scene.render.filepath = str(HERE / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    return Path(scene.render.filepath)


def label(path, scene, cam, parts):
    """Number each part on the image and add a legend strip underneath."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    u = w / 1920                                    # scale with resolution
    font = ImageFont.truetype(FONT, round(22 * u))
    small = ImageFont.truetype(FONT, round(21 * u))
    names = sorted(parts, key=lambda n: world_to_camera_view(
        scene, cam, Vector(parts[n])).x)
    rows = -(-len(names) // 3)
    strip = round((rows * 36 + 36) * u)
    sheet = Image.new("RGB", (w, h + strip), "white")
    sheet.paste(img)
    draw = ImageDraw.Draw(sheet)
    r = round(19 * u)
    for i, name in enumerate(names, 1):
        uv = world_to_camera_view(scene, cam, Vector(parts[name]))
        x, y = uv.x * w, (1 - uv.y) * h
        bx, by = x, y - 46 * u                      # badge sits above the part
        draw.line((x, y, bx, by), fill="white", width=round(3 * u))
        draw.ellipse((x - 4 * u, y - 4 * u, x + 4 * u, y + 4 * u), fill="white")
        draw.ellipse((bx - r, by - r, bx + r, by + r), fill="#c0392b",
                     outline="white", width=round(2 * u))
        draw.text((bx, by), str(i), font=font, fill="white", anchor="mm")
        col, row = (i - 1) // rows, (i - 1) % rows
        lx, ly = (40 + col * 630) * u, h + (22 + row * 36) * u
        draw.ellipse((lx, ly, lx + 2 * r * 0.8, ly + 2 * r * 0.8), fill="#c0392b")
        draw.text((lx + r * 0.8, ly + r * 0.8), str(i), font=small, fill="white",
                  anchor="mm")
        draw.text((lx + 44 * u, ly + r * 0.8), name, font=small, fill="#222",
                  anchor="lm")
    sheet.save(path)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--quality", default="final", choices=QUALITIES)
    p.add_argument("--only", choices=VIEWS)
    args = p.parse_args()
    fmt = FORMATS["youtube"]
    scene = S.reset_scene(fmt, QUALITIES[args.quality], kit.SECONDS)
    parts = kit.build(scene, fmt)
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE / "induction_kit.blend"))

    # A free camera for the stills; the turntable camera stays in the .blend.
    cam = bpy.data.objects.new("StillCamera", bpy.data.cameras.new("StillCamera"))
    scene.collection.objects.link(cam)
    cam.data.clip_start = 0.02
    scene.camera = cam
    for name, (eye, aim, lens) in VIEWS.items():
        if args.only in (None, name):
            path = render(scene, cam, name, eye, aim, lens)
            if name == "kit_labelled":
                label(path, scene, cam, parts)
            print("Saved", path)


if __name__ == "__main__":
    main()
