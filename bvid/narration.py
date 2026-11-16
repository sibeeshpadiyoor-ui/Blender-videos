"""Turn a list of narration sentences into a voice track and a timeline.

Uses the same voice as the Beyond the Obvious Physics channel: Kokoro
"am_michael" (American English, male), speed 0.92, with questions given a
rising ending (bvid/prosody.py), a light cleanup filter and loudness
normalisation. It runs offline once the two model files are in `models/`.

A sentence is a string, or (string, pause) to hold longer after it.
Each sentence is synthesized on its own, so the animation can cue visuals
to the exact moment it starts; clips are cached by text and voice.
"""
import hashlib
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
VOICE = os.environ.get("TTS_VOICE", "am_michael")
SPEED = float(os.environ.get("TTS_SPEED", "0.92"))   # 1.0 = normal; lower is slower
LEAD_IN = 0.5         # silence before the first sentence
PAUSE = 0.6           # silence after every sentence
TAIL = 1.5            # hold after the last sentence

# Same cleanup as the channel's episodes: remove rumble, even out the level.
VOICE_FILTER = ("highpass=f=75,"
                "acompressor=threshold=0.10:ratio=2.5:attack=10:release=200:"
                "makeup=1.8,loudnorm=I=-16:TP=-1.5:LRA=8")


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


_KOKORO = None


def _kokoro():
    global _KOKORO
    if _KOKORO is None:
        from kokoro_onnx import Kokoro
        models = ROOT / "models"
        model = Path(os.environ.get("KOKORO_MODEL", models / "kokoro-v1.0.onnx"))
        voices = Path(os.environ.get("KOKORO_VOICES", models / "voices-v1.0.bin"))
        if not model.exists() or not voices.exists():
            raise SystemExit(
                "Kokoro model files are missing. Download kokoro-v1.0.onnx and "
                "voices-v1.0.bin from https://github.com/thewh1teagle/"
                "kokoro-onnx/releases/tag/model-files-v1.0 into models/")
        _KOKORO = Kokoro(str(model), str(voices))
    return _KOKORO


def _trim(x, sr, thresh=0.012, margin=0.05):
    loud = np.where(np.abs(x) > thresh)[0]
    if len(loud) == 0:
        return x
    return x[max(loud[0] - int(margin * sr), 0):
             min(loud[-1] + int(margin * sr), len(x))]


def _sentence(text, cache):
    """One sentence -> (mono float samples, sample rate), cached on disk."""
    import soundfile as sf
    from . import prosody

    key = hashlib.sha1(f"v1|{VOICE}|{SPEED}|{text}".encode()).hexdigest()[:16]
    path = cache / f"{key}.wav"
    if not path.exists():
        samples, sr = _kokoro().create(text, voice=VOICE, speed=SPEED,
                                       lang="en-us")
        samples = prosody.shape(np.asarray(samples, dtype="float32"), sr, text)
        sf.write(str(path), _trim(samples, sr), sr)
    x, sr = sf.read(str(path), dtype="float32")
    return (x if x.ndim == 1 else x.mean(axis=1)), sr


def prepare(sentences, out_dir):
    import soundfile as sf

    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is needed to build the narration track")
    out_dir = Path(out_dir)
    cache = out_dir / "sentences"
    cache.mkdir(parents=True, exist_ok=True)

    extra = [s[1] if isinstance(s, tuple) else 0.0 for s in sentences]
    sentences = [s[0] if isinstance(s, tuple) else s for s in sentences]

    clips = [_sentence(text, cache) for text in sentences]
    sr = clips[0][1]
    starts, ends, pieces, cursor = [], [], [], LEAD_IN
    pieces.append(np.zeros(round(LEAD_IN * sr), dtype="float32"))
    for (x, _), pause in zip(clips, extra):
        starts.append(cursor)
        ends.append(cursor + len(x) / sr)
        pieces.append(x)
        gap = PAUSE + pause
        pieces.append(np.zeros(round(gap * sr), dtype="float32"))
        cursor += len(x) / sr + gap
    total = ends[-1] + TAIL
    pieces.append(np.zeros(round(TAIL * sr), dtype="float32"))

    raw = out_dir / "narration_raw.wav"
    sf.write(str(raw), np.concatenate(pieces), sr)
    track = out_dir / "narration.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw),
                    "-af", VOICE_FILTER, "-ar", "48000", str(track)],
                   check=True)
    return Timeline(sentences, starts, ends, total, track)
