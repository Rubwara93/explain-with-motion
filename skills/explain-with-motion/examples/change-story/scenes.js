  // ── Figuren einsetzen ──
  const PF = ["#6f9fc4", "#a3c3da", "#f8c595", "#cfe0ee", "#9b9388", "#a3c3da"];
  for (let i = 0; i < 5; i++) document.getElementById("pp" + i).innerHTML = FIG.person("pp" + i + "f", PF[i]);
  for (let i = 0; i < 6; i++) document.getElementById("dq" + i).innerHTML = FIG.person("dq" + i + "f", PF[i]);
  for (let i = 0; i < 5; i++) document.getElementById("zq" + i).innerHTML = FIG.person("zq" + i + "f", PF[i]);
  document.getElementById("zp").innerHTML = FIG.person("zpf", "#6f9fc4", { brows: true });
  document.getElementById("af").innerHTML = FIG.person("aff", "#a3c3da", { brows: true });

  // Häkchen-Raster (S8)
  let ch = "";
  for (let i = 0; i < 14; i++) {
    const x = 60 + (i % 7) * 140, y = 404 + Math.floor(i / 7) * 74;
    ch += `<div class="chk ck" style="position:absolute;left:${x}px;top:${y}px;width:52px;height:52px"><svg width="28" height="28" viewBox="0 0 20 20"><path d="M4 10.5 L8.5 15 L16 5.5" fill="none" stroke="#fbfaf8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></div>`;
  }
  document.getElementById("checks").innerHTML = ch;

  // S4-Kacheln (S9): 4 × 3, Kachel 7 ist neu
  let gr = "";
  for (let i = 0; i < 12; i++) {
    const x = 342 + (i % 4) * 102, y = 80 + Math.floor(i / 4) * 102;
    gr += `<div class="tile gt" id="gt${i}" style="left:${x}px;top:${y}px"><svg class="gck" width="40" height="40" viewBox="0 0 20 20" style="opacity:0"><path d="M4 10.5 L8.5 15 L16 5.5" fill="none" stroke="#1b5180" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg></div>`;
  }
  document.getElementById("grid").innerHTML = gr;

  gsap.set("#dp1, #dp2, #dp3, #fi1, #fi2, #f1, #f2, #plus, #rtile, #rplus, #eqA, #eqB, #s14 .lt, #s14 .rt, #notesIc", { transformOrigin: "50% 50%" });

  // ── S0 Training ──
    const NR = [-4, 3, -2, 5, -3, 2, -5];
  NR.forEach((r, i) => tl.fromTo("#n" + i, { opacity: 0, y: -60, rotation: r * 2 }, { opacity: 1, y: 0, rotation: r, duration: 0.7, ease: "power2.out" }, Q(5.6 + i * 0.5)));
  sceneOut("s0", 11.37);

  // ── S1 Covey + S4 ──
  fin("#s1e", 11.5);
  pop("#c1", 15.85, 0.7); fade("#l1", 16.2);
  pop("#c2", 20.65, 0.8); fade("#l2", 21.0);
  pop("#c3", 32.1, 0.9); fade("#l3", 32.5);
  ["#c1", "#c2", "#c3"].forEach((s) => gsap.set(s, { svgOrigin: "540 330" }));
  document.querySelectorAll("#s1 .m").forEach((el, i) => tl.fromTo(el, { opacity: 0, x: 380, y: -120, rotation: 20 }, { opacity: 1, x: 0, y: 0, rotation: (i % 2 ? 6 : -6), duration: 0.8, ease: "power2.inOut" }, Q(43.8 + i * 0.18)));
  tl.fromTo("#s4tile", { opacity: 0, scale: 0.4, rotation: -8 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.7, ease: "power3.out" }, Q(47.9));
  gsap.set(".pr", { svgOrigin: "633 265" });
  document.querySelectorAll(".pr").forEach((el, i) => tl.fromTo(el, { opacity: 0.9, scale: 1 }, { opacity: 0, scale: 2.6, duration: 1.4, ease: "power1.out", repeat: 1, immediateRender: false }, Q(59.2 + i * 0.45)));
  sceneOut("s1", 61.44);

  // ── S2 Raum ──
    for (let i = 0; i < 5; i++) fin("#pp" + i, 63.2 + i * 0.25, 0.7, 30);
  ["#b0", "#b1", "#b2", "#b3", "#b4"].forEach((b, i) => pop(b, 69.5 + i * 0.22, 0.45));
  for (let i = 0; i < 5; i++) {
    tl.to(`#pp${i}f-browL, #pp${i}f-browR`, { opacity: 1, duration: 0.3 }, Q(69.6 + i * 0.2));
    tl.to(`#pp${i}f-mouth`, { attr: { d: "M -14 -104 Q 0 -112 14 -104" }, duration: 0.4, ease: "power1.inOut" }, Q(69.6 + i * 0.2));
  }
  fout("#b0, #b1, #b2, #b3, #b4", 76.4, 0.3);
  fade("#s2h4", 76.75, 0.4); tl.fromTo("#s2angst", { opacity: 0 }, { opacity: 1, duration: 0.4 }, Q(77.5)); grow("#s2ul", 77.8, 0.5);
  sceneOut("s2", 81.89);
  boil(61.44, 81.89);

  // ── S3 Frage ──
  pop("#qcard", 81.95, 0.6);   tl.fromTo("#qtext .w", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.45, ease: "power2.out", stagger: 0.27 }, Q(84.25));
  pop("#a1", 91.45); pop("#a2", 95.75);
  sceneOut("s3", 101.63);

  // ── S4 Venn ──
    tl.fromTo("#vl", { opacity: 0, x: -180 }, { opacity: 1, x: 0, duration: 1.2, ease: "power2.inOut" }, Q(101.8));
  tl.fromTo("#vr", { opacity: 0, x: 180 }, { opacity: 1, x: 0, duration: 1.2, ease: "power2.inOut" }, Q(101.8));
  fade("#vlt", 102.6); fade("#vrt", 102.6);
  pop("#vmid", 106.75);
  sceneOut("s4", 108.87);

  // ── S5 Zukunft ──
    fin("#zp", 109.2, 0.6, 20);
  draw("#zline", 113.6, 1.0); fade("#zhead", 114.5, 0.3); fade("#zl1", 114.0); fade("#zl2", 114.6);
  draw("#zdash", 115.4, 1.2); pop("#zcloud", 116.0, 0.6);
  pop("#zt3", 120.6, 0.5);
  draw("#zb1", 120.9, 0.35); draw("#zb2", 121.3, 0.35);
  tl.to("#zcloud", { y: -6, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: 5 }, Q(116.6));
  fout("#zgrp", 124.3, 0.4);   fin("#eq1", 128.4); fade("#eq2", 129.2); fin("#eq3", 129.65);
  sceneOut("s5", 131.69);
  boil(108.87, 124.7);

  // ── S6 Vertraute ──
  fin("#vh", 133.9, 0.7); grow("#vul", 135.0, 0.6);
  pop("#skc", 137.5, 0.6); fade("#ske", 137.8); fin("#skt", 141.1);
  sceneOut("s6", 144.56);

  // ── S7 iPhone ──
  fin("#phone", 144.6, 0.8, 30); fade("#icons", 145.3, 0.6);
  fin("#iy", 146.95);
  pop("#notesIc", 151.1, 0.5); draw("#notesRing", 151.4, 0.6);
  gsap.set("#pad", { transformOrigin: "293px 191px" });
  tl.fromTo("#pad", { opacity: 0, scale: 0.1 }, { opacity: 1, scale: 1, duration: 1.0, ease: "power3.inOut" }, Q(157.3));
  draw("#padw", 158.6, 0.9);
    sceneOut("s7", 166.07);

  // ── S8 Fragen ──
  pop("#f1", 166.2); draw("#farr", 168.9, 0.5); pop("#f2", 169.4, 0.6);
  fin("#fq1", 177.45, 0.6); fin("#fq2", 179.4, 0.6);
  document.querySelectorAll("#checks .ck").forEach((el, i) => pop(el, 181.4 + i * 0.16, 0.4));
  sceneOut("s8", 184.43);

  // ── S9 Runtergedampft ──
    document.querySelectorAll("#grid .gt").forEach((el, i) => pop(el, 184.6 + i * 0.07, 0.4));
  const order = [0, 5, 10, 3, 8, 1, 11, 4, 9, 2, 7];
  order.forEach((k, j) => {
    const t = Q(186.7 + j * 0.3);
    tl.to("#gt" + k, { backgroundColor: "#cfe0ee", duration: 0.35 }, t);
    tl.to(`#gt${k} .gck`, { opacity: 1, duration: 0.3 }, t);
  });
  tl.to("#gt6", { backgroundColor: "#f28b2d", duration: 0.4 }, Q(190.0));
  tl.to("#grid", { scale: 1.04, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 3, transformOrigin: "540px 227px" }, Q(199.6));
  order.forEach((k, j) => tl.to("#gt" + k, { opacity: 0, scale: 0.3, duration: 0.5, ease: "power2.in" }, Q(204.7 + j * 0.12)));
  tl.to("#gt6", { x: -51, y: 0, scale: 1.7, duration: 1.0, ease: "power2.inOut" }, Q(206.4));
  fin("#glab", 212.85);
  fade("#calm", 210.5, 0.6);
  tl.to("#calm", { attr: { d: "M 60 520 L 120 516 L 180 524 L 240 516 L 300 524 L 360 517 L 420 523 L 480 517 L 540 523 L 600 518 L 660 522 L 720 518 L 780 522 L 840 519 L 900 521 L 960 519 L 1020 520" }, stroke: "#206093", duration: 1.4, ease: "power2.inOut" }, Q(215.5));
  sceneOut("s9", 216.97);

  // ── S10 Handlungsfähigkeit ──
  document.querySelectorAll(".stn").forEach((el, i) => pop(el, 218.4 + i * 0.25, 0.4));
  fade("#hpath", 220.6, 0.4); fade("#hdot", 220.6, 0.3);
  [[400, 400], [630, 360], [850, 316]].forEach(([x, y], i) => tl.to("#hdot", { attr: { cx: x, cy: y }, duration: 0.7, ease: "power2.inOut" }, Q(220.9 + i * 1.1)));
  sceneOut("s10", 225.21);

  // ── S11 Dynamiken ──
  fin("#dh", 225.9, 0.7);
  pop("#dp1", 228.9); pop("#dp2", 230.4); pop("#dp3", 232.35);
  for (let i = 0; i < 6; i++) fin("#dq" + i, 232.6 + i * 0.15, 0.6, 24);
  pop("#db1", 235.55); pop("#db2", 237.0);
  tl.to("#dq1f-browL, #dq1f-browR, #dq4f-browL, #dq4f-browR", { opacity: 1, duration: 0.3 }, Q(235.6));
  sceneOut("s11", 238.38);
  boil(232.4, 238.38);

  // ── S12 Angst will Sicherheit ──
  pop("#hcirc", 238.45, 0.7); fade("#hring", 238.8, 0.6); fin("#af", 238.9, 0.8, 20);
  
  fin("#at", 238.6, 0.7); fin("#as", 239.4, 0.7);
  pop("#home", 256.4, 0.6); fin("#hwl", 257.0);
    tl.to("#hw", { attr: { fill: "#cfe0ee" }, duration: 0.6 }, Q(262.8));
  draw("#crack", 266.1, 0.5);
  tl.to("#hw", { attr: { fill: "#ece8e2", stroke: "#9b9388" }, duration: 0.6 }, Q(266.3));
  sceneOut("s12", 268.05);
  boil(238.38, 268.05);
  boil(315.86, 318.96);

  // ── S13 Vertrautheit → Sicherheit ──
  pop("#fi1", 268.5, 0.7); fin("#fw1", 268.9);
  draw("#fw2", 271.1, 0.5); pop("#fi2", 271.4, 0.7); fin("#fw3", 271.8);
  tl.fromTo("#fring", { opacity: 0.9, scale: 1 }, { opacity: 0, scale: 1.35, duration: 1.4, ease: "power1.out", repeat: 1, immediateRender: false, svgOrigin: "750 210" }, Q(273.1));
  sceneOut("s13", 277.05);

  // ── S14 vertraut – neu – Mehrwert ──
  fade("#cl1", 277.2); document.querySelectorAll("#s14 .lt").forEach((el, i) => pop(el, 277.3 + i * 0.2, 0.5));
  fade("#cl2", 278.6); document.querySelectorAll("#s14 .rt").forEach((el, i) => pop(el, 278.7 + i * 0.2, 0.5));
  fade("#calm2", 280.0, 0.6);
  pop("#eqA", 288.75, 0.4); pop("#eqB", 290.05, 0.4);
  tl.to("#calm2", { attr: { d: "M 120 522 L 180 519 L 240 525 L 300 519 L 360 525 L 420 519 L 480 525 L 540 519 L 600 525 L 660 519 L 720 525 L 780 519 L 840 525 L 900 520 L 960 522" }, stroke: "#206093", duration: 1.6, ease: "power2.inOut" }, Q(291.8));
  tl.fromTo("#npr", { opacity: 0.9, scale: 1 }, { opacity: 0, scale: 1.6, duration: 1.2, ease: "power1.out", repeat: 2, immediateRender: false, svgOrigin: "785 357" }, Q(293.4));
  pop("#plus", 297.15, 0.5);
  draw("#prob", 300.55, 0.35);
  draw("#benefit", 300.9, 0.9); fade("#benhead", 301.7, 0.3);
  fout("#prob", 302.2, 0.3); draw("#fix", 302.4, 0.45);
  sceneOut("s14", 304.2);

  // ── S15 Rahmung ──
  pop("#rtile", 304.4, 0.6);
  draw("#fr1", 306.75, 0.5); fin("#rq1", 306.75);
  draw("#fr2", 308.65, 0.45); fin("#rq2", 308.65);
  draw("#fr3", 309.75, 0.5); fin("#rq3", 309.75);
  draw("#fr4", 311.75, 0.45); fin("#rq4", 311.75);
  pop("#rplus", 312.5, 0.5);
  tl.fromTo("#rring", { opacity: 0.9, scale: 1 }, { opacity: 0, scale: 1.7, duration: 1.3, ease: "power1.out", repeat: 1, immediateRender: false, svgOrigin: "540 270" }, Q(312.7));
  sceneOut("s15", 315.86);

  // ── S16 Schluss: das Team, entspannt ──
  pop("#zbg", 315.9, 0.8);
  for (let i = 0; i < 5; i++) fin("#zq" + i, 316.0 + i * 0.12, 0.6, 24);
  pop("#ztile", 316.6, 0.5);

