/* Simple, friendly people figures (head + body), drawn as SVG markup strings.
   FIG.person(id, fill, {brows:true}) -> <svg>…</svg>. Ids inside: <id>-all, -head, -eyes, -browL, -browR, -mouth.
   Brows start hidden unless {brows:true}; worry()/relax() in helpers.js animate brows and mouth. */
(function () {
  const INK = "#1e1428";
  function person(p, fill, opts = {}) {
    return `
<svg class="fig" viewBox="-110 -210 220 320" width="220" height="320" overflow="visible">
  <ellipse cx="0" cy="98" rx="70" ry="10" fill="#1c2733" opacity=".12"/>
  <g id="${p}-all" class="boil">
    <g id="${p}-armL"><path d="M -50 -40 Q -78 0 -70 40" fill="none" stroke="${INK}" stroke-width="22" stroke-linecap="round"/><path d="M -50 -40 Q -78 0 -70 40" fill="none" stroke="${fill}" stroke-width="11" stroke-linecap="round"/></g>
    <g id="${p}-armR"><path d="M 50 -40 Q 78 0 70 40" fill="none" stroke="${INK}" stroke-width="22" stroke-linecap="round"/><path d="M 50 -40 Q 78 0 70 40" fill="none" stroke="${fill}" stroke-width="11" stroke-linecap="round"/></g>
    <path d="M -46 -66 C -20 -78 20 -78 46 -66 C 60 -58 64 -40 64 -20 L 66 70 C 66 88 54 96 40 96 L -40 96 C -54 96 -66 88 -66 70 L -64 -20 C -64 -40 -60 -58 -46 -66 Z" fill="${fill}" stroke="${INK}" stroke-width="6" stroke-linejoin="round"/>
    <path d="M 40 -60 C 52 -50 56 -30 56 -10" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity=".35"/>
    <g id="${p}-head">
      <circle cx="0" cy="-128" r="48" fill="${fill}" stroke="${INK}" stroke-width="6"/>
      <path d="M 22 -160 C 34 -152 40 -140 40 -126" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity=".35"/>
      <g id="${p}-eyes"><circle cx="-16" cy="-132" r="6.5" fill="${INK}"/><circle cx="16" cy="-132" r="6.5" fill="${INK}"/></g>
      <path id="${p}-browL" d="M -27 -150 Q -16 -153 -6 -150" fill="none" stroke="${INK}" stroke-width="4.5" stroke-linecap="round" opacity="${opts.brows ? 1 : 0}"/>
      <path id="${p}-browR" d="M 6 -150 Q 16 -153 27 -150" fill="none" stroke="${INK}" stroke-width="4.5" stroke-linecap="round" opacity="${opts.brows ? 1 : 0}"/>
      <path id="${p}-mouth" d="M -14 -110 Q 0 -100 14 -110" fill="none" stroke="${INK}" stroke-width="5" stroke-linecap="round"/>
      <circle cx="-30" cy="-114" r="7" fill="#f2a08c" opacity=".55"/><circle cx="30" cy="-114" r="7" fill="#f2a08c" opacity=".55"/>
    </g>
  </g>
</svg>`;
  }
  window.FIG = { person, INK };
})();
