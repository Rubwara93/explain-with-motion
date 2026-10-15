#!/usr/bin/env python3
"""Assemble index.html from the project's sources.

Usage: python3 build.py <project-dir>      (new_project.py copies this script to <project>/tools/build.py)

Inputs in <project-dir>:
  project.json            layout, fps, clip duration, lower third, footer, end card
  brand.json              colours, fonts, logo, name
  captions.json           [[start, end, html], ...] (from captions.py) – optional
  src/scenes.html         scene markup (one <div class="clip scene"> per scene)
  src/scenes.js           scene animation, uses the helpers (fin, pop, draw, …) and `tl`
  src/scenes.css          optional extra CSS
  src/template/           shell.html, helpers.js, figures.js (copied from the skill)

Everything is inlined into index.html: the HyperFrames renderer does not load local helper scripts
other than GSAP, and scripts outside the composition root never run in the render.
"""
import html, json, sys
from pathlib import Path

P = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
proj = json.load(open(P / "project.json"))
brand = json.load(open(P / "brand.json"))
T = P / "src/template"

LAYOUTS = {
    # canvas, video box, caption strip, graphics panel, footer  (x, y, w, h)
    "4:5": dict(W=1080, H=1350, video=(0, 0, 1080, 608), caps=(0, 608, 1080, 108), panel=(0, 716, 1080, 572),
                foot=(0, 1288, 1080, 62), capfont=31, lt=(24, 496)),
    "9:16": dict(W=1080, H=1920, video=(0, 0, 1080, 608), caps=(0, 608, 1080, 128), panel=(0, 736, 1080, 1024),
                 foot=(0, 1760, 1080, 70), capfont=34, lt=(24, 496)),
    "16:9": dict(W=1920, H=1080, video=(0, 120, 1080, 608), caps=(0, 728, 1080, 150), panel=(1080, 0, 840, 1010),
                 foot=(0, 1010, 1920, 70), capfont=32, lt=(24, 608)),
}
L = LAYOUTS[proj.get("layout", "4:5")]
W, H = L["W"], L["H"]
fps = proj.get("fps", 25)
clip_dur = float(proj["clip_duration"])
ec = proj.get("endcard") or {}
ec_len = float(ec.get("seconds", 0)) if ec else 0.0
ec_start = round(clip_dur - 0.26, 2)
dur = round(clip_dur + ec_len, 2) if ec_len else clip_dur


def box(sel, b, extra=""):
    x, y, w, h = b
    return f"{sel}{{left:{x}px;top:{y}px;width:{w}px;height:{h}px;{extra}}}"


geo = "\n".join([box("#vwrap", L["video"]), box("#capstrip", L["caps"]), box("#panelbg", L["panel"]),
                 box(".scene", L["panel"]),
                 box("#foot", L["foot"]), f".cap{{font-size:{L['capfont']}px}}",
                 f"#lt{{left:{L['lt'][0]}px;top:{L['lt'][1]}px}}"])
if not proj.get("captions", True):
    geo += "\n#capstrip{display:none}"
panel_h = L["panel"][3]

c = brand["colors"]
names = ["paper", "paper2", "ink", "muted", "line", "primary", "primary-dark", "primary-light", "primary-lighter",
         "accent", "accent-light", "accent-text"]
brandvars = "\n".join(f"  --{n}:{c[n.replace('-', '_')]};" for n in names)

faces = []
for role in ("display", "text"):
    f = brand["fonts"][role]
    for fc in f["faces"]:  # same shape as the output of fetch_font.py
        rng = f'unicode-range:{fc["unicodeRange"]};' if fc.get("unicodeRange") else ""
        faces.append(f'@font-face{{font-family:"{f["family"]}";src:url("{fc["file"]}") format("woff2");'
                     f'font-weight:{fc["weight"]};font-style:{fc.get("style", "normal")};font-display:block;{rng}}}')

lt = proj.get("lower_third")
lt_start = float(lt.get("start", 0.6)) if lt else 0.6
lt_end = lt_start + float(lt.get("duration", 6.0)) if lt else 6.6
lower = (f'  <div id="lt" class="clip" data-start="{lt_start}" data-duration="{round(lt_end - lt_start, 2)}" data-track-index="2"><div class="bar"></div>'
         f'<div class="n">{html.escape(lt["name"])}</div><div class="r">{html.escape(lt.get("role", ""))}</div></div>') if lt else ""
if lt and lt.get("position") == "top-left":   # use when the footage has burned-in name labels bottom-left (Zoom, Riverside)
    geo += f"\n#lt{{left:24px;top:{L['video'][1] + 24}px}}"
logo = brand.get("logo")
foot_right = (f'<img src="{logo}" alt="" />' if logo else "") + html.escape(brand.get("name", ""))
footer = (f'  <div id="foot" class="clip" data-start="0" data-duration="{clip_dur}" data-track-index="2"><div class="line"></div>'
          f'<div class="l">{html.escape(proj.get("footer_left", ""))}</div><div class="rr">{foot_right}</div></div>')

endcard = ""
if ec_len:
    parts = []
    if ec.get("logo", logo):
        parts.append(f'<img src="{ec.get("logo", logo)}" alt="" style="height:{ec.get("logo_height", 140)}px" />')
    if ec.get("eyebrow"): parts.append(f'<div class="eb">{html.escape(ec["eyebrow"])}</div>')
    if ec.get("headline_html"): parts.append(f'<div class="hl">{ec["headline_html"]}</div>')
    if ec.get("subline"): parts.append(f'<div class="sl">{html.escape(ec["subline"])}</div>')
    cta = ec.get("cta")
    if cta:
        parts.append('<div class="div"></div>')
        if cta.get("before"): parts.append(f'<div class="ct">{html.escape(cta["before"])}</div>')
        if cta.get("highlight"): parts.append(f'<div class="ch">{html.escape(cta["highlight"])}</div>')
        if cta.get("after"): parts.append(f'<div class="ct">{html.escape(cta["after"])}</div>')
        if cta.get("logo"): parts.append(f'<img src="{cta["logo"]}" alt="" style="height:{cta.get("logo_height", 41)}px;margin-top:16px" />')
    endcard = (f'  <div id="endcard" class="clip" data-start="{ec_start}" data-duration="{round(dur - ec_start, 2)}" data-track-index="6">'
               f'<div id="ecin">{"".join(parts)}</div></div>')

# captions: prefer the work dir's file (re-running captions.py there is picked up automatically)
cap_src = Path(proj["work"]) / "captions.json" if proj.get("work") and (Path(proj["work"]) / "captions.json").exists() else P / "captions.json"
caps = json.load(open(cap_src)) if cap_src.exists() else []
read = lambda p: (P / p).read_text() if (P / p).exists() else ""
helpers = (T / "helpers.js").read_text().replace("{{FPS}}", str(fps))
out = (T / "shell.html").read_text()
rep = {
    "LANG": proj.get("lang", "en"), "W": W, "H": H, "DUR": dur, "CLIPDUR": clip_dur, "EC_START": ec_start,
    "FONTFACES": "\n".join(faces), "BRANDVARS": brandvars, "PAPER": c["paper"], "GEOCSS": geo,
    "DISPLAY": brand["fonts"]["display"]["family"], "TEXT": brand["fonts"]["text"]["family"],
    "LOWER_THIRD": lower, "FOOTER": footer, "ENDCARD": endcard,
    "SCENES_HTML": read("src/scenes.html"), "SCENES_CSS": read("src/scenes.css"), "SCENES_JS": read("src/scenes.js"),
    "FIGURES_JS": (T / "figures.js").read_text(), "HELPERS_JS": helpers,
    "LT_IN": lt_start + 0.1, "LT_OUT": lt_end - 0.5,
    "CAPS": json.dumps(caps, ensure_ascii=False), "PANEL_W": L["panel"][2], "PANEL_H": panel_h,
}
for k, v in rep.items():
    out = out.replace("{{" + k + "}}", str(v))
(P / "index.html").write_text(out)
print(f"index.html  {W}x{H}  {dur:.2f}s  (clip {clip_dur:.2f}s, end card {ec_len:.1f}s)  panel {L['panel'][2]}x{panel_h}")
