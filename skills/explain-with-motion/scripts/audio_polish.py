#!/usr/bin/env python3
"""Optional: clean up the speech with Auphonic (needs your own AUPHONIC_API_KEY, free tier = 2 h/month).

Usage:
  python3 audio_polish.py <work-dir>                 -> work/audio/polished.wav + two equally loud listening samples
  python3 audio_polish.py <work-dir> --apply <render.mp4> [--out renders/video_audio.mp4]
                                                     -> swaps the sound of a finished render, picture untouched

Settings: noise and reverb reduction, adaptive leveler, NO voice re-synthesis. Auphonic's "Studio
Voice" filter rebuilds the voice and on normal call/camera sound it stops sounding like the
speaker – use it only for heavily band-limited sources (voice messages), and only if the user asks.
The timeline is never changed (silence/filler cutting off), so picture and graphics stay in sync.
No limiter afterwards – only a gain step; limiters added audible clicks in tests.
"""
import argparse, json, os, subprocess, sys, time
from pathlib import Path
import urllib.request

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402

API = "https://auphonic.com/api"
ALGO = {"silence_cutter": False, "filler_cutter": False, "cough_cutter": False, "music_cutter": False,
        "leveler": True, "levelerstrength": 70, "compressor": "soft", "normloudness": True, "loudnesstarget": -16,
        "maxpeak": -1.0, "loudnessmethod": "dialog", "denoise": True, "denoisemethod": "dynamic", "denoiseamount": 12,
        "deverbamount": 6, "debreathamount": -1, "dehum": 0, "dehumamount": 0, "filtering": True, "filtermethod": "hipfilter"}


def req(method, url, key, data=None, files=None):
    import requests  # noqa
    h = {"Authorization": f"bearer {key}"}
    r = requests.request(method, url, headers=h, json=data, files=files, timeout=600)
    r.raise_for_status()
    return r


def loud(f):
    e = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    j = json.loads(e[e.rindex("{"):e.rindex("}") + 1])
    return float(j["input_i"]), float(j["input_tp"])


ap = argparse.ArgumentParser()
ap.add_argument("work"); ap.add_argument("--apply"); ap.add_argument("--out")
ap.add_argument("--sample", default=None, help="sample window, e.g. 60:90")
a = ap.parse_args()
work = Path(a.work).resolve(); A = work / "audio"; A.mkdir(exist_ok=True)
src = A / "original.wav"; pol = A / "polished.wav"

if not a.apply:
    key = os.environ.get("AUPHONIC_API_KEY") or sys.exit("AUPHONIC_API_KEY is not set (auphonic.com -> Account -> API key)")
    common.run(["ffmpeg", "-v", "error", "-y", "-i", str(work / "clip/clip.mov"), "-vn", "-ac", "1", "-ar", "48000",
                "-c:a", "pcm_s24le", str(src)])
    body = {"metadata": {"title": "explain-with-motion"}, "algorithms": ALGO, "output_basename": "polished",
            "output_files": [{"format": "wav-24bit"}]}
    uuid = req("POST", f"{API}/productions.json", key, data=body).json()["data"]["uuid"]
    with open(src, "rb") as fh:
        req("POST", f"{API}/production/{uuid}/upload.json", key, files={"input_file": fh})
    req("POST", f"{API}/production/{uuid}/start.json", key)
    print("Auphonic is processing ...")
    while True:
        d = req("GET", f"{API}/production/{uuid}.json", key).json()["data"]
        if d["status_string"] == "Done": break
        if d["status_string"] in ("Error", "Incomplete"): sys.exit(f"Auphonic error: {d.get('error_message')}")
        time.sleep(10)
    url = next(o for o in d["output_files"] if o["format"].startswith("wav"))["download_url"]
    r = req("GET", url, key)
    pol.write_bytes(r.content)
    if abs(common.duration(pol) - common.duration(src)) > 0.02:
        sys.exit("duration changed – do not use (would break sync)")
    s0, s1 = (a.sample or f"{min(60, common.duration(src) / 3):.0f}:{min(90, common.duration(src) / 3 + 30):.0f}").split(":")
    for name, f in [("original", src), ("polished", pol)]:
        i, _ = loud(f)
        common.run(["ffmpeg", "-v", "error", "-y", "-ss", s0, "-to", s1, "-i", str(f), "-af", f"volume={-16 - i:.2f}dB",
                    "-c:a", "libmp3lame", "-q:a", "2", str(A / f"sample_{name}.mp3")])
    print(f"done. Listen to {A}/sample_original.mp3 and sample_polished.mp3 (same loudness) and let the user choose.")
else:
    render = Path(a.apply).resolve()
    out = Path(a.out).resolve() if a.out else render.with_name(render.stem + "_audio.mp4")
    total = common.duration(render)
    st = A / "polished_stereo.wav"
    common.run(["ffmpeg", "-v", "error", "-y", "-i", str(pol), "-af", f"pan=stereo|c0=c0|c1=c0,apad=whole_dur={total}",
                "-c:a", "pcm_s24le", str(st)])
    i, tp = loud(st); g = min(-14 - i, -1.0 - tp)
    common.run(["ffmpeg", "-v", "error", "-y", "-i", str(render), "-i", str(st), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", f"volume={g:.2f}dB", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)])
    print(f"{out}  loudness {loud(out)[0]:.1f} LUFS")
