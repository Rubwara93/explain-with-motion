---
name: explain-with-motion
description: Turns a passage from a long recording (interview, podcast, Zoom/Riverside call, talk, webinar) in which someone explains an idea into a split-screen explainer video – the speaker on top, captions, and hand-made motion graphics that visualise the explanation underneath – in 4:5, 9:16 or 16:9, rendered locally with HyperFrames. Use this skill whenever someone wants "the part where I explain X" from a recording as a video with animations, graphics, illustrations or a split screen, wants to turn an interview answer, podcast segment or talk excerpt into a LinkedIn/Instagram/YouTube video "with motion graphics", or asks for "a video like the S4/change one" – even if they do not say "split screen" or "HyperFrames". Not for pure captioning, short motion-only clips or videos without a speaker.
---

# Explain with motion

Result: one MP4 in which the speaker stays visible and the panel below draws what they explain.
The explanation stays theirs – the graphics make the structure visible, they do not repeat the words.

Talk to the user in their language, in plain words. They know their content; they may not know video
terms. Show them the plan before you cut and before you build, because cutting and building take
minutes and their feedback is cheapest early.

All scripts live in `scripts/` next to this file. `<skill>` below means this skill's folder.

## 0. Check the machine (once)

```bash
python3 <skill>/scripts/doctor.py --fetch-model
```
Needs ffmpeg, Node 20+, whisper.cpp (`whisper-cli`), Python with numpy. The script names the install
command for anything missing. Everything runs locally; no account is needed (Auphonic is optional, step 8).

## 1. Intake

Ask only what you cannot infer, ideally in one round:
- the recording (path) and **which passage** ("where I talk about the customer and the new software").
- who speaks (names, and the role line for the lower third, e.g. "in conversation with …").
- format: 4:5 feed (default), 9:16 reels, 16:9 YouTube.
- look: their brand (colours, fonts, logo, or a website to read them from) or the calm default.
- end card: key sentence, and optional call to action ("More in the course … at …") with logo.
- what the video is for (a post? a course?) – it decides what the graphics should generalise.

## 2. Transcribe and find the passage

```bash
python3 <skill>/scripts/transcribe.py <recording> --work <work> --lang de
```
Read `<work>/transcript.txt` and locate the passage. Choose it so it stands on its own: start at the
first sentence of the story (not mid-thought), end on a sentence that lands. Then plan the cuts:
remove stumbles, false starts, long "uh"s, side remarks addressed to the host ("you wrote a great
article about …"), anything that needs the original conversation to make sense. Keep short host
turns when they move the story.

Write `<work>/cut.json` (format in the header of `scripts/cut.py`) and **show the user the plan in
plain words** – where it starts and ends, what is removed and why, resulting length. Cut after OK:

```bash
python3 <skill>/scripts/cut.py <work>/cut.json
python3 <skill>/scripts/probe.py seams <work>
```
Read every seam: is the first and last word complete? Fix doubtful seams with
`probe.py env`/`probe.py say` and `overrides` (see `references/pitfalls.md`, Cutting), cut again.

## 3. Captions

Write `<work>/captions.txt` from the transcript of the cut: wording as spoken, recognition errors
fixed (names, terms, umlauts, punctuation), `|` between cards (one card = what fits in two short
lines, roughly 4-9 words, broken at phrase boundaries), `*word*` for the few words worth stressing.
Mark words you could not verify and ask the user about them later instead of guessing silently.

```bash
python3 <skill>/scripts/captions.py <work>          # add --check for a per-card listening check
```
Merge cards the script reports as too fast. If merging would make a card longer than two lines,
move a few words from the fast card to its neighbour instead of merging it whole.

## 4. Scene plan (show before building)

Read `references/design-rules.md` now – the rules there come from real feedback and decide whether the
video feels right. Then plan 12-20 scenes for ~5 minutes (fewer for shorter clips): for each phase of
the story one picture, start/end on phrase boundaries in `captions.json`, every scene following the
previous one without a gap. `references/scene-recipes.md` lists metaphors that worked, with working code.

Show the plan as a short table – time, what is said, what the picture shows – and ask for changes.
Ask explicitly where the speaker places key items in any model they use (e.g. which zone a thing
belongs to): placement is meaning.

## 5. Build

```bash
python3 <skill>/scripts/new_project.py <project> --work <work> --layout 4:5
```
Then edit in `<project>`: `brand.json`, `project.json` (lower third, footer, end card – formats in
`references/brand.md`), and the scenes:

- `src/scenes.html` – one `<div id="sN" class="clip scene" data-start data-duration data-track-index="3"><div class="sc">…</div></div>` per scene, coordinates inside the panel (`PANEL_W`×`PANEL_H`)
- `src/scenes.js` – animation with the helpers `fin, fade, fout, pop, grow, draw, pulse, morph, sceneOut,
  boil, centre, person, worry, relax` on the shared timeline `tl` (all defined in
  `src/template/helpers.js`, times in seconds of the clip)
- `src/scenes.css` – scene-specific CSS

Start from `examples/change-story/` (a complete 5-minute example: read the scene you need, not the whole
file). Rebuild with `python3 tools/build.py .` – never edit `index.html` directly, it is generated.
Captions are read from the work dir, so re-running `captions.py` is picked up by the next build.

Things that are easy to miss:
- **Lower third**: set `lower_third.start` to a moment when the named person is on screen (calls cut to
  whoever speaks). If the footage has burned-in name labels bottom-left (Zoom, Riverside), use
  `"position": "top-left"`.
- **Never an empty panel**: something enters within ~0.5 s of every scene start.
- Call `boil(start, end)` for every time range with people figures; enlarge figures for tall panels
  with CSS (e.g. `#s2 .p svg{width:160px;height:233px}`).
- The last scene needs no `sceneOut` – the end card fades in over it.

## 6. Check and look

```bash
python3 <skill>/scripts/render.py <project> --snap 10,45,90,… --no-render
```
Fix every error and contrast warning. Look at the contact sheet(s) – one frame per scene, taken
right after its last element landed. Check against `references/design-rules.md` §5 (logic of placement)
and `references/pitfalls.md`. Offer the live preview for the user's own look:
`npx hyperframes preview --background` in the project (they can click any element and edit it there).

## 7. Render and verify

```bash
python3 <skill>/scripts/render.py <project> --out renders/<name>.mp4
```
The script reports picture/sound offset (must be 0 ms), whether the video moves, and loudness
(target −14 LUFS). Rendering takes about 1–5× the video length depending on the machine; run it in the
background for longer videos.

## 8. Optional: cleaner sound

Only if the user wants it and has an Auphonic key (`AUPHONIC_API_KEY`):
```bash
python3 <skill>/scripts/audio_polish.py <work>                        # makes equally loud before/after samples
python3 <skill>/scripts/audio_polish.py <work> --apply <render.mp4>   # after the user picked "polished"
```
Never use voice re-synthesis ("studio voice") unless asked – it changes how people sound.

## 9. Hand over

Tell the user where the MP4 (and `captions.srt` for platforms that take subtitle files) is, what you
could not verify (uncertain words), and offer one round of changes. Iterations are cheap now: edit
`src/scenes.*`, rebuild, re-render. Keep earlier renders with a version suffix instead of overwriting.
