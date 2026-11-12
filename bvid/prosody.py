"""Expression for the narrator: rising question endings and emphatic words.

Kokoro reads "Right?" and "Why not?" with a falling ending, so questions sound like statements, and a
one-word "Wrong." sounds flat. This edits the pitch contour (Praat PSOLA, via parselmouth) of one sentence:

* question (?):   the last part of the sentence glides upward (yes/no and tag questions more than wh-questions)
* emphasis (!) or a one-word statement:  higher, wider pitch, a little louder and slower

If parselmouth is not installed the sentence is returned unchanged.
"""
import re

import numpy as np

WH = {"why", "what", "where", "when", "who", "whom", "whose", "which", "how"}


def classify(text):
    t = text.strip()
    words = re.findall(r"[A-Za-z']+", t)
    if t.endswith("?"):
        first = words[0].lower() if words else ""
        # "Why not?" / "Where does the mass go?" -> wh-question; everything else rises more
        return "wh" if first in WH and len(words) > 2 else ("whshort" if first in WH else "yn")
    if t.endswith("!") or (len(words) == 1 and t.endswith(".")):
        return "emph"
    return "plain"


def _tiers(snd):
    from parselmouth.praat import call
    manip = call(snd, "To Manipulation", 0.01, 60, 320)
    tier = call(manip, "Extract pitch tier")
    n = call(tier, "Get number of points")
    ts = np.array([call(tier, "Get time from index", i + 1) for i in range(n)])
    vs = np.array([call(tier, "Get value at index", i + 1) for i in range(n)])
    return manip, ts, vs


def _apply(snd, manip, ts, new_vs, dur_factor=1.0):
    from parselmouth.praat import call
    new = call("Create PitchTier", "p", snd.xmin, snd.xmax)
    for t, v in zip(ts, new_vs):
        call(new, "Add point", float(t), float(v))
    call([manip, new], "Replace pitch tier")
    if dur_factor != 1.0:
        dt = call("Create DurationTier", "d", snd.xmin, snd.xmax)
        call(dt, "Add point", snd.xmin, dur_factor)
        call([manip, dt], "Replace duration tier")
    return call(manip, "Get resynthesis (overlap-add)")


def shape(x, sr, text):
    kind = classify(text)
    if kind == "plain":
        return x
    try:
        import parselmouth
    except ImportError:
        return x
    snd = parselmouth.Sound(x.astype("float64"), sampling_frequency=sr)
    manip, ts, vs = _tiers(snd)
    if len(ts) < 6:
        return x
    st = 12 * np.log2(vs / np.median(vs))
    t0, t1 = ts[0], ts[-1]
    pos = (ts - t0) / max(t1 - t0, 1e-6)
    dur = 1.0
    if kind in ("yn", "wh", "whshort"):
        rise = {"yn": 8.0, "wh": 5.0, "whshort": 6.0}[kind]
        start = {"yn": 0.45, "wh": 0.6, "whshort": 0.35}[kind]
        ramp = np.clip((pos - start) / (1 - start), 0, 1) ** 1.6
        st = st + rise * ramp
        dur = 1.04
    else:  # emphasis
        med = 0.0
        st = med + (st - med) * 1.35 + 2.5
        dur = 1.12
    new_vs = np.median(vs) * 2 ** (st / 12)
    y = _apply(snd, manip, ts, new_vs, dur)
    y = np.asarray(y.values[0], dtype="float32")
    if kind == "emph":
        y = y * 1.25
    return y
