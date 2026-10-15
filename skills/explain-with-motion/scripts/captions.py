#!/usr/bin/env python3
"""Time the corrected caption text against the cut clip.

Usage: python3 captions.py <work-dir> [--check]

Reads  <work-dir>/captions.txt   corrected caption text, written by the agent:
         - stay close to what is said; fix recognition errors, names, terms, punctuation
         - "|" starts a new caption card (one card = one short line pair, ~4-9 words)
         - *word* marks an emphasised word (shown in the accent colour)
       <work-dir>/clip/clip.mov
Writes <work-dir>/captions.json   [[start, end, "text with <b>emphasis</b>"], ...] in clip time
       <work-dir>/captions.srt

The clip is transcribed piecewise (exact word times), the caption words are matched to it, missing
words are interpolated, and every card change is moved into the nearest real speech pause.
--check re-transcribes every card window and lists cards whose text does not match the sound.
"""
import difflib, json, re, statistics, subprocess, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402

work = Path(sys.argv[1])
lang = json.load(open(work / "meta.json")).get("lang", "de")
clip = work / "clip/clip.mov"
dur = common.duration(clip)
wav = common.to_wav16k(clip, work / "clip/clip16k.wav")
cache = work / "clip/chunkwords.json"
if not cache.exists() or cache.stat().st_mtime < clip.stat().st_mtime:
    json.dump(common.chunk_words(wav, lang), open(cache, "w"), ensure_ascii=False)
norm = lambda t: re.sub(r"[^\w]", "", t.lower().replace("ß", "ss"))
src = [(norm(w), s, e) for w, s, e in json.load(open(cache)) if norm(w)]

cards = []
for chunk in (work / "captions.txt").read_text().split("|"):
    toks, emph = [], False
    for raw in chunk.split():
        if raw.lstrip("„\"(").startswith("*"):
            emph = True
        toks.append([raw.replace("*", ""), emph])
        if raw.rstrip(".,:;?!“\")").endswith("*"):
            emph = False
    if toks:
        cards.append(toks)
flat = [t for c in cards for t in c]
a = [norm(t[0]) for t in flat]
cand = [[] for _ in flat]
for blk in difflib.SequenceMatcher(None, a, [x[0] for x in src], autojunk=False).get_matching_blocks():
    for k in range(blk.size):
        cand[blk.a + k].append(src[blk.b + k][1:])
times = [(statistics.median(c[0] for c in cs), statistics.median(c[1] for c in cs)) if cs else None for cs in cand]
known = [i for i, t in enumerate(times) if t]
for i in range(len(times)):
    if times[i] is None:
        p = max([k for k in known if k < i], default=None); n = min([k for k in known if k > i], default=None)
        ts = times[p][1] if p is not None else 0.0
        te = times[n][0] if n is not None else dur - 0.5
        gap = (n if n is not None else len(times)) - (p if p is not None else -1)
        pos = i - (p if p is not None else -1)
        times[i] = (ts + (te - ts) * (pos - 1) / gap, ts + (te - ts) * pos / gap)
print(f"matched {len(known) / max(len(flat), 1):.0%} of caption words to the sound")

seq, idx = [], 0
for c in cards:
    seq.append([times[idx][0], times[idx + len(c) - 1][1], c]); idx += len(c)
for i in range(len(seq)):
    seq[i][0] = max(0.0, seq[i][0] - 0.08)
for i in range(len(seq) - 1):
    nxt = seq[i + 1][0]
    seq[i][1] = nxt if nxt - seq[i][1] < 0.8 else seq[i][1] + 0.35
seq[-1][1] = dur; seq[0][0] = 0.0
pcm = common.load_pcm(wav)
env = common.envelope(pcm, smooth=1)
quiet = env < np.percentile(env, 12) + 9
nfr = len(env)
for i in range(1, len(seq)):
    t = seq[i][0] + 0.08
    lo = max(int((t - 0.3) * 100), int((seq[i - 1][0] + 0.5) * 100)); hi = min(int((t + 0.3) * 100), nfr)
    runs, k = [], lo
    while k < hi:
        if quiet[k]:
            j = k
            while j < nfr and quiet[j]:
                j += 1
            if j - k >= 10:
                runs.append(j / 100)
            k = j
        else:
            k += 1
    if not runs:
        continue
    new = round(min(runs, key=lambda r: abs(r - t)) - 0.06, 2)
    if new <= seq[i - 1][0] + 0.3:
        continue
    if seq[i - 1][1] >= seq[i][0] - 0.01 or seq[i - 1][1] > new:
        seq[i - 1][1] = new
    seq[i][0] = new


def html(c):
    out, open_ = [], False
    for w, e in c:
        if e and not open_: out.append("<b>"); open_ = True
        if not e and open_: out.append("</b>"); open_ = False
        out.append(w + " ")
    if open_: out.append("</b>")
    return "".join(out).replace(" </b>", "</b> ").strip()


res = [[round(s, 2), round(e, 2), html(c)] for s, e, c in seq]
json.dump(res, open(work / "captions.json", "w"), ensure_ascii=False, indent=0)
ts = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round(x % 1 * 1000)) % 1000:03d}"
(work / "captions.srt").write_text("\n".join(f"{i + 1}\n{ts(s)} --> {ts(e)}\n{' '.join(w for w, _ in c)}\n"
                                             for i, (s, e, c) in enumerate(seq)))
print(f"{len(res)} cards -> captions.json / captions.srt")
for i, (s, e, t) in enumerate(res):
    plain = re.sub("<[^>]+>", "", t)
    if e - s < 1.0 or len(plain) / max(e - s, 0.01) > 26:
        print(f"  too fast #{i:03d} {s:7.2f}-{e:7.2f} ({e - s:.2f}s): {plain}   -> merge with a neighbour card")

if "--check" in sys.argv:
    bad = 0
    for i, (s, e, t) in enumerate(res):
        plain = re.sub("<[^>]+>", "", t)
        heard = common.whisper_text(clip, lang, s, e)
        r = difflib.SequenceMatcher(None, norm(plain), norm(heard)).ratio()
        if r < 0.5:
            bad += 1
            print(f"  check #{i:03d} {s:7.2f}-{e:7.2f} r={r:.2f}\n     CARD: {plain}\n     HEARD: {heard}")
    print(f"check: {bad} suspicious of {len(res)} (short cards often look suspicious only because whisper misses edge words)")
