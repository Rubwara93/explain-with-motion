#!/usr/bin/env python3
"""Download a Google Font as woff2 files and print the matching config block.

Usage:
  python3 fetch_font.py "Work Sans" 300,400,500 <project>/assets/fonts [--italic] [--serif] [--subsets latin,latin-ext]

In this skill: paste the printed "faces" into brand.json and prefix every "file" with "assets/".

--italic   also fetch the italic styles of the same weights
--serif    print a serif fallback stack (Georgia) instead of a sans one

File paths in the printed block are relative to the project folder (the parent of
<project>/fonts), so the block can be pasted into <project>/config.json as is.

Google Fonts are under the SIL Open Font License or Apache 2.0, so embedding them
in the HTML file is allowed. Commercial brand fonts need a web licence first.
"""
import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def ssl_context():
    """python.org builds on macOS ship without CA certificates; fall back to certifi or the system bundle."""
    try:
        import certifi  # type: ignore
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    for cafile in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"):
        if os.path.exists(cafile):
            return ssl.create_default_context(cafile=cafile)
    return ssl.create_default_context()


CTX = ssl_context()


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
            return r.read()
    except urllib.error.URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            sys.exit("SSL-Zertifikate fehlen / missing SSL certificates: python3 -m pip install certifi "
                     "(macOS python.org: run 'Install Certificates.command') or use /usr/bin/python3")
        raise


def main():
    argv = sys.argv[1:]
    italic = "--italic" in argv
    serif = "--serif" in argv
    subsets = ["latin", "latin-ext"]
    if "--subsets" in argv:
        i = argv.index("--subsets")
        subsets = argv[i + 1].split(",")
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 3:
        sys.exit(__doc__)
    family, weights, out = args[0], [w.strip() for w in args[1].split(",")], Path(args[2]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    project = out.parent

    if italic:
        axis = "ital,wght@" + ";".join([f"0,{w}" for w in weights] + [f"1,{w}" for w in weights])
    else:
        axis = "wght@" + ";".join(weights)
    css = get(f"https://fonts.googleapis.com/css2?family={urllib.parse.quote(family)}:{axis}&display=swap").decode()

    slug = re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")
    faces, by_url = [], {}
    for sub, block in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*{[^}]*})", css):
        if sub not in subsets:
            continue
        weight = int(re.search(r"font-weight:\s*(\d+)", block).group(1))
        style = re.search(r"font-style:\s*(\w+)", block).group(1)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
        rng = re.search(r"unicode-range:\s*([^;]+);", block)
        if url in by_url:  # variable font: one file serves several weights
            face = by_url[url]
            lo, hi = (face["weight"], face["weight"]) if isinstance(face["weight"], int) else map(int, face["weight"].split())
            face["weight"] = f"{min(lo, weight)} {max(hi, weight)}"
            continue
        fn = out / f"{slug}-{weight}{'-italic' if style == 'italic' else ''}-{sub}.woff2"
        fn.write_bytes(get(url))
        face = {"weight": weight, "style": style, "file": os.path.relpath(fn, project),
                "unicodeRange": rng.group(1).strip() if rng else None}
        by_url[url] = face
        faces.append(face)
    if not faces:
        sys.exit(f"Keine Schrift gefunden / font not found: {family}")
    fallback = "Georgia, 'Times New Roman', serif" if serif else "system-ui, -apple-system, 'Segoe UI', sans-serif"
    print(json.dumps({"family": family, "fallback": fallback, "weight": int(weights[0]), "faces": faces},
                     indent=2, ensure_ascii=False))
    print(f"\n# 'weight' only matters for fonts.display (title, timer, counter). {len(faces)} file(s) in {out}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
