# Lecture decks — rules for every session

The course (LUMS CES, *E-Commerce: Building, Scaling & Managing Digital
Businesses*) has one slide deck per session, built as a Claude Slides artifact
in the Consulytics theme and exported to PowerPoint with animations. These are
the instructor's standing rules. Apply them to every new deck and every edit.

## Content

1. **No classroom instructions on a slide.** Nothing like "take the strongest
   answer from the board", "in your teams, 12 minutes", "read the middle column
   again", "write it down", "submit before you leave". There may be no board.
   If the slide needs a prompt, phrase it as a **question** to the room.
   Timings, facilitation moves and logistics go in the **speaker notes**.
2. **Theory first, then the simulation.** Each session teaches real-world
   e-commerce practice and frameworks on their own, with no reference to the
   simulation. A separate, clearly titled section afterwards maps that theory
   onto the simulation round's decisions, using the simulation as the worked
   example.
3. **Never let simulation numbers pass as market data.** Every figure that comes
   from the simulation (segment shares, repeat rates, weights, cash cycle days,
   margins) is labelled as the simulation's assumption, and the slide says real
   founders get such numbers from research. Never invent a real-world
   statistic; illustrative examples are marked as illustrative.
4. **Introduce the simulation's market before using it.** Students do not know
   what the simulation sells or how it works until a slide tells them.
5. The course map (`docs/15-course-map.md`) says which decisions open in which
   session; each session's simulation section covers exactly those.

## Design and animation

- Consulytics palette: ink `#131316`, red `#ed0000`, light `#f5f5f6`,
  white cards with `#e4e4e7` borders, Inter / JetBrains Mono.
- One idea per click, plain **fade** builds (the instructor's own style is
  PowerPoint "Appear", one click per idea). Every content slide builds; title
  slides build only their promise line.
- Boxes in a row are the same height; nothing overflows or overlaps; nothing
  below y = 920 except the footer. Render and check every slide before
  publishing.

## Tools (`tools/deck/`)

- `pinbuild.py` — turns flowing content (card rows, tables) into pinned,
  click-by-click builds without moving anything.
- `fit.py` — measures slides in Chromium; equalises card rows.
- `build_pptx.py` + `extract.js` — exports a deck to a native .pptx: every
  element an editable shape, every build a Fade entrance On Click, speaker notes
  and transitions included. The Slides artifact's own PowerPoint export drops
  animations, so use this instead.
  `python tools/deck/build_pptx.py <deck folder> <out.pptx> <logo.png>`
  (the deck folder holds `project/deck.json` and `project/slides/`).

## The decks

- Session 1 — https://claude.ai/artifact/F5n9AU3uuw6LRAxWTTeEox
- Session 2 — https://claude.ai/artifact/8m8wJahwjW9ZJ6FLqhgypd
