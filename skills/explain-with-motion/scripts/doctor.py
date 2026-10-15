#!/usr/bin/env python3
"""Check the tools this skill needs and (optionally) fetch the whisper model.

Usage: python3 doctor.py [--fetch-model]
"""
import shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:
    import common  # noqa: E402  (needs numpy)
except ImportError:
    sys.exit("  MISSING python numpy  ->  python3 -m pip install numpy   (then run this check again)")
HF_VERSION = "0.8.161"  # keep in sync with new_project.py --version default

NEED = {
    "ffmpeg": "brew install ffmpeg   (Windows: winget install ffmpeg, Linux: apt install ffmpeg)",
    "ffprobe": "comes with ffmpeg",
    "node": "brew install node   (or https://nodejs.org, version 20+)",
    "npx": "comes with node",
    "whisper-cli": "brew install whisper-cpp   (Linux/Windows: build whisper.cpp, see https://github.com/ggerganov/whisper.cpp)",
}

ok = True
for tool, hint in NEED.items():
    if shutil.which(tool):
        print(f"  ok      {tool}")
    else:
        ok = False
        print(f"  MISSING {tool}  ->  {hint}")
try:
    import numpy  # noqa: F401
    print("  ok      python numpy")
except ImportError:
    ok = False
    print("  MISSING python numpy  ->  pip3 install numpy")

fetch = "--fetch-model" in sys.argv
try:
    p = common.model_path(fetch=fetch)
    print(f"  ok      whisper model ({p})")
except SystemExit:
    ok = False
    print("  MISSING whisper model  ->  python3 scripts/doctor.py --fetch-model")

if shutil.which("npx"):
    r = subprocess.run(["npx", "--yes", f"hyperframes@{HF_VERSION}", "--version"], capture_output=True, text=True)
    print(f"  {'ok     ' if r.returncode == 0 else 'MISSING'} hyperframes {r.stdout.strip()}")

print("\nAll set." if ok else "\nInstall the missing pieces, then run this check again.")
sys.exit(0 if ok else 1)
