#!/usr/bin/env python3
"""Check, render and verify the video.

Usage: python3 render.py <project-dir> [--out renders/video.mp4] [--snap 12,48,90] [--no-render]

1. python3 tools/build.py, then `hyperframes check` (stops on errors)
2. optional snapshots (--snap t1,t2,…) -> contact sheet path printed, look at it before rendering
3. render with long ffmpeg timeouts (a 5-minute clip has ~8000 frames; the default 5-min extraction
   limit is too short) and hardware GPU mode
4. verify: duration, picture/sound offset against the clip at three points (expect 0 ms),
   frozen-video check, integrated loudness
"""
import argparse, json, os, subprocess, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--out", default="renders/video.mp4")
ap.add_argument("--snap", default=None)
ap.add_argument("--no-render", action="store_true")
a = ap.parse_args()
P = Path(a.project).resolve()
pkg = json.load(open(P / "package.json")) if (P / "package.json").exists() else {}
ver = "latest"
for v in pkg.get("scripts", {}).values():
    if "hyperframes@" in v:
        ver = v.split("hyperframes@")[1].split()[0]; break
HF = ["npx", "--yes", f"hyperframes@{ver}"]

common.run([sys.executable, str(P / "tools/build.py"), str(P)])
chk = subprocess.run(HF + ["check"], cwd=P, capture_output=True, text=True)
lines = [l for l in chk.stdout.splitlines() if any(k in l for k in ("✗", "⚠", "error(s)", "Check"))
         and "nested_structure_needs_subcomposition" not in l and "timeline_track_too_dense" not in l]
print("\n".join(lines))
if "Check failed" in chk.stdout:
    sys.exit("check failed – fix the errors listed above (full report: npx hyperframes check)")
if a.snap:
    s = subprocess.run(HF + ["snapshot", ".", "--at", a.snap], cwd=P, capture_output=True, text=True).stdout
    print("\n".join(l.strip() for l in s.splitlines() if "contact-sheet" in l))
if a.no_render:
    sys.exit(0)

out = P / a.out
out.parent.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, FFMPEG_PROCESS_TIMEOUT_MS="3600000", PRODUCER_FFMPEG_PROCESS_TIMEOUT_MS="3600000",
           PRODUCER_BROWSER_GPU_MODE="hardware")
fps = json.load(open(P / "project.json")).get("fps", 25)
r = subprocess.run(HF + ["render", ".", "-o", str(out), "--fps", str(fps)], cwd=P, env=env, capture_output=True, text=True)
(P / "renders/render.log").write_text(r.stdout + r.stderr)
if r.returncode != 0 or not out.exists():
    sys.exit("render failed – see renders/render.log")

clip = P / "assets/video/clip.mp4"
print(f"\nrendered {out}  {common.duration(out):.2f}s")


def pcm(f, ss, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(t), "-i", str(f), "-ac", "1", "-ar", "8000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(float)


cd = common.duration(clip)
for ss in (min(20, cd * 0.1), cd * 0.5, max(cd - 20, cd * 0.9)):
    x, y = pcm(out, ss, 4), pcm(clip, ss, 4)
    n = min(len(x), len(y))
    if n < 1000:
        continue
    c = np.correlate(x[:n][400:-400], y[:n], "valid")
    print(f"  sync @{ss:6.1f}s: offset {(np.argmax(c) - 400) / 8:.1f} ms")
v = json.load(open(P / "project.json"))
vx, vy, vw, vh = {"4:5": (0, 0, 1080, 608), "9:16": (0, 0, 1080, 608), "16:9": (0, 120, 1080, 608)}[v.get("layout", "4:5")]
sc = subprocess.run(["ffmpeg", "-v", "error", "-t", str(cd), "-i", str(out), "-vf",
                     f"crop={vw}:{vh}:{vx}:{vy},scale=108:61,select='gt(scene,0.002)',metadata=print:file=-", "-f", "null", "-"],
                    capture_output=True, text=True).stdout.count("pts_time")
print(f"  video frames that change: {sc} of ~{int(cd * fps)} (a frozen clip would show only a handful)")
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(out), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
i = [l for l in m.splitlines() if l.strip().startswith("I:")]
print(f"  loudness {i[-1].strip() if i else '?'}")
