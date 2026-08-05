# Lesson HTML Design

Design system for HTML this skill generate. One course identity cross every `lessons/*.html` and `reference/*.html` in workspace — set read as course, not pile one-offs.

Hard constraint from [SKILL.md](../SKILL.md) shape every choice — see [Constraints](#constraints). One file, three parts, read in order: direction, layout, the retrieval-gate signature, [what may vary per lesson](#variation), constraints and validation; then [Tokens](#tokens), every CSS token role; then [Components](#components), every reusable block a generated lesson emit and the [template argument](#template-arguments) table. One file because the three drift apart when they are three — a component change that needs a token and a validator rule is one edit here.

## Artifacts

Maintainable split — spec here, code as real file skill copy:

| File                                                                  | Role                          | Copied into workspace as |
| --------------------------------------------------------------------- | ----------------------------- | ------------------------ |
| [`templates/assets/roots.css`](../../../templates/assets/roots.css)   | Root variables (token values) | `assets/roots.css`       |
| [`templates/assets/styles.css`](../../../templates/assets/styles.css) | Screen and print rules        | `assets/styles.css`      |
| [`templates/assets/quiz.js`](../../../templates/assets/quiz.js)       | Reusable quiz widget          | `assets/quiz.js`         |
| [`templates/lesson.html`](../../../templates/lesson.html)             | Lesson skeleton + arguments   | `lessons/NNNN-slug.html` |

Edit template; don't fork per lesson. Lesson fill the `{{arguments}}` in skeleton — every word on the page arrive as argument, none from the template ([§ Template arguments](#template-arguments)) — link three local `assets/` file, and vary what [Variation](#variation) allow. Nothing more.

## Direction

Course-timetable study instrument, light. Cool blue-gray page, graphite ink, transit blue navigation and calibration signal; vermilion mark route stop and muted brick mark wrong answer. Serif body carry sustained reading, sans label and marginalia, mono code and spaced-repetition result line. Single body column, wide right margin hold citation as sidenote — margin earn width, every claim cite, so citation live beside claim, not inline footnote bomb.

Not cream-and-terracotta default (blue-gray not cream; transit blue not terracotta). Not dashboard blue: transit blue mark route, control and calibration, never drown reading surface. Not broadsheet multi-column (single column + margin; rules are study structure, not newspaper).

Lesson open as route card: header carry vertical transit rule and one vermilion stop, then route navigation name its four stop before retrieval gate. This sequence explain lesson shape without expose sealed body — recall, then the two thing the lesson teach, then where it lead. The stop labels are the lesson's own word for those four ([Variation](#variation)); the four stop and their order are not.

Voice: dropped-article style throughout this skill deliberate, load-bearing — preserve in edit; don't normalize to standard English.

## Icons

Shell carries a ten-icon set — heroicons (`@heroicons/react@2.2.0/24/outline`, MIT, source `tailwindlabs/heroicons`), inline `<svg class="icon">` at one anchor each. Inline, not sprite — offline-first (no remote `<use href>`), no asset copy step, color via `stroke="currentColor"` token-aware. Selection and authoring in [§ Icon — shell set](#icon--shell-set).

Rules:

- **One icon per anchor.** A new icon earns a place only where the surrounding text already names the gesture; adjacent text always carries the meaning, so every icon is `aria-hidden="true"`. Decorative, not informational.
- **No sprite file.** Per-use inline bytes are <2 KB total across the shell; sprite adds file copy, asset-staleness entry, and `check_lesson.py` doesn't validate `<use href>` resolve. Add sprite when icon count past ~15 or any single lesson repeats an icon >3×.
- **No web font, no iconfont.** Banned by `file://` constraint.
- **Print:** summary and lesson-nav icons are `display: none` in print CSS — they are interactive gestures, not content. Callout and synthesis icons print in `--ink`/inherit color.
- **No motion.** Icons aren't animated; motion budget belongs to quiz state, seal release, pointer interactions.

## Layout

Body column (`--measure`) + sidenote column (`--margin-w`), fixed gap between. `.lesson` take `width: fit-content`, plus bounded outer width, so desktop canvas breathe without outer whitespace swallowing course route. Everything default into body column; sidenote and `h2` opt out. Hairline separate, never box. Sidenote sit right after paragraph that cite it — grid auto-placement land it column 2 same row, beside own claim. Tablet and narrow screen collapse below.

Sidenote live **inside** `.lesson-content`, not after. Two reason, both load-bearing: outside sealed wrapper they read plain while gate shut (citation text leak lesson); and — since sealed wrapper single grid item holding whole body — sidenote outside can only stack below entire lesson, never beside paragraph. So `.lesson-content` span both column, take `grid-template-columns: subgrid`, re-expose parent two column to paragraph and sidenote nested in it. Where subgrid unsupported, `@supports not` block block the wrapper, body fall back to one column with sidenote inline below anchor — narrow-screen layout, degradation not break. That fallback must be asked for. Left alone, dropped `subgrid` leave one explicit column, `grid-column: 2` open _implicit_ second track: note beside paragraph at whatever width it take, no gap (`column-gap` on `.lesson`, not wrapper), body squeeze. Not documented degradation — collision.

## Signature — the retrieval gate

Cold open lesson's calibration surface. Body content below it **sealed**: dimmed, blurred, `inert`, small label (`SEAL-LABEL` — the lesson's own line; the CSS literal is fallback). Every cold-open item answered, `quiz.js` drop `.sealed` and `inert` together, body quiet release. Cobalt top rule make one required action visible without turning it into a game show — embody retrieval-before-instruction, brief core mechanism.

Seal two halves, need both. Blur visible half; `inert` half that hold. Blur alone gate eye only — Tab still walk sealed lesson, screen reader still read it out, signature become decoration for exact reader who can't see it. `check_lesson.py` enforce pairing (`quiz-releases-not-inert`). Label text come from `data-seal-label` on sealed element and nowhere else — the stylesheet keep no English literal behind it, because that fallback only ever render for the lesson that forgot the attribute, and it render in the wrong language. Sealed body without it fail instead (`seal-label-missing`).

Instruction need third piece, same reason `inert` exist. Veil label CSS content **inside** inert subtree, and inert prune that subtree from accessibility tree outright — sentence gate exist to give land nowhere, screen-reader user tab out of cold open into body simply absent, unexplained. So `.seal-note` carry sentence as real text, sibling of quiz, outside seal. It `role="status"` because `quiz.js` swap its text on release: unseal move no focus, own no live region of its own, so otherwise page largest state change silent for everyone not watching. Unlike `.quiz-fb` it start **full** — first string page copy, read in order; only swap announcement. Revisit unseal from remembered state, no gate to explain, so that path remove element rather than assert release that didn't happen.

Swap text come from `data-unsealed-label` on `.seal-note`, so translate with lesson, carry one instruction page otherwise never give: **paste result line back**. Without it, cold open end in mono box reading `Cold open 0007-x: 1 right, 2 wrong` beside Copy button, nothing on page say what either for — spaced-repetition loop depend on learner action lesson never ask for. Slot cost nothing: release announcement had to happen anyway.

Quiet on purpose: faint veil, cobalt rule, small uppercase label. No confetti, no green flash. `prefers-reduced-motion` mean no transition, instant release; veil stay, blur static mask not movement — cancel it, reduced-motion reader read whole sealed lesson at 35% opacity. Seal state, not performance.

## Variation

Learner who can predict page before it load stop reading it. Lesson 12 must not be lesson 1 with different word. Template carry argument, not copy ([§ Template arguments](#template-arguments)) — what a lesson choose:

- **Every string.** All copy arrive as [template argument](#template-arguments), route stop label and section heading included. The strings `quiz.js` write at runtime — progress count, undo, copy status — are not arguments but still not the widget's to keep: each take an override attribute on `<html>`, set once for the whole lesson, and the `QUIZ-STRINGS` slot is the template's reminder that they exist at all ([§ Quiz](#quiz)). A callout's visible label is the same case — `data-type` name it in English until `data-callout-label` take over ([§ Callout](#callout)). Between them, nothing English reach a non-English learner.
- **Which optional component appear, and in what order** — `KNOWLEDGE-BLOCKS` and `SKILLS-BLOCKS` are free slots. Callout, figure, self-explanation, aside, worked example, practice quiz, further sidenote: order inside a section carry no meaning, so it is the lesson's. Gate the choice on record state (fading rule), never on variety for its own sake.
- **Which optional line appear at all** — an argument marked optional ([§ Template arguments](#template-arguments)) drop with its element. A lesson that keep every one of them is a lesson shaped by the template.
- **Accent** — `<html data-accent>`, closed set of hue name. Hue only: light, dark and print keep their own lightness.
- **Density** — `<html data-density>`, section rhythm only. Short lesson breathe less, long lesson breathe more; component padding and `--measure` never move.

Both hooks in [§ Per-lesson hooks](#per-lesson-hooks). Name, never value — a colour written into a lesson restate a token and the next edit to `roots.css` miss it. `check_lesson.py` take the allowed name from the linked stylesheet and fail any other (`unknown-accent`, `unknown-density`); an unknown name would otherwise fall back to the default and read as correct. Inline `<style>` does not widen the set — a lesson that define its own hue rule is the case this rule exist to stop.

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

Static subset (quiz structure, offline, a11y) machine-enforced here. Non-static concern (result-line shape, print layout, motion, component content) enforced by template-as-source and [Components](#components), not this script.

## Reference docs

`reference/*.html` link same stylesheet, drop cold-open + sealed wrapper, lean on print CSS — read and printed, not worked through. Same token and component; no separate identity.

## Tokens

Token role and rationale for lesson CSS. Value live in [`templates/assets/roots.css`](../../../templates/assets/roots.css) `:root` — single source. Edit there; never restate value here or anywhere. Name and role only — no value here, on purpose. Value drift when restated.

| Token           | Role                                 |
| --------------- | ------------------------------------ |
| `--paper`       | cool blue-gray page surface          |
| `--paper-2`     | pale field, cold-open field, code    |
| `--paper-3`     | deeper field, route bar              |
| `--ink`         | graphite body text                   |
| `--ink-soft`    | secondary text, marginalia           |
| `--rule`        | hairlines                            |
| `--rule-2`      | control boundaries (quiz options)    |
| `--accent-h`    | accent hue — the one per-lesson knob |
| `--accent`      | cobalt — gate, correct, links        |
| `--accent-bg`   | cobalt tint — active control bg      |
| `--signal`      | vermilion — route stop, release edge |
| `--wrong`       | wrong (muted brick, never alarm-red) |
| `--success`     | correct (muted green)                |
| `--serif`       | body face (sustained reading)        |
| `--sans`        | labels and marginalia face           |
| `--mono`        | code and result-line face            |
| `--s-1`…`7`     | space ladder — margins and padding   |
| `--measure`     | body line length                     |
| `--margin-w`    | sidenote column width                |
| `--radius`      | corner radius, controls and code     |
| `--radius-sm`   | small radius — option markers        |
| `--tap`         | minimum touch target (44px)          |
| `--stop-size`   | route-stop circle diameter           |
| `--rule-thin`   | 2px — hairlines, focus outlines      |
| `--rule-thick`  | 3px — accent stripes, feedback bars  |
| `--ease-out`    | standard easing curve                |
| `--ease-spring` | spring easing — press transforms     |
| `--shadow-sm`   | hairline elevation                   |

Why these token, not others:

- **System-only type stacks.** Web font banned on `file://` — no CDN, no remote `@import`, cable unplugged, page still render. Serif stack ship on Windows + macOS, degrade clean; sans and mono ride OS default. No web font worth network dependency brief forbid.
- **`--measure` bound line length** for sustained reading. Width typographic decision, not layout accident — body column past ~36rem stop being read, start being scanned.
- **`--margin-w` earn its width** because every claim cite. Citation live beside claim as sidenote, not bunch as inline footnote bomb. Margin structural, not decorative.
- **`--wrong` muted oxblood, never alarm-red.** Wrong answer teaching signal, not emergency. Red shout; oxblood correct quiet, keep page calm.
- **One space ladder, not free value.** Structural gap come off `--s-*`; rare quarter-rem optical adjustment stay beside component it tune. Type size live at use — page has few roles, named ladder hide more than it help.
- **`--accent-h` is hue alone, not a second accent.** Light, dark and print each set `--accent`'s own lightness and chroma; a per-lesson rule that set `--accent` outright would out-specify all three and drag a light-mode colour into dark. Hue is the one part safe to vary, so it is the only part that varies.
- **`--rule-2` exist because `--rule` too faint to be edge.** Hairline separate; control boundary must be _found_. Quiz option border only thing saying "this is clickable", `--rule` sit near 1.5:1 on paper — under 3:1 control boundary owe. Two token, two job; never use `--rule` on interactive edge.

## Per-lesson hooks

Two attribute on `<html>`, both optional, both a **name from a closed set** — never a value. Value live in `roots.css` beside the token they move, so one edit there move every lesson that pick that name. Rationale and the identity limit: [§ Variation](#variation).

| Attribute      | Values                                       | Moves                                                                                 |
| -------------- | -------------------------------------------- | ------------------------------------------------------------------------------------- |
| `data-accent`  | `cobalt` (default), `teal`, `violet`, `plum` | `--accent-h`, and so `--accent` (and `--accent-bg` in dark, where the tint carry hue) |
| `data-density` | `compact`, `roomy`                           | `--s-5`, `--s-6`, `--s-7` — section rhythm                                            |

Attribute absent read as the default; a lesson that want the default drop the attribute rather than spell it. Density has no `default` name for that reason — the base `:root` is it, and a name would restate values that already live there.

`check_lesson.py` read the allowed name straight out of the linked CSS and fail a lesson that use any other (`unknown-accent`, `unknown-density`) — a misspelt name would otherwise render the default and look correct. Add a name to `roots.css` and it is allowed; this table is documentation, never the source, and the one table — template and [the argument table](#template-arguments) point here rather than restate the names, so a fifth copy cannot drift.

`<html>` carry a third kind of hook that is no token: the `data-*` overrides for words `quiz.js` write, which the `QUIZ-STRINGS` slot above the tag exist to remind ([§ Quiz](#quiz)). Same element, different layer — string, not value.

`--signal` take no hook: vermilion mark route stop and release edge in every lesson, and that is course identity, not lesson choice.

## Components

Spec for every reusable block a generated lesson emit. Every component here is plain HTML + the shared stylesheet; nothing needs a new script. Offline-only, print-friendly — see [§ Constraints](#constraints).

## Template arguments

[`templates/lesson.html`](../../../templates/lesson.html) is skeleton plus argument — no fixed lesson copy left in it. Two brace forms, one convention:

- `{{UPPER-KEBAB}}` — **named argument**, table below. Wording is the lesson's, never the template's.
- `{{lowercase prose}}` — fill-in guidance at point of use (a sidenote line, a synthesis point). Not named, not tabled.

Argument marked _optional_ in the table drop with the element that hold it — that is the point of it, one fewer fixed line every lesson repeat. Every other one fill.

Both gone from a finished lesson: `check_lesson.py` reject any surviving `{{` (`unfilled-placeholder`), except inside `<pre>`/`<code>`, where a lesson teaching a brace-syntax template language need them. What a lesson may vary beyond its copy — optional block choice and order, accent, density — and what it may not: [§ Variation](#variation).

| Argument                                                               | Slot                                 | Fill with                                                                                                                   |
| ---------------------------------------------------------------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `LANG`                                                                 | `<html lang>`                        | BCP-47 tag of the language lesson written in                                                                                |
| `ACCENT`                                                               | `<html data-accent>`                 | a name from [§ Per-lesson hooks](#per-lesson-hooks) — never a colour; drop attribute for default                            |
| `DENSITY`                                                              | `<html data-density>`                | a name from the same table; drop attribute for default                                                                      |
| `QUIZ-STRINGS`                                                         | comment above `<html>`               | optional — the `data-*` overrides this lesson need for words `quiz.js` write ([Quiz](#quiz)) go on `<html>`; delete comment |
| `TITLE`                                                                | `<title>`, `h1`                      | lesson title                                                                                                                |
| `TOPIC`                                                                | `<title>`                            | course topic                                                                                                                |
| `EYEBROW`                                                              | `.lesson-header .eyebrow`            | where lesson sit, e.g. `Lesson 4 · ownership`                                                                               |
| `LEAD`                                                                 | `.lead`                              | one thing lesson land — see [Lead](#lead)                                                                                   |
| `ROUTE-LABEL`                                                          | `.toc` `aria-label` + `.toc-eyebrow` | what the route is called; same string both slots                                                                            |
| `STOP-1`…`STOP-4`                                                      | route stops, and `h2` of section 2–4 | [Lesson route](#lesson-route)                                                                                               |
| `RECORD-ID`                                                            | `<!-- cold-open: … -->`              | `NNNN-slug` of record each item test — one pair per `.quiz-item`                                                            |
| `COLD-OPEN-TITLE`, `COLD-OPEN-INTRO`                                   | `.cold-open`                         | [Cold open](#cold-open)                                                                                                     |
| `COLD-OPEN-EYEBROW`                                                    | `.cold-open .eyebrow`                | optional — drop the `p` when the title carry it; [Cold open](#cold-open)                                                    |
| `QUIZ-LABEL`                                                           | `.quiz` `data-label`                 | head of result line; free text, scoring key on the id that follow it                                                        |
| `LESSON-ID`                                                            | `.quiz` `data-lesson`                | own file stem, `NNNN-slug`                                                                                                  |
| `QUESTION`, `OPT`, `FEEDBACK`                                          | `.quiz-item`                         | [Quiz](#quiz)                                                                                                               |
| `COPY-LABEL`                                                           | `.quiz-copy`                         | copy-control label                                                                                                          |
| `SEAL-NOTE`, `UNSEALED-LABEL`                                          | `.seal-note`                         | [§ Signature](#signature--the-retrieval-gate)                                                                               |
| `SEAL-LABEL`                                                           | `.lesson-content` `data-seal-label`  | the veil's own line — the only text the veil have, so a sealed body without it fail (`seal-label-missing`)                  |
| `BODY`                                                                 | first `<p>` under Knowledge          | [SKILL.md](../SKILL.md) `## Knowledge` authoring rules                                                                      |
| `URL`                                                                  | sidenote and body links              | citation target                                                                                                             |
| `KNOWLEDGE-BLOCKS`, `SKILLS-BLOCKS`                                    | after the Knowledge / Skills `h2`    | optional components this lesson earn, in the order it earn them                                                             |
| `SYNTHESIS-TITLE`, `SYNTHESIS-PROMPT`                                  | `.synthesis`                         | [Synthesis](#synthesis)                                                                                                     |
| `WHERE-NEXT`, `FOLLOW-UP`                                              | Where next                           | [Where next](#where-next)                                                                                                   |
| `NAV-LABEL`, `PREV-LABEL`, `NEXT-LABEL`                                | `.lesson-nav`                        | navigation labels                                                                                                           |
| `PREV-LESSON`, `PREV-LESSON-TITLE`, `NEXT-LESSON`, `NEXT-LESSON-TITLE` | `.lesson-nav`                        | neighbour file stem and title; no neighbour → drop that whole `.lesson-nav-cell`                                            |

## Lesson route

`.toc`, four ordered stops. Each anchor own square number; route show lesson scope before cold open, never use it as dense global navigation. Four-stop route is load-bearing — `check_lesson.py` fail a lesson that carry any other count (`route-four-stops`). Anchors fixed with it: `#recall`, `#knowledge`, `#skills`, `#where-next`.

Stop **labels** are the lesson's, through `STOP-1`…`STOP-4`. One label per stop, used twice: route stop 2–4 and the `h2` of the section it point at. Two names for one stop — a route saying "Understand" over a heading saying "Knowledge" — is the vocabulary drift this replaces. Keep the same four labels across a course; they translate once, not per lesson. Synthesis close the lesson but is not a route stop.

Stop 1 point at the cold open. Lesson with nothing due carry none (see below) — then `id="recall"` ride on `.lesson-header` and `STOP-1` name what the lesson actually open with.

## Cold open

`.cold-open`, `--paper-2` calibration field, transit-blue top rule, fine frame. `COLD-OPEN-TITLE` label it — over an optional `COLD-OPEN-EYEBROW`, which drop with its `p` when the title already say where the block sit; three stacked label on one small field is the sameness this template exist to avoid. `COLD-OPEN-INTRO` is one plain sentence explaining answer-from-memory and the release condition. Hold quiz. Field span both column; what it hold stay bound to `--measure`, so cold-open quiz and practice quiz further down same lesson one component at one width, ✓ mark stay next to word it mark.

**No due record, no cold open** ([SKILL.md](../SKILL.md) step 5). Then drop the whole `.cold-open` section and the `.seal-note` with it, drop `sealed`, `inert` and `data-seal-label` off `.lesson-content`, and re-anchor stop 1 per [Lesson route](#lesson-route). Half-dropping it is the failure: a sealed body with no quiz to release it is a lesson nobody can open, and `check_lesson.py` fail it (`sealed-never-released`) — the missing anchor is a separate catch, `broken-anchor`.

## Lead

`.lead` on opening paragraph. One thing lesson land, set above body size. At body size it read as first paragraph, not claim rest of page argue. The `.lead` is the output of reconciliation, not a restatement of the first source.

## Quiz

Shape only:

```html
<div class="quiz" data-releases="contentId" data-label="…" data-lesson="NNNN-slug">
  <div class="quiz-item" role="group" aria-labelledby="q1" data-correct="0">
    <p class="quiz-q" id="q1">…</p>
    …<button class="quiz-btn" type="button">…</button>…
  </div>
  <p class="quiz-result" role="status"></p>
  <button class="quiz-copy" type="button" hidden>…COPY-LABEL…</button>
</div>
<p class="seal-note" role="status">…</p>
```

`.quiz-result` carry **no** `hidden` — `quiz.js` never unhide it, so hidden one result line, and scoring affordance, nobody ever see. `role="group"` + `aria-labelledby` tie option to own question: three sibling button carry no question with them, so on item 2 of 3 screen reader otherwise offer bare option list.

Two to four `.quiz-btn` per item; count is the lesson's, `data-correct` a 0-based index into it, and `check_lesson.py` range-check the pair. Equal-width `.quiz-btn` option so formatting never leak answer (rule from [SKILL.md](../SKILL.md) `## Skills`; same character-count per option where possible). Right/wrong carry mono ✓/✗ mark plus border + tint — border colour and tint both colour, mark what keep state readable without it. Answered option carry `aria-disabled`: still focusable, mark stay reachable, but no longer offer action that do nothing. Result line and per-item feedback `role="status"`: both appear without focus moving, unannounced result line a result line screen-reader user never learn exist — so both start **empty and in tree**, and `quiz.js` fill them. Live region that arrive already full the case screen reader most often miss. `.quiz-fb` keep its `hidden` and authored text in markup, what a no-JS page need; init hoist that text into JS and empty element. Copy control must work on `file://` — no copy control, no spaced-repetition loop. This section quiz contract; [`templates/assets/quiz.js`](../../../templates/assets/quiz.js) implement it.

**Labels.** Every string `quiz.js` write into a page live in one place — its `DEFAULTS` map — and every one take an override attribute. Put the attribute **on `<html>`** and it cover the whole lesson; put it on one `.quiz` and that quiz win, because the widget resolve with `closest()`. So a non-English course set what it need beside `lang` once, and never fork the widget. The `QUIZ-STRINGS` comment above `<html>` is the reminder they exist: fill the attributes onto `<html>` and delete it, or delete it unfilled when the course is English — either way `check_lesson.py` catch a lesson that ignored it.

Restating a default in markup is a second copy that drift, so a lesson spell out only what it change. The template spell out two, both for a reason a default cannot cover: `data-label`, which genuinely differ between a cold open and a practice quiz in the same lesson, and `data-unsealed-label`, which carry the paste-back instruction the default (`Lesson unsealed.`) leave out — see [§ Signature](#signature--the-retrieval-gate).

| Attribute                | Fills                                    | Default                                                           |
| ------------------------ | ---------------------------------------- | ----------------------------------------------------------------- |
| `data-label`             | head of the result line (`QUIZ-LABEL`)   | `Cold open`                                                       |
| `data-progress-label`    | `.quiz-progress`, any quiz past one item | `{n} of {total} answered`                                         |
| `data-undo-label`        | undo control; countdown append to it     | `Undo`                                                            |
| `data-copied-label`      | copy control, briefly, after a copy      | `Copied`                                                          |
| `data-copied-status`     | `.quiz-copy-status` after a copy         | `Result copied. Paste it into your next message to your teacher.` |
| `data-copy-failed-label` | `.quiz-copy-status` after a failed copy  | `Copy failed. Result selected; copy it manually.`                 |
| `data-unsealed-label`    | `.seal-note` once the body release       | `Lesson unsealed.`                                                |

`{n}` and `{total}` fill from the widget. Keep the slot, move it where the sentence need it — a translation own its own word order, which is why the widget never glue a number onto a fragment.

`teach.py score` key on the `NNNN-slug` at the end of the head, never on `data-label` words, so translating the label cannot break scoring.

**Feedback content (load-bearing).** Per-item feedback text must state _why_ the correct option is correct and _why_ the chosen wrong option is wrong, not merely confirm or reject. The high-information gain live in this text (Wisniewski 2020: d=0.99 high-information vs d=0.24 reinforcement-only); the scoring result line is KR-level (right/wrong counts) for scheduling, not for learning, so the per-item feedback carry all the specificity. Authoring rule, not a markup change — the `.quiz-fb` slot already exist.

**Undo window.** Answer not final instant clicked. Chosen option go to neutral `data-state="chosen"` mark, `.quiz-undo` appear, item lock three second later. Nothing about answer reveal inside that window — no right/wrong, no correct option, no feedback. Reveal-then-undo would hand back free retry with answer already on screen, and that one thing retrieval measurement can't survive. Once locked, no retry: window buy back tap, never recall. Reason it exist: this line reschedule memory record, so mis-tap noise recorded as signal.

Copy control show only on first pass through gated cold open — revisit unseal from remembered state, practice quiz never gate, so neither produce line worth pasting. Successful copy announce that learner paste result into next message to teacher. `data-lesson` bind line to own lesson.

## Worked example

`.worked-example` in the Skills section — the single highest-leverage cognitive-load technique for written instruction, and the one an adaptive system can taper as expertise grows (expertise reversal: worked examples become redundant load for competent learners and can reverse — Kalyuga; Sweller/van Merriënboer/Paas). One fully worked example, then a parallel bare problem. Density scale with record state — see [SKILL.md](../SKILL.md) `## Skills` fading rule.

```html
<div class="worked-example">
  <p class="we-problem">…one problem statement…</p>
  <ol class="we-steps">
    <li>
      <span class="we-action">…do this…</span>
      <span class="we-why">— principle that justify the step…</span>
    </li>
    …
  </ol>
  <p class="we-takeaway">…one-line takeaway…</p>
</div>
```

Each step carry the _why_, not just the _what_ — process-oriented example improve far transfer (van Gog). Style as ordered list with cobalt left rule, mirroring the `code` block so it read as one component. No inline bold — `.we-action` is the run-in label (see Emphasis below).

## Self-explanation reveal

Open-ended prompt after the Knowledge or at a worked-step boundary, with a model-answer reveal. Must be open-ended (free reveal), **not** multiple-choice — meta-analysis show MC self-explanation prompts fail (Bisra 2018: MC g=0.24 ns; open-ended g=0.67). Reuse native `<details>`:

```html
<details class="self-explain">
  <summary>
    <svg class="icon icon-closed" viewBox="0 0 24 24" aria-hidden="true">
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M9 15 3 9m0 0 6-6M3 9h12a6 6 0 0 1 0 12h-3"
      />
    </svg>
    <svg class="icon icon-open" viewBox="0 0 24 24" aria-hidden="true">
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="m15 15 6-6m0 0-6-6m6 6H9a6 6 0 0 0 0 12h3"
      />
    </svg>
    In your own words: why does … hold?
  </summary>
  <div class="self-explain-model">…model answer…</div>
</details>
```

Distinct from cold open: cold open test prior record; self-explanation elaborate the current lesson. Keep one per non-trivial worked step or concept; not a new widget, just `<details>` with the shared style. Summary carry a closed/open icon pair as the first child — `arrow-uturn-left` (closed) and `arrow-uturn-right` (open) — decorative, both rendered, CSS toggle one off on `[open]`; `<summary>` text adjacent already names what unlocks. Lesson language switch carries the icon shape, not a CSS `+`/`−` glyph.

## Details — optional depth

Native `<details>`/`<summary>` for genuinely optional deeper content (a worked derivation, an edge case, a longer aside) inside the body. Offline, prints sensibly, no JS. Cap one nesting level. Label `summary` with real information scent ("How we chose this threshold"), never hide a prerequisite. Self-explanation (above) is its primary use; a plain `<details class="aside">` serve other optional depth.

```html
<details class="aside">
  <summary>…same closed/open icon pair as above…How we chose this threshold</summary>
  …
</details>
```

## Synthesis

`<section class="synthesis">` between Skills and Where next — the consolidation slot. Student-led synthesis in the final stretch protect retention (Villarreal 2025; ICAP constructive above passive); re-stating the rule after practice consolidate the schema (LearnLab example-rule coordination). Not a route stop — the four-stop route stay four.

```html
<section class="synthesis" id="synthesis">
  <h2>
    <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">…sparkles…</svg>…SYNTHESIS-TITLE…
  </h2>
  <ul class="synthesis-points">
    <li>…core idea, one line…</li>
    …3–5…
  </ul>
  <p class="synthesis-rule">…re-state the core rule in light of what practice showed…</p>
  <p class="synthesis-prompt">
    …SYNTHESIS-PROMPT: say it back in your own words, then have it checked…
  </p>
</section>
```

The prompt is a retrieval nudge that feed the spaced-repetition loop. Keep "Where next" navigation-only; synthesis carry consolidation.

## Callout

`.callout`, a typed aside for a common pitfall, a by-the-way, an optional better way, or an irreversible action. No sanctioned home for these existed, so warning got buried as prose or bold got abused.

```html
<div class="callout" data-type="warning" role="note">
  <svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
    <path
      stroke-linecap="round"
      stroke-linejoin="round"
      d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
    />
  </svg>
  <p>…</p>
</div>
```

`data-type`: `note` (by-the-way), `tip` (optional better way), `warning` (common pitfall), `caution` (irreversible / data-loss). Left rule reuses `--accent`/`--signal`/`--wrong` by type; sans label, kept short.

Cap one or two per lesson, never stacked, placed beside the content it qualify — visually distinct from citation sidenote (full-width block, not margin). Each callout carry a type-specific `<svg class="icon">` as the first child — `information-circle` (note), `light-bulb` (tip), `exclamation-triangle` (warning), `lock-closed` (caution) — decorative (`aria-hidden="true"`); adjacent text label and stripe color carry the meaning. Path data copy from heroicons/24/outline.

The printed label is the type name itself, so a bare `data-type` ship an English word into every callout. Add `data-callout-label="…"` and the lesson word win — a non-English course need it, and a lesson that want `Pitfall` over `Warning` may take it. Stripe colour and icon still key on `data-type`, so the type stay the type. Not plain `data-label`: `quiz.js` resolve that name through `closest()`, so a quiz inside the callout would take the callout word as its result-line head.

## Figure — diagram

Optional `<figure class="diagram">` for inline SVG or a local `assets/` image. Words + images beat words alone — the most robust CTML finding (Mayer 2024, 200+ experiments) — and inline SVG fit `file://` with no dependency. Gate on record state like the worked-example rule: graphic help low-knowledge learner but **hamper** high-knowledge (Vogt 2020, expertise reversal), so do not add a diagram to a lesson a competent learner see.

```html
<figure class="diagram">
  <svg viewBox="0 0 320 180" role="img" aria-labelledby="d1-title">
    <title id="d1-title">…</title>
    …
  </svg>
  <figcaption>
    …caption; cite the claim it illustrate via <a class="cite" href="#n1">1</a>…
  </figcaption>
</figure>
```

A local image take the same frame — `<img src="assets/…png" alt="…" />` in place of the `<svg>`, and the asset copied into workspace `assets/` first.

Offline enforced by `check_lesson.py` (any `<img>`/`srcset` remote or missing fail). Prefer inline SVG — no asset to copy, no stale-asset drift. The "diagram helper" named in [SKILL.md](../SKILL.md) `## Assets` is a reusable SVG component in `assets/`, not a script.

## Analogy

Authoring rule, not a new block: when introducing a concept via analogy, (1) name source and target, (2) explicitly map correspondences — a small 2-column table or short list, (3) name at least one place the analogy breaks (`unlike: …`). Analogies help only when correspondences are mapped _and_ breakdown points named (Gentner structure-mapping; FAR guide). Render the "where it fails" line as a `.callout` `data-type="note"`. The mapping itself is a plain table (see prose-vs-table rule in [SKILL.md](../SKILL.md) `## Knowledge`).

## Emphasis

Emphasis authoring rule: see [SKILL.md](../SKILL.md) `## Knowledge`. Headings carry scan weight, not inline bold — do not bold to "make important". The `.lead` is italic by stylesheet, not by author hand.

## Citations

```html
<p>…claim…<a class="cite" href="#n1">1</a></p>
<p class="sidenote" id="n1">¹ <a href="…">Author, Title</a> — one line on what it covers.</p>
```

One `.sidenote` per citation, numbered in order, each right after the paragraph that cite it — the count is the lesson's, and the template ship exactly one as the shape. A lesson with six claims carry six; a Where next that cite nothing carry none there. Sidenote live inside `.lesson-content` ([§ Layout](#layout)).

Inline `a.cite` number real link to own `.sidenote` (`id="n1"`, `n2`, … in order); note itself sans, small, `--ink-soft`, hairline left rule, and a `<p>` rather than `<aside>` — aside here scoped to no sectioning element, so each note would land as own `complementary` landmark, finished lesson would bury `<main>` under dozen of them. `a.cite` take inline padding with cancelling negative margin: vertical padding on inline box don't touch line box, so tap target grow from 8px to something findable without pixel of reflow. Matter on phone, one place note moved away from claim it belong to. Beside paragraph, pairing obvious; on phone and paper note moved below claim, matching numeral only thing tying claim to source.

## Knowledge / Skills

`h2` section with route-stop mark and `--rule` hairline above (structural divider, not decoration). Knowledge first, skill second. Knowledge section manage intrinsic load (one tightly-scoped thing); Skills section reduce difficulty for high-element-interactivity task — worked example then fading — the corollary of desirable difficulty that live in the cold open (Pyke 2024): difficulty desirable for low-element-interactivity retrieval, reduced for high-element-interactivity skill.

## Code

`--mono` on `--paper-2`, 4px cobalt left rule, horizontal scroll.

## Where next

Final block: one primary source (highest-trust thing found), cross-link to related lesson and reference doc by anchor, line invite follow-up question. Navigation only — consolidation live in [Synthesis](#synthesis). Wording is the lesson's (`WHERE-NEXT`, `FOLLOW-UP`); the four link shapes are not, because a lesson live in `lessons/` and every relative depth here is a link `check_lesson.py` will call broken:

```html
<a href="https://…">…primary source…</a>
<a href="NNNN-slug.html">…related lesson…</a>
<a href="../reference/slug.html#anchor">…reference doc…</a>
<a href="../index.html">…course home…</a>
```

## Icon — shell set

Inline heroicons (`@heroicons/react@2.2.0/24/outline`, MIT, source `tailwindlabs/heroicons`). One `<svg class="icon">` per anchor, `aria-hidden="true"`, path data copied verbatim from `heroicons/optimized/24/outline/<name>.svg`. Color via `stroke="currentColor"` — callout and route hooks set `color` token-specific. The selection is the only sanctioned shell set; a lesson reach for a different icon only at `<figure class="diagram">` (which gate on record state per [Figure](#figure--diagram)) with the same inline approach.

| Icon                   | Where                                     | Why                                        |
| ---------------------- | ----------------------------------------- | ------------------------------------------ |
| `academic-cap`         | `.lesson-header > .eyebrow`               | "Lesson" affordance — study instrument     |
| `arrow-long-left`      | `.lesson-nav-link` previous               | paired glyph replaces `←`                  |
| `arrow-long-right`     | `.lesson-nav-link` next                   | paired glyph replaces `→`                  |
| `exclamation-triangle` | `.callout[data-type="warning"]`           | common-pitfall glyph                       |
| `light-bulb`           | `.callout[data-type="tip"]`               | optional-better-way glyph                  |
| `information-circle`   | `.callout[data-type="note"]`              | by-the-way glyph                           |
| `lock-closed`          | `.callout[data-type="caution"]`           | irreversible-action glyph                  |
| `arrow-uturn-left`     | `.self-explain` / `.aside` summary closed | universal expand affordance                |
| `arrow-uturn-right`    | same, open                                | universal collapse affordance              |
| `sparkles`             | `.synthesis > h2`                         | consolidation marker; vermilion `--signal` |

Wrapper, drop into any use site:

```html
<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
  <path stroke-linecap="round" stroke-linejoin="round" d="…path from heroicons repo…" />
</svg>
```
