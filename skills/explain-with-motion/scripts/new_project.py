#!/usr/bin/env python3
"""Create the HyperFrames project for one video.

Usage: python3 new_project.py <project-dir> --work <work-dir> [--layout 4:5|9:16|16:9] [--lang de]
                              [--version 0.8.161] [--no-fonts]

Does:
  - npx hyperframes init <project-dir> (blank), pinned to one CLI version
  - copies the template (shell, helpers, people figures) to src/template/ and build.py to tools/
  - encodes the cut clip for frame-accurate seeking (keyframe every second, limited range, neutral
    transfer tag – without the tag Chrome darkens the shadows of camera footage)
  - copies captions.json, downloads GSAP (renders must not depend on a CDN)
  - writes project.json and a default brand.json (calm paper look) and fetches its fonts
    Spectral + Work Sans from Google Fonts (SIL Open Font License)
  - writes empty src/scenes.html / src/scenes.js and builds index.html once
"""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import common  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--work", required=True)
ap.add_argument("--layout", default="4:5", choices=["4:5", "9:16", "16:9"])
ap.add_argument("--lang", default=None)
ap.add_argument("--version", default="0.8.161")
ap.add_argument("--no-fonts", action="store_true")
a = ap.parse_args()

P = Path(a.project).resolve(); work = Path(a.work).resolve()
clip = work / "clip/clip.mov"
if not clip.exists():
    sys.exit(f"{clip} missing – run cut.py first")
lang = a.lang or json.load(open(work / "meta.json")).get("lang", "en")

if not P.exists() or not any(P.iterdir()):
    env = dict(os.environ, HYPERFRAMES_SKIP_SKILLS="1")
    common.run(["npx", "--yes", f"hyperframes@{a.version}", "init", str(P), "--example", "blank", "--skip-transcribe",
                "--non-interactive", "--skill", "talking-head-recut"], env=env, stdout=subprocess.DEVNULL)
for d in ["src/template", "tools", "assets/video", "assets/vendor", "assets/fonts", "assets/logos", "renders"]:
    (P / d).mkdir(parents=True, exist_ok=True)
for f in ["shell.html", "helpers.js", "figures.js"]:
    shutil.copy(SKILL / "assets/template" / f, P / "src/template" / f)
shutil.copy(SKILL / "scripts/build.py", P / "tools/build.py")

fps = round(eval(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                                 "-of", "csv=p=0", str(clip)], capture_output=True, text=True).stdout.strip()))
tmp = P / "assets/video/_clip.mp4"
common.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-vf", "scale=in_range=auto:out_range=tv,format=yuv420p",
            "-c:v", "libx264", "-crf", "17", "-g", str(fps), "-keyint_min", str(fps), "-movflags", "+faststart",
            "-c:a", "aac", "-b:a", "192k", str(tmp)])
common.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-c", "copy", "-bsf:v", "h264_metadata=transfer_characteristics=2",
            str(P / "assets/video/clip.mp4")])
tmp.unlink()
clip_dur = round(common.duration(P / "assets/video/clip.mp4"), 3)
if (work / "captions.json").exists():
    shutil.copy(work / "captions.json", P / "captions.json")
if not (P / "assets/vendor/gsap.min.js").exists():
    common.run(["curl", "-sL", "--fail", "-o", str(P / "assets/vendor/gsap.min.js"),
                "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"])

if not (P / "project.json").exists():
    json.dump({
        "layout": a.layout, "fps": fps, "lang": lang, "clip_duration": clip_dur, "captions": True, "work": str(work),
        "lower_third": {"name": "Speaker Name", "role": "in conversation with …", "start": 0.6, "duration": 6.0,
                        "position": "bottom-left"},
        "footer_left": "Speaker Name · Topic of the video",
        "endcard": {"seconds": 5, "eyebrow": "", "headline_html": "Key <em>message</em>.", "subline": "",
                    "cta": None},
    }, open(P / "project.json", "w"), indent=2, ensure_ascii=False)
else:
    pj = json.load(open(P / "project.json")); pj["clip_duration"] = clip_dur; pj["work"] = str(work)
    json.dump(pj, open(P / "project.json", "w"), indent=2, ensure_ascii=False)

if not (P / "brand.json").exists():
    brand = {
        "name": "", "logo": None,
        "colors": {"paper": "#fbfaf8", "paper2": "#f5f3ef", "ink": "#1c2733", "muted": "#756e64", "line": "#ece8e2",
                   "primary": "#206093", "primary_dark": "#1b5180", "primary_light": "#cfe0ee", "primary_lighter": "#eaf1f7",
                   "accent": "#f28b2d", "accent_light": "#fbddc1", "accent_text": "#b25003"},
        "fonts": {"display": {"family": "Spectral", "faces": []}, "text": {"family": "Work Sans", "faces": []}},
    }
    if not a.no_fonts:
        for role, fam, w, extra in [("display", "Spectral", "400,500", ["--italic", "--serif"]), ("text", "Work Sans", "400,500,600", [])]:
            out = subprocess.run([sys.executable, str(SKILL / "scripts/fetch_font.py"), fam, w, str(P / "assets/fonts"), *extra],
                                 capture_output=True, text=True, check=True).stdout
            faces = json.loads(out[out.index("{"):out.rindex("}") + 1])["faces"]
            brand["fonts"][role]["faces"] = [dict(f, file="assets/" + f["file"]) for f in faces]
    json.dump(brand, open(P / "brand.json", "w"), indent=2, ensure_ascii=False)

for f, txt in [("src/scenes.html", "<!-- one <div id=\"sN\" class=\"clip scene\" data-start=… data-duration=… data-track-index=\"3\"><div class=\"sc\">…</div></div> per scene -->\n"),
               ("src/scenes.js", "// scene animation – see references/scene-recipes.md\n"), ("src/scenes.css", "")]:
    if not (P / f).exists():
        (P / f).write_text(txt)
common.run([sys.executable, str(P / "tools/build.py"), str(P)])
print(f"\nProject ready: {P}\n  edit brand.json, project.json, src/scenes.html, src/scenes.js, then: python3 tools/build.py .")
