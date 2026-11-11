#!/usr/bin/env python3
"""Render an animation to an upload-ready MP4.

    python render.py wave_ring --format reels --quality preview
    python render.py title_card --format youtube --text "MY CHANNEL"

Also works inside a regular Blender install:

    blender -b -P render.py -- wave_ring --format reels
"""
import argparse
import importlib
import pkgutil
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import bpy  # noqa: E402

import animations  # noqa: E402
from bvid import scene as S  # noqa: E402
from bvid.encode import encode  # noqa: E402
from bvid.formats import FORMATS, QUALITIES  # noqa: E402


def parse_args():
    names = [m.name for m in pkgutil.iter_modules(animations.__path__)]
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("animation", choices=names)
    p.add_argument("--format", default="reels", choices=FORMATS,
                   help="reels = 9:16 for Instagram Reels / YouTube Shorts, "
                        "youtube = 16:9 (default: reels)")
    p.add_argument("--quality", default="preview", choices=QUALITIES)
    p.add_argument("--text", help="text for animations that show text "
                                  r"(use \n for a new line)")
    p.add_argument("--loops", type=int, default=1,
                   help="repeat the animation N times in the video")
    p.add_argument("--audio", help="music/voice file to add to the video")
    p.add_argument("--still", type=int, metavar="FRAME",
                   help="render only this frame as a PNG (quick look)")
    p.add_argument("--save-blend", action="store_true",
                   help="also save a .blend to open and tweak in Blender")
    p.add_argument("--out", default=str(ROOT / "output"))
    # When run as `blender -b -P render.py -- args`, ours come after "--".
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    return p.parse_args(argv)


def main():
    args = parse_args()
    fmt, quality = FORMATS[args.format], QUALITIES[args.quality]
    anim = importlib.import_module(f"animations.{args.animation}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # Narrated animations list their sentences; the voice track sets the
    # length of the video and the timing of the visuals.
    kwargs, audio, seconds = {}, args.audio, getattr(anim, "SECONDS", None)
    if hasattr(anim, "NARRATION"):
        from bvid import narration
        timeline = narration.prepare(anim.NARRATION,
                                     out / "audio" / args.animation)
        kwargs["timeline"] = timeline
        seconds = timeline.total
        audio = audio or timeline.audio
    if args.text is not None:
        kwargs["text"] = args.text

    scene = S.reset_scene(fmt, quality, seconds)
    anim.build(scene, fmt, **kwargs)
    stem = f"{args.animation}_{fmt.name}_{quality.name}"

    if args.save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(out / f"{stem}.blend"))

    if args.still is not None:
        scene.frame_set(args.still)
        scene.render.filepath = str(out / f"{stem}_f{args.still:04d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"\nSaved {scene.render.filepath}")
        return

    frames = out / "frames" / stem
    shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir(parents=True)
    scene.render.filepath = str(frames / "f_")
    bpy.ops.render.render(animation=True)

    video = encode(frames / "f_%04d.png", out / f"{stem}.mp4", fmt.fps,
                   crf=quality.crf, loops=args.loops, audio=audio)
    print(f"\nSaved {video}")


if __name__ == "__main__":
    main()
