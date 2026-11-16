#!/usr/bin/env python3
"""Synthesize the voiceover for the induction kit video.

    python kits/induction_kit/make_voiceover.py

Script: scripts/induction_kit/01-mutual-induction-and-jumping-ring.md
Uses the channel voice set in bvid/narration.py. Writes voiceover.mp3,
captions.srt and timings.json (when each sentence starts, for cueing the
animation) into voiceover/ next to this file.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from animations.induction_kit_video import NARRATION  # noqa: E402
from bvid import narration  # noqa: E402

def main():
    out = HERE / "voiceover"
    timeline = narration.prepare(NARRATION, out)
    mp3 = out / "voiceover.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i",
                    str(timeline.audio), "-b:a", "128k", str(mp3)], check=True)
    cues = [{"index": i, "start": round(timeline.start(i), 2),
             "end": round(timeline.end(i), 2), "text": text}
            for i, text in enumerate(NARRATION)]
    (out / "timings.json").write_text(json.dumps(
        {"voice": narration.VOICE, "speed": narration.SPEED, "total": round(timeline.total, 2),
         "sentences": cues}, indent=2))
    timeline.write_srt(out / "captions.srt")
    print(f"Saved {mp3} ({timeline.total:.1f} s)")
    for cue in cues:
        print(f'{cue["start"]:6.2f}  {cue["text"]}')


if __name__ == "__main__":
    main()
