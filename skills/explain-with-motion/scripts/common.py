"""Shared helpers: audio envelope, whisper.cpp model lookup, chunked word timing.

Why chunked transcription: whisper drifts by up to ~1.5 s over long stretches, and a single
word sometimes gets a multi-second span. Splitting the audio at real pauses into 3-8 s pieces
and transcribing each piece on its own gives word times that stay within a few frames, because
the position of every piece is known exactly and whisper never sees long silence.
"""
import json, os, shutil, subprocess, sys, tempfile, wave
from pathlib import Path

import numpy as np

MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
MODEL_CANDIDATES = [
    Path.home() / ".cache/explain-with-motion/ggml-small.bin",
    Path.home() / ".cache/hyperframes/whisper/models/ggml-small.bin",
]
HOP = 160  # 10 ms at 16 kHz


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def model_path(fetch=False):
    for p in MODEL_CANDIDATES:
        if p.exists() and p.stat().st_size > 100_000_000:
            return p
    if not fetch:
        sys.exit("whisper model missing. Run: python3 scripts/doctor.py --fetch-model")
    dst = MODEL_CANDIDATES[0]
    dst.parent.mkdir(parents=True, exist_ok=True)
    print("Downloading whisper model ggml-small.bin (~470 MB, once) ...")
    run(["curl", "-L", "--fail", "-o", str(dst), MODEL_URL])
    return dst


def to_wav16k(media, out):
    run(["ffmpeg", "-v", "error", "-y", "-i", str(media), "-vn", "-ac", "1", "-ar", "16000", str(out)])
    return out


def load_pcm(wav):
    with wave.open(str(wav)) as wf:
        return np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32)


def envelope(pcm, smooth=3):
    """dB level per 10 ms frame."""
    n = len(pcm) // HOP
    env = 20 * np.log10(np.sqrt((pcm[: n * HOP].reshape(n, HOP) ** 2).mean(1)) + 1e-3)
    if smooth > 1:
        env = np.convolve(env, np.ones(smooth) / smooth, mode="same")
    return env


def duration(media):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(media)], capture_output=True, text=True).stdout
    return float(out.strip())


def chunk_words(wav, lang="de", min_chunk=300, max_chunk=800):
    """Word list [[text, start, end], ...] from piecewise transcription at real pauses."""
    pcm = load_pcm(wav)
    env = envelope(pcm, smooth=1)
    n = len(env)
    quiet = env < np.percentile(env, 12) + 9
    mids, k = [], 0
    while k < n:
        if quiet[k]:
            j = k
            while j < n and quiet[j]:
                j += 1
            if j - k >= 15:
                mids.append((k + j) // 2)
            k = j
        else:
            k += 1
    cuts, last = [0], 0
    for m in mids:
        if m - last >= min_chunk:
            cuts.append(m)
            last = m
    final = [0]
    for c in cuts[1:] + [n]:
        while c - final[-1] > max_chunk:
            a, b = final[-1] + min_chunk, final[-1] + max_chunk
            final.append(a + int(np.argmin(env[a:b])))
        final.append(c)
    final = sorted(set(final))
    tmp = tempfile.mkdtemp(prefix="ewm-")
    files = []
    for i in range(len(final) - 1):
        a, b = final[i], final[i + 1]
        if b - a < 20:
            continue
        f = f"{tmp}/{i:05d}.wav"
        with wave.open(f, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
            w.writeframes(pcm[a * HOP:b * HOP].astype(np.int16).tobytes())
        files.append((a / 100, f))
    model = str(model_path())
    base = ["whisper-cli", "-m", model, "-l", lang, "-ml", "1", "-sow", "-oj", "-np"]
    for i in range(0, len(files), 150):
        args = list(base)
        for _, f in files[i:i + 150]:
            args += ["-f", f]
        subprocess.run(args, capture_output=True)
    out = []
    for off, f in files:
        try:
            js = json.load(open(f + ".json"))
        except FileNotFoundError:
            continue
        for x in js["transcription"]:
            t = x["text"].strip()
            if t:
                out.append([t, round(off + x["offsets"]["from"] / 1000, 3), round(off + x["offsets"]["to"] / 1000, 3)])
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def whisper_text(wav_or_media, lang="de", t0=None, t1=None, pad=0.4):
    """Plain transcription of a (short) window, for spot checks."""
    tmp = tempfile.mkdtemp(prefix="ewm-")
    f = f"{tmp}/w.wav"
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if t0 is not None:
        cmd += ["-ss", str(t0)]
    if t1 is not None:
        cmd += ["-to", str(t1)]
    cmd += ["-i", str(wav_or_media), "-ac", "1", "-ar", "16000", "-af", f"adelay=300,apad=pad_dur={pad}", f]
    run(cmd)
    subprocess.run(["whisper-cli", "-m", str(model_path()), "-l", lang, "-nt", "-np", "-otxt", "-f", f], capture_output=True)
    txt = open(f + ".txt").read().strip().replace("\n", " ") if os.path.exists(f + ".txt") else "?"
    shutil.rmtree(tmp, ignore_errors=True)
    return txt


def fmt(s):
    return f"{int(s // 60):02d}:{s % 60:05.2f}"
