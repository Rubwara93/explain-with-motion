# Brand and project settings

## brand.json

```json
{
  "name": "Acme Coaching",                 // shown in the footer next to the logo (may be "")
  "logo": "assets/logos/logo.png",          // PNG/SVG in the project, or null
  "colors": {
    "paper": "#fbfaf8",       "paper2": "#f5f3ef",     // background, caption strip
    "ink": "#1c2733",         "muted": "#756e64",      // text, secondary text
    "line": "#ece8e2",                                 // hairlines
    "primary": "#206093",     "primary_dark": "#1b5180",  // main colour, italic accent words
    "primary_light": "#cfe0ee", "primary_lighter": "#eaf1f7",
    "accent": "#f28b2d",      "accent_light": "#fbddc1",  // "the new thing", highlights
    "accent_text": "#b25003"                            // accent as TEXT colour (needs 4.5:1 on paper)
  },
  "fonts": {
    "display": {"family": "Spectral",  "faces": [ …output of fetch_font.py… ]},
    "text":    {"family": "Work Sans", "faces": [ … ]}
  }
}
```

The default is a calm paper look (warm off-white, deep blue, one orange accent, Spectral + Work Sans).
To use the user's brand:

1. Ask for colours, fonts and logo – or a website URL. From a website, read the CSS custom properties,
   the colours of buttons/headings and the `font-family` of headings and body text.
2. Map them: one main colour (`primary`, plus a darker and two light tints), one accent, a light
   background. Keep the background light – the format lives on calm paper; dark themes work but need
   all diagram colours checked.
3. Fonts: `python3 scripts/fetch_font.py "<Google Font>" 400,500 <project>/assets/fonts [--italic] [--serif]`,
   paste the printed `faces` into brand.json and prefix each `file` with `assets/`. Commercial
   brand fonts need a web licence; if missing, pick the closest Google Font and say so.
4. Logo into `assets/logos/`. Ask before using a logo of another organisation (partner, academy)
   in the end card; use the file the user provides.

Diagram SVGs in the example use the default hex colours directly. When the brand changes, replace
those hex values too (search for `#206093`, `#f28b2d`, `#cfe0ee`, `#fbddc1`, `#1b5180`).

## project.json

```json
{
  "layout": "4:5",              // 4:5 feed (default) | 9:16 reels/shorts | 16:9 YouTube/web
  "fps": 25, "lang": "de", "clip_duration": 318.96, "captions": true,
  "lower_third": {"name": "Ruben Langwara", "role": "im Gespräch mit Rebecca van der Linde",
                  "start": 0.6, "duration": 6.0, "position": "bottom-left"},   // or null; "top-left" over burned-in name labels
  "work": "/path/to/work",      // set by new_project.py; captions.json is read from here
  "footer_left": "Ruben Langwara · Emotional intelligent durch den Change",
  "endcard": {
    "seconds": 6.5,
    "eyebrow": "Resilienz Initiative", "logo": "assets/logos/signet.png", "logo_height": 140,
    "headline_html": "Emotionale <em>Dynamiken</em> verstehen.",
    "subline": "Ruben Langwara · aus dem Interview mit Rebecca van der Linde",
    "cta": {"before": "Mehr dazu in der Fortbildung", "highlight": "Emotionale Resilienz",
            "after": "an der Resilienz Akademie", "logo": "assets/logos/academy.svg", "logo_height": 41}
  }
}
```

Layout geometry (video box, caption strip, panel) is fixed per layout in `build.py`:

| layout | canvas | video | captions | graphics panel |
|---|---|---|---|---|
| 4:5 | 1080×1350 | top, 1080×608 | 108 px strip | 1080×572 below |
| 9:16 | 1080×1920 | top, 1080×608 | 128 px strip | 1080×1024 below (keep the lowest ~250 px calm: app UI covers it) |
| 16:9 | 1920×1080 | left, 1080×608 | 150 px under the video | 840×1010 on the right |
