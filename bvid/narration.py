"""Turn a list of narration sentences into a voice track and a timeline.

The whole narration is synthesized in one request, which keeps the voice
natural across sentences. The speech service reports when each word is
spoken, and that gives the start time of every sentence so the animation
can cue visuals to it. The result is cached until the text or voice changes.
"""
import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

VOICE = "en-US-AndrewNeural"
RATE = "-8%"          # slightly slower than normal speech
LEAD_IN = 0.5         # silence before the first sentence
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


async def _request(text, path):
    import edge_tts

    words = []
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE,
                                       boundary="WordBoundary")
    with open(path, "wb") as audio:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # offsets are in units of 100 nanoseconds
                words.append((chunk["text"], chunk["offset"] / 1e7))
    return words


def _synthesize(text, path):
    import certifi
    # Behind a TLS-inspecting proxy the system CA bundle is the one to trust.
    ca = os.environ.get("SSL_CERT_FILE")
    if ca:
        certifi.where = lambda: ca
    import edge_tts

    # Write to a temporary name so a failed request never leaves a broken
    # clip in the cache; the service occasionally needs another try.
    tmp = path.with_suffix(".part")
    for attempt in range(6):
        try:
            words = asyncio.run(_request(text, tmp))
            if words and tmp.stat().st_size:
                tmp.replace(path)
                return words
        except edge_tts.exceptions.NoAudioReceived:
            pass
        time.sleep(5 * (attempt + 1))
    raise SystemExit("The speech service returned no audio; try again later")


def _sentence_starts(sentences, words):
    """Find when each sentence begins from the per-word timings."""
    text = " ".join(sentences)
    begins, pos = [], 0
    for sentence in sentences:
        begins.append(pos)
        pos += len(sentence) + 1

    starts, cursor = [None] * len(sentences), 0
    for word, seconds in words:
        found = text.find(word, cursor)
        if found < 0:
            continue
        cursor = found + len(word)
        index = max(i for i, b in enumerate(begins) if b <= found)
        if starts[index] is None:
            starts[index] = seconds
    if any(s is None for s in starts):
        raise SystemExit("Could not time every narration sentence")
    return starts


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

    text = " ".join(sentences)
    digest = hashlib.sha1(f"{VOICE}|{RATE}|{text}".encode()).hexdigest()[:10]
    voice = out_dir / f"voice_{digest}.mp3"
    timing = out_dir / f"voice_{digest}.json"
    if voice.exists() and timing.exists():
        words = json.loads(timing.read_text())
    else:
        words = _synthesize(text, voice)
        timing.write_text(json.dumps(words))

    spoken = _duration(voice)
    begins = _sentence_starts(sentences, words)
    starts = [LEAD_IN + b for b in begins]
    ends = starts[1:] + [LEAD_IN + spoken]
    durations = [e - s for s, e in zip(starts, ends)]
    total = LEAD_IN + spoken + TAIL

    track = out_dir / "narration.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(voice),
         "-af", f"adelay={round(LEAD_IN * 1000)}:all=1,apad",
         "-t", f"{total:.3f}", "-ar", "48000", str(track)], check=True)
    return Timeline(starts, durations, total, track)
