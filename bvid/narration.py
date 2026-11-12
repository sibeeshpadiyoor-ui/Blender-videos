"""Turn a list of narration sentences into a voice track and a timeline.

A sentence is a string, or (string, pause) to hold longer after it.

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
RATE = "-12%"         # slower than normal speech, for teaching
PAUSE = 0.6           # extra silence added after every sentence
LEAD_IN = 0.5         # silence before the first sentence
TAIL = 1.5            # hold after the last sentence


@dataclass
class Timeline:
    sentences: list
    starts: list      # when each sentence begins
    ends: list        # when its last word finishes
    total: float
    audio: Path

    def start(self, i):
        return self.starts[i]

    def end(self, i):
        return self.ends[i]

    def write_srt(self, path):
        def stamp(t):
            h, rem = divmod(t, 3600)
            m, sec = divmod(rem, 60)
            return f"{int(h):02d}:{int(m):02d}:{sec:06.3f}".replace(".", ",")
        lines = []
        for i, text in enumerate(self.sentences):
            lines += [str(i + 1),
                      f"{stamp(self.starts[i])} --> {stamp(self.ends[i] + 0.2)}",
                      text, ""]
        Path(path).write_text("\n".join(lines), encoding="utf-8")


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
                words.append((chunk["text"], chunk["offset"] / 1e7,
                              chunk["duration"] / 1e7))
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


def _sentence_spans(sentences, words):
    """(start, end) of each sentence in the raw voice, from word timings."""
    text = " ".join(sentences)
    begins, pos = [], 0
    for sentence in sentences:
        begins.append(pos)
        pos += len(sentence) + 1

    spans, cursor = [None] * len(sentences), 0
    for word, start, length in words:
        found = text.find(word, cursor)
        if found < 0:
            continue
        cursor = found + len(word)
        index = max(i for i, b in enumerate(begins) if b <= found)
        first = spans[index][0] if spans[index] else start
        spans[index] = (first, start + length)
    if any(s is None for s in spans):
        raise SystemExit("Could not time every narration sentence")
    return spans


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

    pauses = [PAUSE + (s[1] if isinstance(s, tuple) else 0.0)
              for s in sentences]
    sentences = [s[0] if isinstance(s, tuple) else s for s in sentences]

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
    spans = _sentence_spans(sentences, words)

    # Cut the voice in the silence between sentences and move each piece
    # later, so every sentence is followed by its extra pause.
    cuts = [0.0] + [(spans[i - 1][1] + spans[i][0]) / 2
                    for i in range(1, len(spans))] + [spoken]
    starts, ends, pieces, shift = [], [], [], LEAD_IN
    for i, (begin, finish) in enumerate(spans):
        starts.append(begin + shift)
        ends.append(finish + shift)
        pieces.append((cuts[i], cuts[i + 1], cuts[i] + shift))
        shift += pauses[i]
    total = ends[-1] + TAIL

    n = len(pieces)
    graph = [f"[0:a]asplit={n}" + "".join(f"[s{i}]" for i in range(n))]
    for i, (a, b, at) in enumerate(pieces):
        graph.append(f"[s{i}]atrim=start={a:.3f}:end={b:.3f},"
                     f"asetpts=PTS-STARTPTS,"
                     f"adelay={round(at * 1000)}:all=1[p{i}]")
    graph.append("".join(f"[p{i}]" for i in range(n))
                 + f"amix=inputs={n}:normalize=0,apad[out]")
    track = out_dir / "narration.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(voice),
         "-filter_complex", ";".join(graph), "-map", "[out]",
         "-t", f"{total:.3f}", "-ar", "48000", str(track)], check=True)
    return Timeline(sentences, starts, ends, total, track)
