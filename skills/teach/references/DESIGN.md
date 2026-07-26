# Lesson HTML Design

Design system for HTML this skill generates. One course identity across every `lessons/*.html` and `reference/*.html` in workspace, so set reads as course, not pile one-offs.

Hard constraints from [SKILL.md](SKILL.md) shape every choice: lessons open on `file://` with network off — no CDN, no remote font, no external script. Print must work. Every claim cites. Cold open seals new content until answered.

## Artifacts

Maintainable split — spec here, code as real files skill copies:

| File                                                   | Role                           | Copied into workspace as |
| ------------------------------------------------------ | ------------------------------ | ------------------------ |
| [`templates/lesson.css`](../../templates/lesson.css)   | Canonical stylesheet           | `assets/lesson.css`      |
| [`templates/quiz.js`](../../templates/quiz.js)         | Reusable quiz widget           | `assets/quiz.js`         |
| [`templates/lesson.html`](../../templates/lesson.html) | Lesson skeleton (placeholders) | `lessons/NNNN-slug.html` |

Edit templates; don't fork per lesson. Lesson fills `{{placeholders}}` in skeleton, links two `assets/` files — nothing more.

## Direction

Moss-and-stone teaching manual, dark. Warm near-black stone page, warm off-white ink, single light-moss accent. Serif body for sustained reading, sans for labels, mono for code and spaced-repetition result line. Single body column with wide right margin holding citations as sidenotes — margin earns width since every claim cites, so citations live beside claim, not as inline footnote bombs.

Not cream-and-terracotta default (stone, not cream; moss, not terracotta). Not black-and-acid-green — the dark here is warm stone, not pure black, and the accent is a muted moss, not a single bright signal colour; calm, reading-first. Not broadsheet multi-column (single column + margin; hairlines as structure, not newspaper).

Voice: the dropped-article style throughout this skill is deliberate and load-bearing — preserve it in edits; do not normalize to standard English.

## Tokens

Names and roles only — no values here, on purpose. Values drift when restated.

| Token        | Role                                   |
| ------------ | -------------------------------------- |
| `--paper`    | page surface                           |
| `--paper-2`  | panels, cold-open field, code          |
| `--ink`      | body text                              |
| `--ink-soft` | secondary text, marginalia             |
| `--rule`     | hairlines                              |
| `--rule-2`   | control boundaries (quiz options)      |
| `--accent`   | light moss — gate, correct, links      |
| `--accent-2` | deep moss — hover, secondary marks     |
| `--wrong`    | wrong (muted oxblood, never alarm-red) |
| `--serif`    | body face (sustained reading)          |
| `--sans`     | labels and marginalia face             |
| `--mono`     | code and result-line face              |
| `--fs-1`…`8` | type ladder, small to large            |
| `--track`    | tracking every uppercase label shares  |
| `--s-1`…`11` | space ladder — margins and padding     |
| `--measure`  | body line length                       |
| `--margin-w` | sidenote column width                  |
| `--gutter`   | body ↔ margin gap                      |
| `--radius`   | corner radius, controls and code       |
| `--tap`      | minimum touch target (44px)            |
| `--tint`     | state wash strength over `--paper`     |

Why these tokens, not others:

- **System-only type stacks.** Web fonts are banned on `file://` — no CDN, no remote `@import`, cable unplugged → page still renders. The serif stack ships on Windows + macOS and degrades cleanly; sans and mono ride the OS defaults. No web font is worth a network dependency the brief forbids.
- **`--measure` bounds line length** for sustained reading. Width is a typographic decision, not a layout accident — a body column past ~36rem stops being read and starts being scanned.
- **`--margin-w` earns its width** because every claim cites. Citations live beside the claim as sidenotes, not bunched as inline footnote bombs. The margin is structural, not decorative.
- **`--wrong` is muted oxblood, never alarm-red.** Wrong answers are a teaching signal, not an emergency. Red shouts; oxblood corrects quietly, keeps the page calm.
- **Two ladders, not free values.** Every size and every gap comes off `--fs-*` or `--s-*`, so a panel's inset and the prose beside it cannot land a sixteenth of a rem apart. Rungs are ranked, never named for the component that reaches for one first — a `--fs-eyebrow` is one reuse away from lying. A value wanted in two rules is a token or it is a value that drifts.
- **`--rule-2` exists because `--rule` is too faint to be an edge.** Hairlines separate; control boundaries must be _found_. A quiz option's border is the only thing saying "this is clickable", and `--rule` sits near 1.5:1 on paper — under the 3:1 a control boundary owes. Two tokens, two jobs; never use `--rule` on an interactive edge.

Token values live in [`templates/lesson.css`](../../templates/lesson.css) `:root` — the single source. Edit there; never restate values here.

## Layout

Body column (`--measure`) + sidenote column (`--margin-w`), gutter between. `.lesson` take `width: fit-content`, not a restated `max-width`: tracks are fixed lengths, so shrink-to-fit is exactly both columns plus gutter plus the element's own padding, and it cannot drift from the tokens. A hand-written `max-width` that forget `box-sizing: border-box` count the padding hang the margin column outside the block and push whole composition off centre. Everything defaults into body column; sidenotes and `.full` opt out. Hairlines separate, never boxes. Sidenote sits immediately after the paragraph that cites it — grid auto-placement then lands it in column 2 of that same row, beside its own claim. Narrow screens collapse below.

Sidenotes live **inside** `.lesson-content`, not after it. Two reasons, both load-bearing: outside the sealed wrapper they read plainly while the gate is shut (citation text leaks the lesson), and — since the sealed wrapper is a single grid item holding the whole body — a sidenote outside it can only stack below the entire lesson, never beside a paragraph. So `.lesson-content` spans both columns and takes `grid-template-columns: subgrid`, re-exposing the parent's two columns to the paragraphs and sidenotes nested in it. Where subgrid is unsupported an `@supports not` block blocks the wrapper, and the body falls back to one column with sidenotes inline below their anchor — the narrow-screen layout, which is a degradation, not a break. That fallback has to be asked for. Left alone, the dropped `subgrid` leaves one explicit column and `grid-column: 2` opens an _implicit_ second track: note beside its paragraph at whatever width it takes, no gutter (`column-gap` is on `.lesson`, not the wrapper), body squeezed. Not the documented degradation — a collision.

## Signature — the retrieval gate

Cold open is lesson's threshold. Body content below it **sealed**: dimmed, blurred, `inert`, small hairline label ("Answer the cold open to unseal the lesson"). Every cold-open item answered → `quiz.js` drops `.sealed` and `inert` together, body quietly releases. One moment page asserts itself — embodies retrieval-before-instruction, brief's core mechanism.

The seal is two halves and needs both. Blur is the visible half; `inert` is the half that holds. Blur alone gates the eye only — Tab still walks the sealed lesson, a screen reader still reads it out, and the signature becomes decoration for exactly the readers who cannot see it. `check_lesson.py` enforces the pairing (`quiz-releases-not-inert`). Label text comes from `data-seal-label` on the sealed element so a non-English lesson can translate it; the CSS literal stays as fallback.

The instruction needs a third piece, and for the same reason `inert` exists. The veil's label is CSS content **inside** the inert subtree, and inert prunes that subtree from the accessibility tree outright — the sentence the gate exists to give lands nowhere, and a screen-reader user tabs out of the cold open into a body that is simply absent, unexplained. So `.seal-note` carries the sentence as real text, sibling of the quiz, outside the seal. It is `role="status"` because `quiz.js` swaps its text on release: unsealing moves no focus and owns no live region of its own, so otherwise the page's largest state change is silent for everyone not watching it. Unlike `.quiz-fb` it starts **full** — that first string is page copy, read in order; only the swap is an announcement. A revisit unseals from remembered state with no gate to explain, so that path removes the element rather than asserting a release that did not happen.

Quiet on purpose: faint veil, hairline frame, small uppercase label. No confetti, no green flash. `prefers-reduced-motion` → no transition, instant release; veil stay, because blur is static mask and not movement — cancel it and reduced-motion reader read whole sealed lesson at 35% opacity. Seal state, not performance.

## Components

- **Cold open** — `.cold-open`, `--paper-2` field, 3px moss left rule, hairline frame, moss eyebrow. Holds quiz. Field spans both columns; what it holds stay bounded to `--measure`, so cold-open quiz and practice quiz further down same lesson are one component at one width, and ✓ mark stay next to words it marks.
- **Lead** — `.lead` on the opening paragraph. One thing lesson lands, set above body size. At body size it read as first paragraph, not as claim rest of page argue.
- **Quiz** — shape only:

  ```html
  <div class="quiz" data-releases="contentId" data-label="Cold open" data-lesson="NNNN-slug">
    <div class="quiz-item" role="group" aria-labelledby="q1" data-correct="0">
      <p class="quiz-q" id="q1">…</p>
      …<button class="quiz-btn" type="button">…</button>…
    </div>
    <p class="quiz-result" role="status"></p>
    <button class="quiz-copy" type="button" hidden>Copy result</button>
  </div>
  <p class="seal-note" role="status">…</p>
  ```

  `.quiz-result` carries **no** `hidden` — `quiz.js` never unhides it, so a hidden one is a result line, and a scoring affordance, that nobody ever sees. `role="group"` + `aria-labelledby` is what ties options to their own question: three sibling buttons carry no question with them, so on item 2 of 3 a screen reader otherwise offers a bare option list.

  Equal-width `.quiz-btn` options so formatting never leaks the answer (rule from [SKILL.md](SKILL.md) `## Skills`; same character-count per option where possible). Right/wrong carries a mono ✓/✗ mark as well as border + tint — border colour and tint are both colour, so the mark is what keeps the state readable without it. Answered options carry `aria-disabled`: still focusable, so the mark stay reachable, but no longer offering an action that do nothing. Result line and per-item feedback are `role="status"`: both appear without focus moving, and an unannounced result line is a result line a screen-reader user never learns exists — so both start **empty and in the tree**, and `quiz.js` fill them. A live region that arrive already full is the case screen readers most often miss. `.quiz-fb` keep its `hidden` and its authored text in markup, which is what a no-JS page need; init hoist that text into JS and empty the element. Copy control must work on `file://` — no copy control, no spaced-repetition loop. This section is the quiz contract; [`templates/quiz.js`](../../templates/quiz.js) implements it.

  **Undo window.** Answer is not final the instant it is clicked. Chosen option go to a neutral `data-state="chosen"` mark, `.quiz-undo` appear, item lock three seconds later. Nothing about the answer is revealed inside that window — no right/wrong, no correct option, no feedback. Reveal-then-undo would hand back a free retry with the answer already on screen, and that is the one thing retrieval measurement cannot survive. Once locked there is no retry: the window buy back the tap, never the recall. Reason it exist: this line reschedule a memory record, so a mis-tap is noise recorded as signal.

  Copy control show only on a first pass through a gated cold open — a revisit unseal from remembered state and a practice quiz never gate, so neither produce a line worth pasting. `data-lesson` bind the line to its own lesson.

- **Citations** — inline `a.cite` number is a real link to its own `.sidenote` (`id="n1"`, `n2`, … in order); note itself sans, small, `--ink-soft`, hairline left rule, and a `<p>` rather than an `<aside>` — an aside here is scoped to no sectioning element, so each note would land as its own `complementary` landmark and a finished lesson would bury `<main>` under a dozen of them. `a.cite` takes inline padding with a cancelling negative margin: vertical padding on an inline box does not touch the line box, so the tap target grows from 8px to something findable without a pixel of reflow. That matters on the phone, which is the one place the note has moved away from the claim it belongs to. Beside the paragraph the pairing is obvious; on a phone and on paper the note has moved below its claim, and matching numeral is then only thing tying claim to source. `sup.cite` stay styled for lessons generated before the link existed.
- **Knowledge / Skills** — `h2` sections with `--rule` hairline above (structural divider, not decoration). Knowledge first, skills second.
- **Code** — `--mono` on `--paper-2`, 2px moss left rule, horizontal scroll.
- **Where next** — final block: one primary source (highest-trust thing found), cross-links to related lessons and reference docs by anchor, line inviting follow-up questions.

## Constraints

- **Offline** — no `@import`, no remote `url()`, no external `<script src>`, no stylesheet `<link>` to anywhere but `assets/`. System font stacks only. Cable unplugged → page renders.
- **Print** — collapse to one column (the margin column has no reader on paper), keep `--measure` (paper is the one medium where reader cannot narrow the window; unbounded page box is a 95-character line) _and drop the block's own padding with it_, since `box-sizing` is border-box and 2rem a side inside a `max-width: --measure` is a 32rem column, not 36rem — the page box has `@page` margins for that. Unseal content, drop sidenotes inline as small footnotes, drop `.seal-note` (on paper the body is already open, so a line promising it is sealed is simply false), avoid page-break inside quiz items and `pre`. Color not load-bearing (B&W prints fine). Quiz options print as plain list, not hidden — hidden they leave question dangling on em-dash with nothing under it, and printed lesson is meant to be worked through; only copy and undo controls go. Sidenote links print their URL after the title: every claim cites, and citation whose URL never printed is citation reader cannot follow.
- **Motion** — reduced-motion → no transitions, instant release; blur stay (static mask, not movement). Default motion subtle (seal ~0.6s, quiz state ~0.15s). No scroll reveals, no ambient animation.
- **Responsive** — below 64rem: single column, sidenotes inline below anchor, cold-open full width, padding shrinks, line length stays bounded.
- **a11y** — visible keyboard focus on every control **and every link**; control boundaries on `--rule-2` (3:1), never `--rule`; quiz state signaled by mark + border, not color alone; answered options `aria-disabled`, still focusable; options grouped and labelled by their own question; sealed body `inert`, not merely blurred; nothing an inert subtree carries — `::after` label included — reaches assistive technology, so the gate's instruction lives outside it in `.seal-note`, and the release announces there; state changes that move no focus announced via `role="status"`, from live regions that were empty and in the tree before the text arrived; focus never dropped by hiding the control it sit on (`.quiz-undo` hand it back to the chosen option); `prefers-reduced-motion` honored; `forced-colors` opt-out on the veil alone, whose background _is_ the component (quiz state survive the forced palette on its mark); sidenotes are `<p>`, never `<aside>`, so citations do not each become a landmark; `lang` set on `<html>`; `<main>` landmark wraps the lesson.

## Validation

[`check_lesson.py`](scripts/check_lesson.py) is the executable contract for the static subset of this design — the script is the spec, so this section does not restate its rules.

`scripts/` and `templates/` live at the plugin root, alongside `skills/`. During a session the working directory is the learner's workspace, never the plugin, so call the script through `${CLAUDE_PLUGIN_ROOT}` (which substitutes directly in this skill content), not by a hand-resolved path.

- `python "${CLAUDE_PLUGIN_ROOT}/skills/teach/scripts/check_lesson.py" --self` — run after editing templates; validates `templates/lesson.html` against the contract (must pass; catches spec/validator mismatch).
- `python "${CLAUDE_PLUGIN_ROOT}/skills/teach/scripts/check_lesson.py" <lesson-path>` — validate a generated lesson for conformance (quiz structure, offline no-remote-refs, a11y static checks). Step 6 of [SKILL.md](SKILL.md) run this on every lesson before opening it.
- `python "${CLAUDE_PLUGIN_ROOT}/skills/teach/scripts/check_lesson.py" --type=reference <path>` — same for a reference document; skips the quiz and cold-open rules.

Stale copied assets are reported by `teach.py state` (detect-only; it never overwrites per-workspace topic components), not by this script.

The static subset (quiz structure, offline, a11y) is machine-enforced here. Non-static concerns (result-line shape, print layout, motion) are enforced by template-as-source, not this script.

## Reference docs

`reference/*.html` link same stylesheet, drop cold-open + sealed wrapper, lean on print CSS — read and printed, not worked through. Same tokens and components; no separate identity.
