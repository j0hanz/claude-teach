# Lesson HTML Design

Design system for HTML this skill generate. One course identity cross every `lessons/*.html` and `reference/*.html` in workspace — set read as course, not pile one-offs.

Hard constraint from [SKILL.md](../SKILL.md) shape every choice — see [Constraints](#constraints). This file hold direction, layout, the retrieval-gate signature, [what may vary per lesson](#variation), constraints and validation. Two peer reference hold the rest: [TOKENS.md](TOKENS.md) name every CSS token role; [COMPONENTS.md](COMPONENTS.md) spec every reusable block a generated lesson emit, and table every [template argument](COMPONENTS.md#template-arguments).

## Artifacts

Maintainable split — spec here and in peer references, code as real file skill copy:

| File                                                                  | Role                          | Copied into workspace as |
| --------------------------------------------------------------------- | ----------------------------- | ------------------------ |
| [`templates/assets/roots.css`](../../../templates/assets/roots.css)   | Root variables (token values) | `assets/roots.css`       |
| [`templates/assets/styles.css`](../../../templates/assets/styles.css) | Screen and print rules        | `assets/styles.css`      |
| [`templates/assets/quiz.js`](../../../templates/assets/quiz.js)       | Reusable quiz widget          | `assets/quiz.js`         |
| [`templates/lesson.html`](../../../templates/lesson.html)             | Lesson skeleton + arguments   | `lessons/NNNN-slug.html` |

Edit template; don't fork per lesson. Lesson fill the `{{arguments}}` in skeleton — every word on the page come from there, none from the template — link three local `assets/` file, and vary what [Variation](#variation) allow. Nothing more.

## Direction

Course-timetable study instrument, light. Cool blue-gray page, graphite ink, transit blue navigation and calibration signal; vermilion mark route stop and muted brick mark wrong answer. Serif body carry sustained reading, sans label and marginalia, mono code and spaced-repetition result line. Single body column, wide right margin hold citation as sidenote — margin earn width, every claim cite, so citation live beside claim, not inline footnote bomb.

Not cream-and-terracotta default (blue-gray not cream; transit blue not terracotta). Not dashboard blue: transit blue mark route, control and calibration, never drown reading surface. Not broadsheet multi-column (single column + margin; rules are study structure, not newspaper).

Lesson open as route card: header carry vertical transit rule and one vermilion stop, then route navigation name its four stop before retrieval gate. This sequence explain lesson shape without expose sealed body — recall, then the two thing the lesson teach, then where it lead. The stop labels are the lesson's own word for those four ([Variation](#variation)); the four stop and their order are not.

Voice: dropped-article style throughout this skill deliberate, load-bearing — preserve in edit; don't normalize to standard English.

## Icons

Shell carries a ten-icon set — heroicons (`@heroicons/react@2.2.0/24/outline`, MIT, source `tailwindlabs/heroicons`), inline `<svg class="icon">` at one anchor each. Inline, not sprite — offline-first (no remote `<use href>`), no asset copy step, color via `stroke="currentColor"` token-aware. Selection and authoring in [COMPONENTS.md § Icon — shell set](COMPONENTS.md#icon--shell-set).

Rules:

- **One icon per anchor.** A new icon earns a place only where the surrounding text already names the gesture; adjacent text always carries the meaning, so every icon is `aria-hidden="true"`. Decorative, not informational.
- **No sprite file.** Per-use inline bytes are <2 KB total across the shell; sprite adds file copy, asset-staleness entry, and `check_lesson.py` doesn't validate `<use href>` resolve. Add sprite when icon count past ~15 or any single lesson repeats an icon >3×.
- **No web font, no iconfont.** Banned by `file://` constraint.
- **Print:** summary and lesson-nav icons are `display: none` in print CSS — they are interactive gestures, not content. Callout and synthesis icons print in `--ink`/inherit color.
- **No motion.** Icons aren't animated; motion budget belongs to quiz state, seal release, pointer interactions.

## Layout

Body column (`--measure`) + sidenote column (`--margin-w`), fixed gap between. `.lesson` take `width: fit-content`, plus bounded outer width, so desktop canvas breathe without outer whitespace swallowing course route. Everything default into body column; sidenote and `.full` opt out. Hairline separate, never box. Sidenote sit right after paragraph that cite it — grid auto-placement land it column 2 same row, beside own claim. Tablet and narrow screen collapse below.

Sidenote live **inside** `.lesson-content`, not after. Two reason, both load-bearing: outside sealed wrapper they read plain while gate shut (citation text leak lesson); and — since sealed wrapper single grid item holding whole body — sidenote outside can only stack below entire lesson, never beside paragraph. So `.lesson-content` span both column, take `grid-template-columns: subgrid`, re-expose parent two column to paragraph and sidenote nested in it. Where subgrid unsupported, `@supports not` block block the wrapper, body fall back to one column with sidenote inline below anchor — narrow-screen layout, degradation not break. That fallback must be asked for. Left alone, dropped `subgrid` leave one explicit column, `grid-column: 2` open _implicit_ second track: note beside paragraph at whatever width it take, no gap (`column-gap` on `.lesson`, not wrapper), body squeeze. Not documented degradation — collision.

## Signature — the retrieval gate

Cold open lesson's calibration surface. Body content below it **sealed**: dimmed, blurred, `inert`, small label (`SEAL-LABEL` — the lesson's own line; the CSS literal is fallback). Every cold-open item answered, `quiz.js` drop `.sealed` and `inert` together, body quiet release. Cobalt top rule make one required action visible without turning it into a game show — embody retrieval-before-instruction, brief core mechanism.

Seal two halves, need both. Blur visible half; `inert` half that hold. Blur alone gate eye only — Tab still walk sealed lesson, screen reader still read it out, signature become decoration for exact reader who can't see it. `check_lesson.py` enforce pairing (`quiz-releases-not-inert`). Label text come from `data-seal-label` on sealed element so non-English lesson can translate it; CSS literal stay as fallback.

Instruction need third piece, same reason `inert` exist. Veil label CSS content **inside** inert subtree, and inert prune that subtree from accessibility tree outright — sentence gate exist to give land nowhere, screen-reader user tab out of cold open into body simply absent, unexplained. So `.seal-note` carry sentence as real text, sibling of quiz, outside seal. It `role="status"` because `quiz.js` swap its text on release: unseal move no focus, own no live region of its own, so otherwise page largest state change silent for everyone not watching. Unlike `.quiz-fb` it start **full** — first string page copy, read in order; only swap announcement. Revisit unseal from remembered state, no gate to explain, so that path remove element rather than assert release that didn't happen.

Swap text come from `data-unsealed-label` on `.seal-note`, so translate with lesson, carry one instruction page otherwise never give: **paste result line back**. Without it, cold open end in mono box reading `Cold open 0007-x: 1 right, 2 wrong` beside Copy button, nothing on page say what either for — spaced-repetition loop depend on learner action lesson never ask for. Slot cost nothing: release announcement had to happen anyway.

Quiet on purpose: faint veil, cobalt rule, small uppercase label. No confetti, no green flash. `prefers-reduced-motion` mean no transition, instant release; veil stay, blur static mask not movement — cancel it, reduced-motion reader read whole sealed lesson at 35% opacity. Seal state, not performance.

## Variation

Learner who can predict page before it load stop reading it. Lesson 12 must not be lesson 1 with different word. Template carry no fixed lesson copy for that reason — what a lesson choose:

- **Every string.** All copy arrive as [template argument](COMPONENTS.md#template-arguments), route stop label and section heading included. The strings `quiz.js` write at runtime — progress count, undo, copy status, serve-mode errors — are not arguments but still not the widget's to keep: each take an override attribute, set once on `<html>` for the whole lesson ([COMPONENTS.md § Quiz](COMPONENTS.md#quiz)). Between the two, nothing English reach a non-English learner.
- **Which optional component appear, and in what order** — `KNOWLEDGE-BLOCKS` and `SKILLS-BLOCKS` are free slots. Callout, figure, self-explanation, aside, worked example, practice quiz: order inside a section carry no meaning, so it is the lesson's. Gate the choice on record state (fading rule), never on variety for its own sake.
- **Accent** — `<html data-accent>`, closed set of four hue name. Hue only: light, dark and print keep their own lightness.
- **Density** — `<html data-density>`, section rhythm only. Short lesson breathe less, long lesson breathe more; component padding and `--measure` never move.

Both hooks in [TOKENS.md § Per-lesson hooks](TOKENS.md#per-lesson-hooks). Name, never value — a colour written into a lesson restate a token and the next edit to `roots.css` miss it.

What never vary, because it _is_ the course:

- four route stop, in order, on their fixed anchor (`#recall`, `#knowledge`, `#skills`, `#where-next`) — `check_lesson.py` enforce the count
- cold open before body, body sealed until every item answered (§ [Signature](#signature--the-retrieval-gate))
- section order: Knowledge, Skills, Synthesis, Where next
- the three shared `assets/` file, and the icon set with its anchor

Test for any change here: two lesson from one course, side by side, still one product. Two products mean it went too far.

## Constraints

- **Offline** — `file://`, no remote refs; enforced by `check_lesson.py` (see [SKILL.md](../SKILL.md) § Untrusted content). Not restated here — validator is spec.
- **Print**:
  - collapse to one column (margin column no reader on paper)
  - keep `--measure` — paper one medium where reader can't narrow window; unbounded page box 95-character line — and drop block's own padding with it, since `box-sizing` border-box and 2rem a side inside `max-width: --measure` 32rem column, not 36rem; page box has `@page` margin for that
  - unseal content; drop sidenote inline as small footnote
  - drop `.seal-note` — on paper body already open, so line promising it sealed simply false
  - avoid page-break inside quiz item and `pre`
  - colour not load-bearing (B&W print fine)
  - quiz option print as plain list, not hidden — hidden they leave question dangling on em-dash with nothing under it, and printed lesson meant to be worked through; only copy and undo control go
  - sidenote link print URL after title: every claim cite, and citation whose URL never printed is citation reader can't follow
- **Motion** — reduced-motion mean no transition, instant release; blur stay (static mask, not movement). Default motion subtle (seal ~0.2s, quiz state ~0.15s). No scroll reveal, no ambient animation.
- **Responsive** — below desktop reading width: single column, sidenote inline below anchor, cold-open full width, padding shrink, line length stay bounded. Narrow phone shrink outer padding once more; route stay visible and wrap clean.
- **a11y**:
  - visible keyboard focus on every control and every link
  - control boundary on `--rule-2` (3:1), never `--rule`
  - quiz state signal by mark + border, not colour alone
  - answered option `aria-disabled`, still focusable
  - option grouped and labelled by own question
  - sealed body `inert`, not merely blurred
  - nothing inert subtree carry — `::after` label included — reach assistive technology, so gate instruction live outside it in `.seal-note`, and release announce there
  - state change that move no focus announce via `role="status"`, from live region empty and in tree before text arrive
  - focus never dropped by hiding control it sit on (`.quiz-undo` hand it back to chosen option)
  - `prefers-reduced-motion` honoured
  - `forced-colors` opt-out on veil alone, whose background _is_ component (quiz state survive forced palette on its mark)
  - sidenote are `<p>`, never `<aside>`, so citation don't each become landmark
  - `lang` set on `<html>`
  - `<main>` landmark wrap lesson

## Validation

[`check_lesson.py`](../scripts/check_lesson.py) executable contract for static subset of this design — script is spec, so section don't restate its rule.

`scripts/` and `templates/` live at plugin root, alongside `skills/`. During session, working directory learner's workspace, never plugin, so call script through `${CLAUDE_PLUGIN_ROOT}` (substitute direct in this skill content), not hand-resolved path.

- `python "${CLAUDE_PLUGIN_ROOT}/skills/teach/scripts/check_lesson.py" --self` — run after editing template; validate `templates/lesson.html` against contract (must pass; catch spec/validator mismatch).
- `python "${CLAUDE_PLUGIN_ROOT}/skills/teach/scripts/check_lesson.py" <lesson-path>` — validate generated lesson for conformance (quiz structure, offline no-remote-refs, a11y static check). Step 6 of [SKILL.md](../SKILL.md) run this on every lesson before opening it.
- `python "${CLAUDE_PLUGIN_ROOT}/skills/teach/scripts/check_lesson.py" --type=reference <path>` — same for reference document; skip quiz and cold-open rule.

Shared assets carry a `teach-template-version` stamp. Bump every shared asset stamp on a release that requires copied workspace assets to change; `teach.py state` reports a stale copy (detect-only; never overwrite per-workspace topic component). This validator only checks document contract. Worked-example, synthesis, callout, figure and details component are authoring guidance, not machine-enforced — offline media inside a figure is still caught by the existing remote/missing-asset check.

Static subset (quiz structure, offline, a11y) machine-enforced here. Non-static concern (result-line shape, print layout, motion, component content) enforced by template-as-source and [COMPONENTS.md](COMPONENTS.md), not this script.

## Reference docs

`reference/*.html` link same stylesheet, drop cold-open + sealed wrapper, lean on print CSS — read and printed, not worked through. Same token and component; no separate identity.
