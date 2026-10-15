  // ── timeline helpers (all times are seconds on the clip timeline) ──
  // Every helper uses fromTo with the hidden state first, so elements stay invisible until their cue
  // even when the renderer seeks backwards or jumps.
  const FPS = {{FPS}};
  const Q = (t) => Math.round(t * FPS) / FPS;                       // snap to frames
  const fin = (s, t, d = 0.6, y = 18) => tl.fromTo(s, { opacity: 0, y }, { opacity: 1, y: 0, duration: d, ease: "power2.out" }, Q(t));
  const fade = (s, t, d = 0.5) => tl.fromTo(s, { opacity: 0 }, { opacity: 1, duration: d, ease: "power1.out" }, Q(t));
  const fout = (s, t, d = 0.4) => tl.to(s, { opacity: 0, duration: d, ease: "power1.in" }, Q(t));
  const pop = (s, t, d = 0.55) => tl.fromTo(s, { opacity: 0, scale: 0.82 }, { opacity: 1, scale: 1, duration: d, ease: "power3.out" }, Q(t));
  const grow = (s, t, d = 0.5) => tl.fromTo(s, { scaleX: 0 }, { scaleX: 1, duration: d, ease: "power2.out" }, Q(t));
  // draw an SVG stroke from its start. dasharray/offset LONGER than the path, otherwise a round cap
  // leaves a dot (or a dash) visible before the line is drawn.
  const draw = (s, t, d = 0.8) => document.querySelectorAll(s).forEach((el) => {
    const L = el.getTotalLength();
    tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.04 }, Q(t));
    tl.fromTo(el, { strokeDasharray: L + 2, strokeDashoffset: L + 4 }, { strokeDashoffset: 0, duration: d, ease: "power2.inOut" }, Q(t));
  });
  // expanding ring(s) around a point; ring elements must start with opacity="0" in the markup
  const pulse = (s, t, origin, { scale = 2.4, d = 1.3, repeat = 1, stagger = 0.45 } = {}) =>
    document.querySelectorAll(s).forEach((el, i) => tl.fromTo(el, { opacity: 0.9, scale: 1 },
      { opacity: 0, scale, duration: d, ease: "power1.out", repeat, immediateRender: false, svgOrigin: origin }, Q(t + i * stagger)));
  // morph an SVG path (same number of points in both shapes), e.g. a jagged stress line going calm
  const morph = (s, t, d, attrs, d2 = 1.4) => tl.to(s, { attr: { d }, ...attrs, duration: d2, ease: "power2.inOut" }, Q(t));
  // fade a whole scene out just before its clip ends
  const sceneOut = (id, end) => fout(`#${id} > .sc`, end - 0.4, 0.4);
  // hand-drawn "line boil" for figures with class="boil" (8 new noise seeds per second)
  const boil = (a, b) => { let k = 0; for (let t = a; t < b; t += 0.125) tl.set("#boilT", { attr: { seed: 1 + (k++ % 7) } }, Q(t)); };
  // centre-based scaling for SVG groups/elements that pop in
  const centre = (s) => gsap.set(s, { transformOrigin: "50% 50%" });
  // people: FIG.person(id, fill, {brows}) returns SVG markup; brows/mouth can be animated later
  const person = (hostId, fill, opts) => { document.getElementById(hostId).innerHTML = FIG.person(hostId + "f", fill, opts); };
  const worry = (hostId, t) => {
    tl.to(`#${hostId}f-browL, #${hostId}f-browR`, { opacity: 1, duration: 0.3 }, Q(t));
    tl.to(`#${hostId}f-mouth`, { attr: { d: "M -14 -104 Q 0 -112 14 -104" }, duration: 0.4, ease: "power1.inOut" }, Q(t));
  };
  const relax = (hostId, t) => {
    tl.to(`#${hostId}f-browL, #${hostId}f-browR`, { opacity: 0, duration: 0.3 }, Q(t));
    tl.to(`#${hostId}f-mouth`, { attr: { d: "M -14 -110 Q 0 -100 14 -110" }, duration: 0.4, ease: "power1.inOut" }, Q(t));
  };
