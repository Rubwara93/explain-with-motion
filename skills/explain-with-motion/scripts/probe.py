#!/usr/bin/env python3
"""Listen-by-proxy tools for cut points.

  python3 probe.py seams <work-dir>                 re-transcribe 2.2 s on both sides of every seam of the cut
  python3 probe.py say <media> <t0> <t1> [--lang de] transcribe one window (e.g. to check a single word)
  python3 probe.py env <media> <t0> <t1>             print the level in 20 ms steps (find pauses / dips)

Use them after cut.py: whisper on a 2-second piece misses or invents words at the very edge,
so read the result as "is the first/last word complete?", not as a perfect transcript.
"""
import json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402

cmd = sys.argv[1]
lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else None

if cmd == "seams":
    work = Path(sys.argv[2])
    lang = lang or json.load(open(work / "meta.json")).get("lang", "de")
    tm = json.load(open(work / "clip/timemap.json"))
    clip = work / "clip/clip.mov"
    for k, (s, e, o) in enumerate(tm):
        d = e - s
        print(f"seg{k} IN : {common.whisper_text(clip, lang, o, o + 2.2)}")
        print(f"seg{k} OUT: {common.whisper_text(clip, lang, o + d - 2.2, o + d)}")
elif cmd == "say":
    print(common.whisper_text(sys.argv[2], lang or "de", float(sys.argv[3]), float(sys.argv[4])))
elif cmd == "env":
    media, t0, t1 = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
    import subprocess
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-to", str(t1), "-i", media, "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32)
    n = len(x) // 320
    e = 20 * np.log10(np.sqrt((x[: n * 320].reshape(n, 320) ** 2).mean(1)) + 1e-3)
    print(" ".join(f"{t0 + i * 0.02:.2f}:{v:.0f}" for i, v in enumerate(e)))
else:
    sys.exit(__doc__)
