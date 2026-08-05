# Lesson HTML Design — Components

Spec for every reusable block a generated lesson emit. Companion to [DESIGN.md](DESIGN.md) (layout, signature, constraints, validation) and [TOKENS.md](TOKENS.md) (token role). One course identity cross every `lessons/*.html` and `reference/*.html` — set read as course, not pile one-offs. Voice: dropped-article style deliberate, load-bearing — preserve in edit.

Every component here is plain HTML + the shared stylesheet; nothing needs a new script. Offline-only, print-friendly — see [DESIGN.md § Constraints](DESIGN.md#constraints).

## Template arguments

[`templates/lesson.html`](../../../templates/lesson.html) is skeleton plus argument — no fixed lesson copy left in it. Two brace forms, one convention:

- `{{UPPER-KEBAB}}` — **named argument**, table below. Wording is the lesson's, never the template's; that is what stop lesson 12 reading as lesson 1 with different words.
- `{{lowercase prose}}` — fill-in guidance at point of use (a sidenote line, a synthesis point). Not named, not tabled.

Both gone from a finished lesson: `check_lesson.py` reject any surviving `{{` (`unfilled-placeholder`), except inside `<pre>`/`<code>`, where a lesson teaching a brace-syntax template language need them. What a lesson may vary beyond its copy — optional block choice and order, accent, density — and what it may not: [DESIGN.md § Variation](DESIGN.md#variation).

| Argument                                                               | Slot                                 | Fill with                                                                                                                             |
| ---------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| `LANG`                                                                 | `<html lang>`                        | BCP-47 tag of the language lesson written in                                                                                          |
| `ACCENT`                                                               | `<html data-accent>`                 | `cobalt` (default), `teal`, `violet`, `plum` — [TOKENS.md § Per-lesson hooks](TOKENS.md#per-lesson-hooks); drop attribute for default |
| `DENSITY`                                                              | `<html data-density>`                | `default`, `compact`, `roomy` — same reference; drop attribute for default                                                            |
| `TITLE`                                                                | `<title>`, `h1`                      | lesson title                                                                                                                          |
| `TOPIC`                                                                | `<title>`                            | course topic                                                                                                                          |
| `EYEBROW`                                                              | `.lesson-header .eyebrow`            | where lesson sit, e.g. `Lesson 4 · ownership`                                                                                         |
| `LEAD`                                                                 | `.lead`                              | one thing lesson land — output of reconciling sources, not restatement of first                                                       |
| `ROUTE-LABEL`                                                          | `.toc` `aria-label` + `.toc-eyebrow` | what the route is called; same string both slots                                                                                      |
| `STOP-1`…`STOP-4`                                                      | route stops, and `h2` of section 2–4 | [Lesson route](#lesson-route)                                                                                                         |
| `RECORD-ID`                                                            | `<!-- cold-open: … -->`              | `NNNN-slug` of record each item test — one pair per `.quiz-item`                                                                      |
| `COLD-OPEN-EYEBROW`, `COLD-OPEN-TITLE`, `COLD-OPEN-INTRO`              | `.cold-open`                         | [Cold open](#cold-open)                                                                                                               |
| `QUIZ-LABEL`                                                           | `.quiz` `data-label`                 | head of result line; free text, scoring key on the id that follow it                                                                  |
| `LESSON-ID`                                                            | `.quiz` `data-lesson`                | own file stem, `NNNN-slug`                                                                                                            |
| `QUESTION`, `OPT`, `FEEDBACK`                                          | `.quiz-item`                         | [Quiz](#quiz)                                                                                                                         |
| `COPY-LABEL`                                                           | `.quiz-copy`                         | copy-control label                                                                                                                    |
| `SEAL-NOTE`, `UNSEALED-LABEL`                                          | `.seal-note`                         | [DESIGN.md § Signature](DESIGN.md#signature--the-retrieval-gate)                                                                      |
| `SEAL-LABEL`                                                           | `.lesson-content` `data-seal-label`  | the veil's own line                                                                                                                   |
| `BODY`                                                                 | first `<p>` under Knowledge          | [SKILL.md](../SKILL.md) `## Knowledge` authoring rules                                                                                |
| `URL`                                                                  | sidenote and body links              | citation target                                                                                                                       |
| `KNOWLEDGE-BLOCKS`, `SKILLS-BLOCKS`                                    | after the Knowledge / Skills `h2`    | optional components this lesson earn, in the order it earn them                                                                       |
| `SYNTHESIS-TITLE`, `SYNTHESIS-PROMPT`                                  | `.synthesis`                         | [Synthesis](#synthesis)                                                                                                               |
| `WHERE-NEXT`, `FOLLOW-UP`                                              | Where next                           | [Where next](#where-next)                                                                                                             |
| `NAV-LABEL`, `PREV-LABEL`, `NEXT-LABEL`                                | `.lesson-nav`                        | navigation labels                                                                                                                     |
| `PREV-LESSON`, `PREV-LESSON-TITLE`, `NEXT-LESSON`, `NEXT-LESSON-TITLE` | `.lesson-nav`                        | neighbour file stem and title; no neighbour → drop that whole `.lesson-nav-cell`                                                      |

## Lesson route

`.toc`, four ordered stops. Each anchor own square number; route show lesson scope before cold open, never use it as dense global navigation. Four-stop route is load-bearing — `check_lesson.py` fail a lesson that carry any other count (`route-four-stops`). Anchors fixed with it: `#recall`, `#knowledge`, `#skills`, `#where-next`.

Stop **labels** are the lesson's, through `STOP-1`…`STOP-4`. One label per stop, used twice: route stop 2–4 and the `h2` of the section it point at. Two names for one stop — a route saying "Understand" over a heading saying "Knowledge" — is the vocabulary drift this replaces. Keep the same four labels across a course; they translate once, not per lesson. Synthesis close the lesson but is not a route stop.

Stop 1 point at the cold open. Lesson with nothing due carry none (see below) — then `id="recall"` ride on `.lesson-header` and `STOP-1` name what the lesson actually open with.

## Cold open

`.cold-open`, `--paper-2` calibration field, transit-blue top rule, fine frame. `COLD-OPEN-EYEBROW` and `COLD-OPEN-TITLE` label it, `COLD-OPEN-INTRO` is one plain sentence explaining answer-from-memory and the release condition. Hold quiz. Field span both column; what it hold stay bound to `--measure`, so cold-open quiz and practice quiz further down same lesson one component at one width, ✓ mark stay next to word it mark.

**No due record, no cold open** ([SKILL.md](../SKILL.md) step 5). Then drop the whole `.cold-open` section and the `.seal-note` with it, drop `sealed`, `inert` and `data-seal-label` off `.lesson-content`, and re-anchor stop 1 per [Lesson route](#lesson-route). Half-dropping it is the failure: a sealed body with no quiz to release it is a lesson nobody can open, and `check_lesson.py` catch that pairing, not the missing anchor — the anchor is caught by `broken-anchor`.

## Lead

`.lead` on opening paragraph. One thing lesson land, set above body size. At body size it read as first paragraph, not claim rest of page argue.

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

**Labels.** `quiz.js` hold an English default for every string it write, each overridable by a `data-*` on `.quiz`, so a non-English lesson translate without touching the widget. Template spell out only `data-label`, the one that vary per lesson — restating a default in markup is a second copy that drift.

| Attribute                | Fills                                   | Default in `quiz.js`                                              |
| ------------------------ | --------------------------------------- | ----------------------------------------------------------------- |
| `data-label`             | head of the result line (`QUIZ-LABEL`)  | `Cold open`                                                       |
| `data-undo-label`        | undo control; countdown append to it    | `Undo`                                                            |
| `data-copied-label`      | copy control, briefly, after a copy     | `Copied`                                                          |
| `data-copied-status`     | `.quiz-copy-status` after a copy        | `Result copied. Paste it into your next message to your teacher.` |
| `data-copy-failed-label` | `.quiz-copy-status` after a failed copy | `Copy failed. Result selected; copy it manually.`                 |

`teach.py score` key on the `NNNN-slug` at the end of the head, never on `data-label` words, so translating the label cannot break scoring.

**Feedback content (load-bearing).** Per-item feedback text must state _why_ the correct option is correct and _why_ the chosen wrong option is wrong, not merely confirm or reject. The high-information gain live in this text (Wisniewski 2020: d=0.99 high-information vs d=0.24 reinforcement-only); the scoring result line is KR-level (right/wrong counts) for scheduling, not for learning, so the per-item feedback carry all the specificity. Authoring rule, not a markup change — the `.quiz-fb` slot already exist.

**Undo window.** Answer not final instant clicked. Chosen option go to neutral `data-state="chosen"` mark, `.quiz-undo` appear, item lock three second later. Nothing about answer reveal inside that window — no right/wrong, no correct option, no feedback. Reveal-then-undo would hand back free retry with answer already on screen, and that one thing retrieval measurement can't survive. Once locked, no retry: window buy back tap, never recall. Reason it exist: this line reschedule memory record, so mis-tap noise recorded as signal.

Copy control show only on first pass through gated cold open — revisit unseal from remembered state, practice quiz never gate, so neither produce line worth pasting. Successful copy announce that learner paste result into next message to teacher. `data-lesson` bind line to own lesson.

**Serve mode vs paste fallback.** On `finish()`, `quiz.js` branch on `window.__TEACH_SERVE` (set by the serve-injected token script — see [SKILL.md](../SKILL.md) session flow): served lesson `POST /score` with `{lesson, line, token}` and no copy button shown; `file://` lesson (flag absent) run the copy-button paste path above, unchanged. Result-line shape identical both paths. Response handling per status: `2xx` unseal the body, render an in-page `.quiz-status` ("Scored. Schedule updated.") plus a `.quiz-schedule` block carry the returned `schedule` array, hide the copy button; `401` keep the body sealed, render `.quiz-reconnect` ("Session restarted — reload this lesson to reconnect") and reveal the `.quiz-copy` button as paste fallback; any other non-2xx (and network failure) keep the body sealed, render a `.quiz-error` block with a retry affordance, and persist the result line to `localStorage` under the seal key so a retry never lose it. The `.quiz-copy` button stay the fallback across every branch — serve mode hide it on success but keep it in markup so a `401` or non-2xx fall back to paste. No static-HTML change: `.quiz-status`, `.quiz-schedule`, `.quiz-reconnect`, `.quiz-error` are JS-created, so the markup contract in the code block above is unchanged and `check_lesson.py` still pass on `templates/lesson.html`.

**Confidence rating (optional, opt-in).** A cold-open quiz may carry `data-confidence="1"` to capture a 1–5 "how sure" rating per item _before_ the answer reveal — a scheduling signal for hypercorrection-aware re-teach (high-confidence-wrong correct more readily; Metcalfe 2017), never a comprehension booster (bare JOL prompts do not help and harm ~1/3 of learners — Ariel 2021, Zhao 2024). When set, `quiz.js` render a small 1–5 selector per item; chosen rating ride into the result token as `pos outcome/N` (e.g. `1 right/4`). No `data-confidence` = unchanged behaviour and unchanged result line. The rating is a scheduling signal only; `teach.py` store it in the record's `confidence` frontmatter and step 4 of [SKILL.md](../SKILL.md) prefer high-confidence-wrong re-teach candidates. Never prompt a bare "how well did you understand this?" — capture confidence, do not ask the learner to judge comprehension.

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

`data-type`: `note` (by-the-way), `tip` (optional better way), `warning` (common pitfall), `caution` (irreversible / data-loss). Left rule reuses `--accent`/`--signal`/`--wrong` by type; sans label, kept short. Cap one or two per lesson, never stacked, placed beside the content it qualify — visually distinct from citation sidenote (full-width block, not margin). Each callout carry a type-specific `<svg class="icon">` as the first child — `information-circle` (note), `light-bulb` (tip), `exclamation-triangle` (warning), `lock-closed` (caution) — decorative (`aria-hidden="true"`); adjacent text label and stripe color carry the meaning. Path data copy from heroicons/24/outline.

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

Authoring discipline for lesson body, stated once so generated lesson stay consistent:

- **bold** only for a new term at its point of definition, or a run-in label — never a whole sentence, never combined with another emphasis
- _italic_ for subtle emphasis and words-as-words, used sparingly (dyslexia risk)
- `code` only for actual code identifiers, filenames, console output
- headings carry scan weight, not inline bold — do not bold to "make important"

LLM over-bold by default, so the rule is load-bearing for an AI author. The `.lead` is italic by stylesheet, not by author hand.

## Citations

Inline `a.cite` number real link to own `.sidenote` (`id="n1"`, `n2`, … in order); note itself sans, small, `--ink-soft`, hairline left rule, and a `<p>` rather than `<aside>` — aside here scoped to no sectioning element, so each note would land as own `complementary` landmark, finished lesson would bury `<main>` under dozen of them. `a.cite` take inline padding with cancelling negative margin: vertical padding on inline box don't touch line box, so tap target grow from 8px to something findable without pixel of reflow. Matter on phone, one place note moved away from claim it belong to. Beside paragraph, pairing obvious; on phone and paper note moved below claim, matching numeral only thing tying claim to source. `sup.cite` stay styled for lesson generated before link existed.

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
