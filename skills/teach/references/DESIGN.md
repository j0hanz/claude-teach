# Lesson HTML Design

Design system for HTML this skill generate. One course identity cross every `lessons/*.html` and `reference/*.html` in workspace — set read as course, not pile one-offs.

Hard constraint from [SKILL.md](../SKILL.md) shape every choice: lessons open on `file://` with network off — no CDN, no remote font, no external script. Print must work. Every claim cite. Cold open seal new content until answered.

## Artifacts

Maintainable split — spec here, code as real file skill copy:

| File                                                                  | Role                           | Copied into workspace as |
| --------------------------------------------------------------------- | ------------------------------ | ------------------------ |
| [`templates/assets/styles.css`](../../../templates/assets/styles.css) | Canonical stylesheet           | `assets/styles.css`      |
| [`templates/assets/quiz.js`](../../../templates/assets/quiz.js)       | Reusable quiz widget           | `assets/quiz.js`         |
| [`templates/lesson.html`](../../../templates/lesson.html)             | Lesson skeleton (placeholders) | `lessons/NNNN-slug.html` |

Edit template; don't fork per lesson. Lesson fill `{{placeholders}}` in skeleton, link two `assets/` file — nothing more.

## Direction

Study instrument, light. Pale ash page, graphite ink, cobalt navigation and calibration signal; muted brick only for wrong answer. Serif body carry sustained reading, sans label and marginalia, mono code and spaced-repetition result line. Single body column, wide right margin hold citation as sidenote — margin earn width, every claim cite, so citation live beside claim, not inline footnote bomb.

Not cream-and-terracotta default (ash not cream; cobalt not terracotta). Not dashboard blue: cobalt mark direction, control and calibration, never drown reading surface. Not broadsheet multi-column (single column + margin; rules are study structure, not newspaper).

Voice: dropped-article style throughout this skill deliberate, load-bearing — preserve in edit; don't normalize to standard English.

## Tokens

Name and role only — no value here, on purpose. Value drift when restated.

| Token        | Role                                  |
| ------------ | ------------------------------------- |
| `--paper`    | ash page surface                      |
| `--paper-2`  | white panels, cold-open field, code   |
| `--ink`      | graphite body text                    |
| `--ink-soft` | secondary text, marginalia            |
| `--rule`     | hairlines                             |
| `--rule-2`   | control boundaries (quiz options)     |
| `--accent`   | cobalt — gate, correct, links         |
| `--accent-2` | deep cobalt — hover, secondary marks  |
| `--wrong`    | wrong (muted brick, never alarm-red)  |
| `--serif`    | body face (sustained reading)         |
| `--sans`     | labels and marginalia face            |
| `--mono`     | code and result-line face             |
| `--fs-1`…`7` | type ladder, small to large           |
| `--track`    | tracking every uppercase label shares |
| `--s-1`…`9`  | space ladder — margins and padding    |
| `--measure`  | body line length                      |
| `--margin-w` | sidenote column width                 |
| `--gutter`   | body ↔ margin gap                     |
| `--radius`   | corner radius, controls and code      |
| `--tap`      | minimum touch target (44px)           |
| `--tint`     | state wash strength over `--paper`    |

Why these token, not others:

- **System-only type stacks.** Web font banned on `file://` — no CDN, no remote `@import`, cable unplugged, page still render. Serif stack ship on Windows + macOS, degrade clean; sans and mono ride OS default. No web font worth network dependency brief forbid.
- **`--measure` bound line length** for sustained reading. Width typographic decision, not layout accident — body column past ~36rem stop being read, start being scanned.
- **`--margin-w` earn its width** because every claim cite. Citation live beside claim as sidenote, not bunch as inline footnote bomb. Margin structural, not decorative.
- **`--wrong` muted oxblood, never alarm-red.** Wrong answer teaching signal, not emergency. Red shout; oxblood correct quiet, keep page calm.
- **Two ladder, not free value.** Every size and gap come off `--fs-*` or `--s-*`, so panel inset and prose beside it can't land sixteenth of rem apart. Rung ranked, never named for component that reach for one first — `--fs-eyebrow` one reuse away from lying. Value wanted in two rule is token, or value that drift.
- **`--rule-2` exist because `--rule` too faint to be edge.** Hairline separate; control boundary must be _found_. Quiz option border only thing saying "this is clickable", `--rule` sit near 1.5:1 on paper — under 3:1 control boundary owe. Two token, two job; never use `--rule` on interactive edge.

Token value live in [`templates/assets/styles.css`](../../../templates/assets/styles.css) `:root` — single source. Edit there; never restate value here.

## Layout

Body column (`--measure`) + sidenote column (`--margin-w`), gutter between. `.lesson` take `width: fit-content`, not restated `max-width`: track fixed length, so shrink-to-fit exactly both column plus gutter plus element own padding — can't drift from token. Hand-written `max-width` that forget `box-sizing: border-box` count padding, hang margin column outside block, push whole composition off centre. Everything default into body column; sidenote and `.full` opt out. Hairline separate, never box. Sidenote sit right after paragraph that cite it — grid auto-placement land it column 2 same row, beside own claim. Narrow screen collapse below.

Sidenote live **inside** `.lesson-content`, not after. Two reason, both load-bearing: outside sealed wrapper they read plain while gate shut (citation text leak lesson); and — since sealed wrapper single grid item holding whole body — sidenote outside can only stack below entire lesson, never beside paragraph. So `.lesson-content` span both column, take `grid-template-columns: subgrid`, re-expose parent two column to paragraph and sidenote nested in it. Where subgrid unsupported, `@supports not` block block the wrapper, body fall back to one column with sidenote inline below anchor — narrow-screen layout, degradation not break. That fallback must be asked for. Left alone, dropped `subgrid` leave one explicit column, `grid-column: 2` open _implicit_ second track: note beside paragraph at whatever width it take, no gutter (`column-gap` on `.lesson`, not wrapper), body squeeze. Not documented degradation — collision.

## Signature — the retrieval gate

Cold open lesson's calibration surface. Body content below it **sealed**: dimmed, blurred, `inert`, small label ("Answer the cold open to unseal the lesson"). Every cold-open item answered, `quiz.js` drop `.sealed` and `inert` together, body quiet release. Cobalt top rule make one required action visible without turning it into a game show — embody retrieval-before-instruction, brief core mechanism.

Seal two halves, need both. Blur visible half; `inert` half that hold. Blur alone gate eye only — Tab still walk sealed lesson, screen reader still read it out, signature become decoration for exact reader who can't see it. `check_lesson.py` enforce pairing (`quiz-releases-not-inert`). Label text come from `data-seal-label` on sealed element so non-English lesson can translate it; CSS literal stay as fallback.

Instruction need third piece, same reason `inert` exist. Veil label CSS content **inside** inert subtree, and inert prune that subtree from accessibility tree outright — sentence gate exist to give land nowhere, screen-reader user tab out of cold open into body simply absent, unexplained. So `.seal-note` carry sentence as real text, sibling of quiz, outside seal. It `role="status"` because `quiz.js` swap its text on release: unseal move no focus, own no live region of its own, so otherwise page largest state change silent for everyone not watching. Unlike `.quiz-fb` it start **full** — first string page copy, read in order; only swap announcement. Revisit unseal from remembered state, no gate to explain, so that path remove element rather than assert release that didn't happen.

Swap text come from `data-unsealed-label` on `.seal-note`, so translate with lesson, carry one instruction page otherwise never give: **paste result line back**. Without it, cold open end in mono box reading `Cold open 0007-x: 1 right, 2 wrong` beside Copy button, nothing on page say what either for — spaced-repetition loop depend on learner action lesson never ask for. Slot cost nothing: release announcement had to happen anyway.

Quiet on purpose: faint veil, cobalt rule, small uppercase label. No confetti, no green flash. `prefers-reduced-motion` mean no transition, instant release; veil stay, blur static mask not movement — cancel it, reduced-motion reader read whole sealed lesson at 35% opacity. Seal state, not performance.

## Components

- **Cold open** — `.cold-open`, `--paper-2` calibration field, 4px cobalt top rule, fine frame. Hold quiz. Field span both column; what it hold stay bound to `--measure`, so cold-open quiz and practice quiz further down same lesson one component at one width, ✓ mark stay next to word it mark.
- **Lead** — `.lead` on opening paragraph. One thing lesson land, set above body size. At body size it read as first paragraph, not claim rest of page argue.
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

  `.quiz-result` carry **no** `hidden` — `quiz.js` never unhide it, so hidden one result line, and scoring affordance, nobody ever see. `role="group"` + `aria-labelledby` tie option to own question: three sibling button carry no question with them, so on item 2 of 3 screen reader otherwise offer bare option list.

  Equal-width `.quiz-btn` option so formatting never leak answer (rule from [SKILL.md](../SKILL.md) `## Skills`; same character-count per option where possible). Right/wrong carry mono ✓/✗ mark plus border + tint — border colour and tint both colour, mark what keep state readable without it. Answered option carry `aria-disabled`: still focusable, mark stay reachable, but no longer offer action that do nothing. Result line and per-item feedback `role="status"`: both appear without focus moving, unannounced result line a result line screen-reader user never learn exist — so both start **empty and in tree**, and `quiz.js` fill them. Live region that arrive already full the case screen reader most often miss. `.quiz-fb` keep its `hidden` and authored text in markup, what a no-JS page need; init hoist that text into JS and empty element. Copy control must work on `file://` — no copy control, no spaced-repetition loop. This section quiz contract; [`templates/assets/quiz.js`](../../../templates/assets/quiz.js) implement it.

  **Undo window.** Answer not final instant clicked. Chosen option go to neutral `data-state="chosen"` mark, `.quiz-undo` appear, item lock three second later. Nothing about answer reveal inside that window — no right/wrong, no correct option, no feedback. Reveal-then-undo would hand back free retry with answer already on screen, and that one thing retrieval measurement can't survive. Once locked, no retry: window buy back tap, never recall. Reason it exist: this line reschedule memory record, so mis-tap noise recorded as signal.

  Copy control show only on first pass through gated cold open — revisit unseal from remembered state, practice quiz never gate, so neither produce line worth pasting. `data-lesson` bind line to own lesson.

- **Citations** — inline `a.cite` number real link to own `.sidenote` (`id="n1"`, `n2`, … in order); note itself sans, small, `--ink-soft`, hairline left rule, and a `<p>` rather than `<aside>` — aside here scoped to no sectioning element, so each note would land as own `complementary` landmark, finished lesson would bury `<main>` under dozen of them. `a.cite` take inline padding with cancelling negative margin: vertical padding on inline box don't touch line box, so tap target grow from 8px to something findable without pixel of reflow. Matter on phone, one place note moved away from claim it belong to. Beside paragraph, pairing obvious; on phone and paper note moved below claim, matching numeral only thing tying claim to source. `sup.cite` stay styled for lesson generated before link existed.
- **Knowledge / Skills** — `h2` section with `--rule` hairline above (structural divider, not decoration). Knowledge first, skill second.
- **Code** — `--mono` on `--paper-2`, 4px cobalt left rule, horizontal scroll.
- **Where next** — final block: one primary source (highest-trust thing found), cross-link to related lesson and reference doc by anchor, line invite follow-up question.

## Constraints

- **Offline** — no `@import`, no remote `url()`, no external `<script src>`, no stylesheet `<link>` to anywhere but `assets/`. System font stack only. Cable unplugged, page render.
- **Print** — collapse to one column (margin column no reader on paper), keep `--measure` (paper one medium where reader can't narrow window; unbounded page box 95-character line) _and drop block's own padding with it_, since `box-sizing` border-box and 2rem a side inside `max-width: --measure` 32rem column, not 36rem — page box has `@page` margin for that. Unseal content, drop sidenote inline as small footnote, drop `.seal-note` (on paper body already open, so line promising it sealed simply false), avoid page-break inside quiz item and `pre`. Colour not load-bearing (B&W print fine). Quiz option print as plain list, not hidden — hidden they leave question dangling on em-dash with nothing under it, and printed lesson meant to be worked through; only copy and undo control go. Sidenote link print URL after title: every claim cite, and citation whose URL never printed is citation reader can't follow.
- **Motion** — reduced-motion mean no transition, instant release; blur stay (static mask, not movement). Default motion subtle (seal ~0.2s, quiz state ~0.15s). No scroll reveal, no ambient animation.
- **Responsive** — below 64rem: single column, sidenote inline below anchor, cold-open full width, padding shrink, line length stay bounded.
- **a11y** — visible keyboard focus on every control **and every link**; control boundary on `--rule-2` (3:1), never `--rule`; quiz state signal by mark + border, not colour alone; answered option `aria-disabled`, still focusable; option grouped and labelled by own question; sealed body `inert`, not merely blurred; nothing inert subtree carry — `::after` label included — reach assistive technology, so gate instruction live outside it in `.seal-note`, and release announce there; state change that move no focus announce via `role="status"`, from live region empty and in tree before text arrive; focus never dropped by hiding control it sit on (`.quiz-undo` hand it back to chosen option); `prefers-reduced-motion` honoured; `forced-colors` opt-out on veil alone, whose background _is_ component (quiz state survive forced palette on its mark); sidenote are `<p>`, never `<aside>`, so citation don't each become landmark; `lang` set on `<html>`; `<main>` landmark wrap lesson.

## Validation

[`check_lesson.py`](../scripts/check_lesson.py) executable contract for static subset of this design — script is spec, so section don't restate its rule.

`scripts/` and `templates/` live at plugin root, alongside `skills/`. During session, working directory learner's workspace, never plugin, so call script through `${CLAUDE_PLUGIN_ROOT}` (substitute direct in this skill content), not hand-resolved path.

- `python "${CLAUDE_PLUGIN_ROOT}/skills/teach/scripts/check_lesson.py" --self` — run after editing template; validate `templates/lesson.html` against contract (must pass; catch spec/validator mismatch).
- `python "${CLAUDE_PLUGIN_ROOT}/skills/teach/scripts/check_lesson.py" <lesson-path>` — validate generated lesson for conformance (quiz structure, offline no-remote-refs, a11y static check). Step 6 of [SKILL.md](../SKILL.md) run this on every lesson before opening it.
- `python "${CLAUDE_PLUGIN_ROOT}/skills/teach/scripts/check_lesson.py" --type=reference <path>` — same for reference document; skip quiz and cold-open rule.

Shared assets carry a `teach-template-version` stamp. Bump both asset stamps on a release that requires copied workspace assets to change; `teach.py state` reports a stale copy (detect-only; never overwrite per-workspace topic component). This validator only checks document contract.

Static subset (quiz structure, offline, a11y) machine-enforced here. Non-static concern (result-line shape, print layout, motion) enforced by template-as-source, not this script.

## Reference docs

`reference/*.html` link same stylesheet, drop cold-open + sealed wrapper, lean on print CSS — read and printed, not worked through. Same token and component; no separate identity.
