#!/usr/bin/env python3
"""Transcribe a whole recording with word timestamps (local whisper.cpp, piecewise at pauses).

Usage: python3 transcribe.py <recording> --work <work-dir> [--lang de]

Writes into <work-dir>:
  source16k.wav     mono 16 kHz copy of the sound (used by cut.py for level analysis)
  words.json        [{"text", "start", "end"}, ...] in seconds of the original recording
  transcript.txt    one sentence per line with [mm:ss.ss] start time, for reading and picking passages
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("recording")
ap.add_argument("--work", required=True)
ap.add_argument("--lang", default="de")
a = ap.parse_args()

work = Path(a.work); work.mkdir(parents=True, exist_ok=True)
wav = common.to_wav16k(a.recording, work / "source16k.wav")
print(f"Transcribing {common.fmt(common.duration(wav))} min ... (roughly 1/10 of real time)")
words = [{"text": t, "start": s, "end": e} for t, s, e in common.chunk_words(wav, a.lang)]
json.dump(words, open(work / "words.json", "w"), ensure_ascii=False)

lines, cur, t0 = [], [], None
for w in words:
    if t0 is None:
        t0 = w["start"]
    cur.append(w["text"])
    if w["text"].rstrip().endswith((".", "?", "!")) or len(cur) > 28:
        lines.append(f"[{common.fmt(t0)}] {' '.join(cur)}"); cur, t0 = [], None
if cur:
    lines.append(f"[{common.fmt(t0)}] {' '.join(cur)}")
(work / "transcript.txt").write_text("\n".join(lines) + "\n")
(work / "meta.json").write_text(json.dumps({"recording": str(Path(a.recording).resolve()), "lang": a.lang}, indent=1))
print(f"{len(words)} words -> {work/'transcript.txt'}")
