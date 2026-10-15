# explain-with-motion

Ein Skill für Claude Code und Codex, der aus einer langen Aufnahme ein Erklärvideo mit Motion Graphics macht. Oben sieht man die Person, die erklärt, darunter laufen Untertitel, und im unteren Teil entstehen Grafiken, die das Gesagte sichtbar machen: Modelle, Vorher-nachher, Ursache und Wirkung, das eine Neue zwischen vielem Vertrautem.

Gedacht für Coaches, Trainerinnen, Beraterinnen und alle, die in Interviews, Podcasts oder Webinaren etwas erklären und genau diese Stelle als Video teilen wollen, etwa als Beispiel zu einem LinkedIn-Post.

*English: A Claude Code / Codex skill that turns a passage from an interview, podcast or call into a split-screen explainer video – speaker on top, captions, and motion graphics that visualise the explanation below. 4:5, 9:16 or 16:9, rendered locally with [HyperFrames](https://hyperframes.heygen.com). The skill talks in the user's language.*

## Was der Skill macht

1. **Transkribiert** die ganze Aufnahme lokal (whisper.cpp) und findet die Passage, die du beschreibst („die Stelle, wo ich über den Kunden mit der neuen Software spreche“).
2. **Schneidet** sie: Versprecher, Füllwörter und Nebenbemerkungen fliegen raus, jeder Schnitt landet in einer echten Sprechpause. Den Schnittplan siehst du vorher in einfachen Worten.
3. **Untertitelt** mit korrigiertem Wortlaut. Namen, Fachbegriffe und Umlaute werden nachgebessert, unsichere Wörter fragt der Skill nach, statt zu raten.
4. **Plant die Szenen** und zeigt dir den Plan, bevor gebaut wird: für jede Phase der Geschichte ein Bild, am Ende das stärkste.
5. **Baut und rendert** das Video in deinem Design (Farben, Schriften, Logo, oder von deiner Website gelesen), mit Bauchbinde, Fußzeile und Abspann samt Hinweis auf dein Angebot.
6. **Prüft** das Ergebnis: Ton und Bild synchron, Lautheit −14 LUFS, kein eingefrorenes Bild, Kontraste.
7. Optional macht er den **Ton sauberer** über Auphonic (eigener Schlüssel nötig). Deine Stimme bleibt dabei deine Stimme.

Die Gestaltungsregeln stammen aus echten Abnahmerunden: Die Grafik erklärt, die Untertitel sprechen. Es gibt keine Überschriften über jeder Szene und keine Beschriftungen, die nur für den einen Kunden aus der Geschichte Sinn ergeben. Was in einem Modell einsortiert wird, liegt auch wirklich darin. Nachzulesen in [references/design-rules.md](skills/explain-with-motion/references/design-rules.md).

## Installation

**Claude Code**, als Plugin:

```
/plugin marketplace add Rubwara93/explain-with-motion
/plugin install explain-with-motion@explain-with-motion
```

**Codex**: im Chat schreiben „Installiere den Skill von github.com/Rubwara93/explain-with-motion“. Von Hand:

```bash
git clone https://github.com/Rubwara93/explain-with-motion.git && cp -r explain-with-motion/skills/explain-with-motion ~/.codex/skills/
```

**Andere Agenten**, die das Agent-Skills-Format lesen:

```bash
npx skills@latest add Rubwara93/explain-with-motion
```

### Voraussetzungen

ffmpeg, Node.js 20+, whisper.cpp und Python 3 mit numpy. Auf dem Mac:

```bash
brew install ffmpeg node whisper-cpp && python3 -m pip install numpy
```

Beim ersten Lauf prüft der Skill alles und lädt das Sprachmodell (rund 470 MB, einmalig). Alles läuft auf dem eigenen Rechner. Für die Transkription und das Video braucht es kein Konto und keinen Cloud-Dienst.

## Benutzung

```
/explain-with-motion Aus ~/Videos/interview.mp4 bitte die Stelle, wo ich erkläre, wie man emotional intelligent mit Veränderung umgeht. Als 4:5-Video für LinkedIn, in meinem Design (www.meine-seite.de), am Ende Hinweis auf meinen Kurs.
```

In Codex: `$explain-with-motion` oder „nutze den Skill explain-with-motion“. Der Agent greift auch von selbst danach, wenn man ein Erklärvideo mit Animationen aus einer Aufnahme haben möchte.

Rechne für ein 5-Minuten-Video mit etwa einer Stunde gemeinsamer Arbeit: Transkription, Schnittplan, Szenenplan, Bau und ein Render, der ungefähr so lange dauert wie das Video selbst. Änderungen danach gehen schnell.

## Aufbau

```
skills/explain-with-motion/
  SKILL.md                   Ablauf für den Agenten
  scripts/doctor.py          Werkzeuge prüfen, Sprachmodell laden
  scripts/transcribe.py      Aufnahme → Wörter mit Zeiten, lesbares Transkript
  scripts/cut.py             Passage schneiden, Schnitte in echte Pausen legen, −14 LUFS
  scripts/probe.py           Schnittstellen prüfen (Kanten nachhören, Pegel ansehen)
  scripts/captions.py        korrigierter Untertiteltext → Zeiten, SRT
  scripts/new_project.py     HyperFrames-Projekt anlegen, Clip vorbereiten, Schriften laden
  scripts/build.py           Szenen + Marke + Untertitel → index.html
  scripts/render.py          prüfen, Probebilder, rendern, Ergebnis messen
  scripts/audio_polish.py    optional: Ton über Auphonic säubern
  scripts/fetch_font.py      Google Font als woff2 laden
  assets/template/           Layout (4:5, 9:16, 16:9), Animationshelfer, Personenfiguren
  references/                Gestaltungsregeln, Bildideen-Katalog, Marke, bekannte Fallen
  examples/change-story/     komplettes 5-Minuten-Beispiel (17 Szenen, ohne Video)
```

## Beispiel

`examples/change-story` ist ein echtes Video: Ruben Langwara erzählt im Interview mit Rebecca van der Linde (Resilienz-Kongress 2026), wie ein Team mit der Einführung einer neuen Software umgeht. Das Video selbst liegt nicht im Repository, die Szenen, der Schnittplan und die Untertitel schon. Sie zeigen, wie man ein Modell (Circle of Influence), eine Angst, die in die Zukunft projiziert, und ein Vorgehen (vertraut, neu, Mehrwert) in Bilder übersetzt.

## Hinweise

- **Rechte**: Nur Aufnahmen verwenden, an denen du die Rechte hast. Wenn andere Personen zu sehen oder zu hören sind (Moderation, Gäste), vorher ihr Einverständnis einholen.
- **Schriften**: Der Standard-Look nutzt Spectral und Work Sans (SIL Open Font License), die beim Anlegen eines Projekts von Google Fonts geladen werden. Kommerzielle Hausschriften nur mit Web-Lizenz.
- **GSAP** wird beim Anlegen eines Projekts von cdnjs geladen (kostenlose GSAP-Standardlizenz).
- **HyperFrames** ist ein Open-Source-Werkzeug von HeyGen und wird per `npx` in einer festen Version geladen.

## Lizenz

MIT, siehe [LICENSE](LICENSE). Von Ruben Langwara, [rubenlangwara.de](https://www.rubenlangwara.de).
