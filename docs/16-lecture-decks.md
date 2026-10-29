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
5. **Illustrate every theory block with real cases**: one Pakistani and one
   global (or regional) company on a two-card case slide after the block,
   with facts checked against published sources and cited in the footer and
   notes. Prefer cases from the simulation's category where they fit.
6. **Two parts per deck.** Part 1 is theory with cases; Part 2 (its own divider
   slide) is the simulation, framed on its actual category — personal care and
   home care in Pakistan — starting with one slide on how that category really
   works online before the simulation's own market.
   *Exception:* Session 11 has three parts. Part 2, the toolkit, is
   platform practice (Shopify, Meta ads, Google Search) between the theory
   and the simulation, which becomes Part 3; it can be taught as a session of
   its own (see *The decks*).
7. The course map (`docs/15-course-map.md`) says which decisions open in which
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

- `s2_slides.py`, `s2_cases.py`, `s3_slides.py`, `s4_slides.py`, `s5_slides.py`, `s6_slides.py`, `s7_slides.py`, `s8_slides.py`, `s9_slides.py`, `s10_slides.py`, `s11_slides.py`, `s12_slides.py` — the generators that wrote the
  Session 2 and 3 slides (helpers: section, card, band, grid, case slides,
  dividers, waterfall, pinned tables). Run with the deck folder as argument.
- Page snapshots (from Session 6): `s6_slides.py` draws each one as a browser
  frame with the page's address. Capture the page, upload it to the deck as an
  asset, and pass a JSON file mapping the snapshot's key to the asset url as
  the third argument; a key with no image renders as an empty labelled frame.
- Simulation numbers on Part 2 slides come from running the engine (one
  baseline round with default decisions), never from memory or the logs.
  Sessions 7 and 8: `python tools/deck/s7_s8_tests.py` prints every line of
  their test tables; Session 9: `python tools/deck/s9_tests.py`; Session 10:
  `python tools/deck/s10_tests.py`; Session 11: `python tools/deck/s11_tests.py`
  (each AI build committed in month 3 and in month 10, twenty games each);
  Session 12: `python tools/deck/s12_tests.py` (the round weights, a default
  team's final score by measure, and months 11 and 12 changed). All four pin the
  Fall-2026 game's PKR 12M of starting capital (new games start on 13M). Scores
  in the Session 11 and 12 tests leave out decision quality: a test team earns
  it for the decisions it submits while its twin submits none.
- `s9_s10_slides.py` writes Sessions 9 and 10 as one deck (Session 10's slide
  ids carry an `s10-` prefix); `s11_s12_slides.py` writes Sessions 11 and 12 as
  one deck (`s11-` and `s12-` prefixes). `fit.py` mis-measures the cover layout
  and the bar chart of round weights (`s12-sim-weights`): fit the slides, then
  copy those back from an unfitted build.
- `s11_toolkit.py` — Session 11's Part 2, the toolkit (33 slides, run from
  `s11_slides.py`, which splices it in before the simulation): Shopify store
  practice, Meta ads in the Andromeda era, Google Search (SEO, AI answers,
  Google Ads and Shopping), an audit exercise, and one slide on where the
  toolkit shows up in the simulation. Platform facts were checked against
  Shopify, Meta and Google's own pages and the cited cases in October 2026;
  these platforms change every quarter, so check them again before teaching.
  Claims the platforms do not make themselves (for example Meta "Entity IDs"
  or similarity thresholds) are labelled as practitioner talk, not fact.

## The decks

- Session 1 — https://claude.ai/artifact/F5n9AU3uuw6LRAxWTTeEox
- Session 2 — https://claude.ai/artifact/8m8wJahwjW9ZJ6FLqhgypd
- Session 3 — https://claude.ai/artifact/V5LSNWTN1zvyQFTE1nvD4j
- Session 4 — https://claude.ai/artifact/HEeHEXCYmqBMGsLMbcjCQH
- Session 5 — https://claude.ai/artifact/GWagEf7Pc9UBaq19ckifh1
- Session 6 — https://claude.ai/artifact/DJvcbGXeMeZjVFLu1hQtCw
- Session 7 — https://claude.ai/artifact/KpatG5RZ6o4cGTzTP1bzxw
- Session 8 — https://claude.ai/artifact/8J2hyQmTcYpZCYkZtjcGgL
- Session 9 — https://claude.ai/artifact/Tg4mvToRefBpjVSgLRoRJT
- Sessions 9 and 10, one deck — https://claude.ai/artifact/QvHmh1sPHgENKFJ2Rko2Hj
- Sessions 11 and 12, one deck — https://claude.ai/artifact/6wkdN1uxouhzmG5CcVdyAe
  (85 slides). Session 11 has 60: Part 1, how AI helps (business case,
  recommendations, forecasting, service, creative, build or buy); Part 2, the
  toolkit, in sections *Shopify*, *Meta*, *Google* and *Applied*; Part 3, AI in
  the simulation. To teach it over two sessions, take Parts 1 and 3 in one and
  Part 2 (about 90 minutes) in the other; the cover's notes give the plan.
