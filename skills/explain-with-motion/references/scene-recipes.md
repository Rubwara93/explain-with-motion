# Scene recipes

A catalogue of visual metaphors that worked, each with the scene in `examples/change-story/` that
implements it (HTML in `scenes.html`, animation in `scenes.js`, look for the `S<n>` comment).
Copy, rename the ids, adapt coordinates to the panel size (`PANEL_W` × `PANEL_H`, 1080 × 572 in 4:5).

| Idea in the talk | Picture | Example |
|---|---|---|
| "we collected the team's stressors" | sticky notes dropping in, slightly rotated | S0 |
| a model with zones (control / influence / concern, inner/outer circle) | concentric circles popping in on the word, small notes flying in and landing inside, the key item as an accent tile | S1 |
| "it triggers emotions" | expanding rings (`pulse`) around the item | S1 |
| a group reacts ("everyone went: huh?") | row of people (`FIG.person`), speech bubbles, brows/mouth turn worried (`worry`) | S2 |
| the turning-point question | one coloured card, the question appears word by word | S3 |
| "the answers were…" | two simple icons (form, dashboard) each getting a check badge | S3 |
| old and new overlap a lot | two circles sliding into a big overlap, check in the middle | S4 |
| fear projects into the future | timeline today → future, dashed arc to a storm cloud, lightning, small worried person | S5 |
| a formula | big `Neu = Stress` / `A → B` with the second part in accent colour | S5, S13 |
| a design principle / term | the term as a card title, the short definition underneath | S6 |
| a well-known object as proof | simple line drawing (phone 2007 with app grid), one icon morphs/zooms into the real-world object (legal pad) | S7 |
| the take-away questions | the questions in large italic, then many check marks popping in ("they found lots of familiar things") | S8 |
| "we boiled the big thing down to the one new part" | grid of tiles, all turn familiar (light + check) one by one except one accent tile; the rest shrink away, the accent tile moves to the centre and grows; a jagged stress line morphs flat | S9 |
| "back to the ability to act" | stepping stones with a dot hopping forward | S10 |
| "you need to read the room" | three icons (hand = pick up, arrow = anticipate, eye = see) + people row with "Sorge" / "Angst" bubbles | S11 |
| an emotion and its function | figure in a big primary circle, the emotion as a word + its function in italic; "familiar world" as a house in a circle that cracks | S12 |
| familiarity → safety | house icon → shield icon | S13 |
| the method in three steps | two columns (before / new) of tiles, `=` between the matching rows, pulse on the new tile, `+` badge, an arc from the new tile resolves a lightning mark on the old problem, stress line goes calm | S14 |
| framing questions (why / what / how / what for) | a picture frame drawn side by side, one question per side, the new tile inside gets the `+` | S15 |
| closing callback | the team from the beginning, now relaxed, around the new tile | S16 |

## Building blocks

- **People**: host `<div id="pp0" class="p abs" style="left:…;top:…">` (110×160) or `class="ps"` (80×116),
  fill in JS: `person("pp0", "#a3c3da")`, later `worry("pp0", t)` / `relax("pp0", t)`, and `boil(a, b)`
  over the scene's time range for the hand-drawn wobble.
- **Tiles**: `<div class="tile">` (90×90, accent-light). For SVG tiles use `<rect rx="14">`.
- **Check badge**: `<circle fill="#206093"/>` + `<path d="M … L … L …" stroke="#fbfaf8"/>`.
- **Pulse rings**: three `<circle class="pr" opacity="0">` at the same centre,
  `pulse(".pr", t, "cx cy")`. The `opacity="0"` in the markup matters (see pitfalls).
- **Stress line**: one `<path>` zigzag; `morph("#line", t, "<flat path with the same points>", {stroke: "#206093"})`.
- **Underline under a word**: `<span class="ul">Wort<i id="x"></i></span>` + `grow("#x", t)`.
- **Scene wrapper**: `<div id="s3" class="clip scene" data-start="81.89" data-duration="19.74" data-track-index="3"><div class="sc">…</div></div>`
  and at the end of its JS block `sceneOut("s3", 101.63)`. Scenes follow each other without gaps;
  start/end on phrase boundaries from `captions.json`.
