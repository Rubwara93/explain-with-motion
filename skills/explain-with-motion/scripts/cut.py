#!/usr/bin/env python3
"""Cut the chosen passage out of the recording: segments joined, cut points placed on real pauses.

Usage: python3 cut.py <work-dir>/cut.json

cut.json:
  {
    "segments":  [[1348.24, 1432.11], [1440.01, 1443.43], ...],   # seconds in the ORIGINAL recording,
                                                               # start = first word, end = last word
    "overrides": [[0, 1347.88, null], [1, 1439.68, null]],       # optional hand-measured cut points
                                                                 # [segment index, start|null, end|null];
                                                                 # starts are floored to the frame grid
                                                                 # (up to 1 frame earlier) – measure with
                                                                 # a few ms of headroom after the dip
    "fps": 25,                                                   # optional, default: source fps
    "loudness": -14                                              # optional, LUFS
  }

Writes <work-dir>/clip/: clip.mov (H.264 + PCM, loudness-normalised), timemap.json, words.json (clip time).

How cut points are found: whisper word edges are only approximate, so each cut is moved onto the
audio itself. Before a segment the cut sits LEAD seconds before the speech onset if there is a real
pause; inside running speech it goes into the deepest level dip between the two words. After a
segment the cut sits TAIL after the word ends (END_TAIL on the very last segment, so the final
syllable can ring out). Every seam gets a 10-40 ms fade so nothing clicks.
"""
import json, subprocess, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402

LEAD, TAIL, END_TAIL = 0.10, 0.12, 0.65

cfg_path = Path(sys.argv[1])
work = cfg_path.parent
cfg = json.load(open(cfg_path))
meta = json.load(open(work / "meta.json"))
SRC = meta["recording"]
words = json.load(open(work / "words.json"))
pcm = common.load_pcm(work / "source16k.wav")
env = common.envelope(pcm)
FLOOR = np.percentile(env, 10)
OFF = FLOOR + 10

src_fps = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                          "-of", "csv=p=0", SRC], capture_output=True, text=True).stdout.strip()
num, den = (src_fps.split("/") + ["1"])[:2]
FPS = cfg.get("fps") or round(float(num) / float(den))


def quiet_runs(a, b, need):
    runs, i = [], a
    while i < b:
        if env[i] < OFF:
            j = i
            while j < b and env[j] < OFF:
                j += 1
            if j - i >= need:
                runs.append((i, j))
            i = j
        else:
            i += 1
    return runs


def onset(t, prev_end):
    a = int((min(t, prev_end) - 0.25) * 100); b = int((t + 0.15) * 100)
    runs = quiet_runs(a, b, 8)
    if runs:
        qs, qe = runs[-1]
        return max(qe / 100 - LEAD, qs / 100), False
    return (a + int(np.argmin(env[a:b]))) / 100, True


def offset(t, next_start, tail):
    a = int((t - 0.2) * 100); b = int((max(t, next_start) + 0.25) * 100)
    runs = quiet_runs(a, b, 12)
    if runs:
        qs, qe = runs[0]
        return min(qs / 100 + tail, max(qe / 100 - 0.05, qs / 100 + 0.06)), False
    return (a + int(np.argmin(env[a:b]))) / 100, True


segs = cfg["segments"]
over = {int(k): (s, e) for k, s, e in cfg.get("overrides", [])}
spans, fades = [], []
for k, (a, b) in enumerate(segs):
    wi = min(range(len(words)), key=lambda i: abs(words[i]["start"] - a))
    wo = min(range(len(words)), key=lambda i: abs(words[i]["end"] - b))
    s, din = onset(words[wi]["start"], words[max(wi - 1, 0)]["end"])
    e, dout = offset(words[wo]["end"], words[min(wo + 1, len(words) - 1)]["start"],
                     END_TAIL if k == len(segs) - 1 else TAIL)
    os_, oe = over.get(k, (None, None))
    if os_ is not None: s, din = os_, True
    if oe is not None: e, dout = oe, True
    s = np.floor(s * FPS) / FPS
    d = round((e - s) * FPS) / FPS
    spans.append((round(s, 3), round(s + d, 3)))
    fades.append((din, dout))

out = work / "clip"; out.mkdir(exist_ok=True)
tm, t = [], 0.0
for s, e in spans:
    tm.append([s, e, round(t, 3)]); t += e - s
json.dump(tm, open(out / "timemap.json", "w"), indent=1)
cw = []
for s, e, o in tm:
    for w in words:
        if w["start"] >= s - 0.2 and w["end"] <= e + 0.3 and w["start"] < e:
            cw.append({"text": w["text"], "start": round(o + max(w["start"], s) - s, 3),
                       "end": round(o + min(w["end"], e) - s, 3), "src": w["start"]})
json.dump(cw, open(out / "words.json", "w"), ensure_ascii=False)

fc, cat = [], ""
for i, (s, e) in enumerate(spans):
    d = e - s
    fi = 0.04 if fades[i][0] else 0.01
    fo = (0.12 if i == len(spans) - 1 else 0.04) if fades[i][1] else 0.01
    fc.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}]")
    fc.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d={fi},afade=t=out:st={d - fo:.3f}:d={fo}[a{i}]")
    cat += f"[v{i}][a{i}]"
fc.append(f"{cat}concat=n={len(spans)}:v=1:a=1[vc][ac]")
fc.append("[vc]scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1[vo]")
raw = out / "cut_raw.mov"
common.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[vo]", "-map", "[ac]",
            "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-fps_mode", "cfr", "-r", str(FPS),
            "-c:a", "pcm_s16le", "-ar", "48000", str(raw)])
L = cfg.get("loudness", -14)
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", f"loudnorm=I={L}:TP=-1.5:LRA=11:print_format=json",
                    "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
ln = (f"loudnorm=I={L}:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
common.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-c:v", "copy", "-af", ln, "-ar", "48000", "-c:a", "pcm_s16le",
            str(out / "clip.mov")])
raw.unlink()
print(f"clip.mov: {t:.2f} s, {len(spans)} segments @ {FPS} fps")
for (s, e), (fi, fo) in zip(spans, fades):
    print(f"   {common.fmt(s)} - {common.fmt(e)}" + ("  [dip cut IN]" if fi else "") + ("  [dip cut OUT]" if fo else ""))
print("Next: python3 probe.py seams", work)
