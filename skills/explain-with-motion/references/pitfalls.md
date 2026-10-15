# Pitfalls (all of these happened)

## Cutting
- **whisper word edges are approximate.** A "start" can be 0.4 s late ("was" got cut off) or include the
  tail of the previous word ("…änderung. Ja"). After `cut.py`, run `probe.py seams`; for a doubtful seam
  look at `probe.py env <recording> t0 t1` (20 ms levels): speech is the high values, a usable cut is
  the deepest dip between two words. Put the hand-measured time into `overrides` and cut again.
- Two segments must not overlap (end of one = start of the next means: merge them into one).
- Remove what only works inside the original conversation: "Becky, you wrote a wonderful article
  about…", "as I said before", greetings, the host's long questions. Keep the host's short turns
  if they carry the story ("…and the focus back on being able to act").
- Video calls show burned-in name labels (bottom-left in Zoom/Riverside). A lower third in the same corner
  covers them only partly – move it with `lower_third.position: "top-left"`.
- Video calls switch to the other person on every "hm". That cannot be fixed without separate
  tracks; it reads as an interview and is fine.

## Captions
- Fast speakers produce cards shorter than 1 s. Merge them with a neighbour in `captions.txt` (remove
  the `|`), otherwise the strip flickers.
- In a flex container, spaces around `<b>` collapse – the template wraps caption HTML in a `<span>`.

## Composition (HyperFrames)
- **Scripts must be inlined.** The renderer loads only GSAP from `assets/vendor`; other local `<script src>`
  files and scripts outside the composition root never run in the render. `build.py` inlines everything.
- **Hidden until cued.** `fromTo` renders its start state immediately – that is why the helpers use it.
  Exception: repeating pulses use `immediateRender:false`; their elements therefore need
  `opacity="0"` in the markup, or the ring sits visibly on screen before the pulse.
- **SVG origin.** For scaling/rotating SVG elements use `svgOrigin:"x y"` (user-space numbers) or
  `centre(sel)` (50% 50% of the element's box). Pixel `transformOrigin` on SVG is box-relative and
  drifts.
- **Unique ids across all scenes.** A label `id="gt7"` collided with tile `gt7` and was shrunk with it.
  Prefix ids per scene (`s9-label`).
- **Drawn lines**: `draw()` uses dasharray/offset longer than the path; with exactly the path length a
  round line cap leaves a dot visible before the line is drawn.
- **Timeline length**: the shell sets a final `tl.set` at the root duration; without it the last frames
  render blank.
- Do not put CSS `transform` on an element you also animate with GSAP x/y/scale (lint
  `gsap_css_transform_conflict`). Set the start state in `fromTo`.
- `hyperframes check` warns `nested_structure_needs_subcomposition` for every scene and sometimes
  `timeline_track_too_dense` – both expected for this monolithic layout; `render.py` hides them. Fix every error and every contrast warning.

## Footage
- Camera/call footage in Chrome looks darker in the shadows unless the transfer characteristic is
  neutral – `new_project.py` re-tags the clip (`transfer_characteristics=2`) and converts to limited range.
- Long clips: the render extracts every frame first; the default 5-minute ffmpeg limit is too short
  for ~8000 frames. `render.py` raises it.

## Sound
- No limiter after Auphonic – it added clicks. Gain only, peak ≤ −1 dBTP.
- Mono speech played as stereo measures ~3 LU louder; measure the final stereo file.
