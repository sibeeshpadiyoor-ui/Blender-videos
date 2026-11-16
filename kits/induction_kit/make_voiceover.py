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

from bvid import narration  # noqa: E402

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
