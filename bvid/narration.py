"""Turn a list of narration sentences into a voice track and a timeline.

Each sentence is synthesized separately, so the animation can cue visuals
to the exact moment a sentence starts. Audio is cached: a sentence is only
re-synthesized when its text or the voice changes.
"""
import asyncio
import hashlib
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

VOICE = "en-US-AndrewNeural"
RATE = "-8%"          # slightly slower than normal speech
LEAD_IN = 0.5         # silence before the first sentence
GAP = 0.4             # silence between sentences
TAIL = 1.5            # hold after the last sentence


@dataclass
class Timeline:
    starts: list
    durations: list
    total: float
    audio: Path

    def start(self, i):
        return self.starts[i]

    def end(self, i):
        return self.starts[i] + self.durations[i]


def _synthesize(text, path):
    import certifi
    # Behind a TLS-inspecting proxy the system CA bundle is the one to trust.
    ca = os.environ.get("SSL_CERT_FILE")
    if ca:
        certifi.where = lambda: ca
    import edge_tts

    # Write to a temporary name so a failed request never leaves a broken
    # clip in the cache; the service occasionally needs a second try.
    tmp = path.with_suffix(".part")
    for attempt in range(6):
        try:
            asyncio.run(edge_tts.Communicate(text, VOICE, rate=RATE)
                        .save(str(tmp)))
            break
        except edge_tts.exceptions.NoAudioReceived:
            if attempt == 5:
                raise SystemExit(f"No audio returned for: {text!r}")
            time.sleep(3 * (attempt + 1))
    tmp.replace(path)


def _duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True)
    return float(out.stdout.strip())


def prepare(sentences, out_dir):
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is needed to build the narration track")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    clips, starts, durations = [], [], []
    t = LEAD_IN
    for i, text in enumerate(sentences):
        digest = hashlib.sha1(f"{VOICE}|{RATE}|{text}".encode()).hexdigest()[:10]
        clip = out_dir / f"{i:02d}_{digest}.mp3"
        if not clip.exists():
            _synthesize(text, clip)
        d = _duration(clip)
        clips.append(clip)
        starts.append(t)
        durations.append(d)
        t += d + GAP
    total = t - GAP + TAIL

    # Place every clip at its start time and mix into one track.
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for clip in clips:
        cmd += ["-i", str(clip)]
    parts = [f"[{i}:a]adelay={round(s * 1000)}:all=1[a{i}]"
             for i, s in enumerate(starts)]
    mix = "".join(f"[a{i}]" for i in range(len(clips)))
    parts.append(f"{mix}amix=inputs={len(clips)}:normalize=0,apad[out]")
    track = out_dir / "narration.wav"
    cmd += ["-filter_complex", ";".join(parts), "-map", "[out]",
            "-t", f"{total:.3f}", "-ar", "48000", str(track)]
    subprocess.run(cmd, check=True)
    return Timeline(starts, durations, total, track)
