# Lesson HTML Design — Components

Spec for every reusable block a generated lesson emit. Companion to [DESIGN.md](DESIGN.md) (layout, signature, constraints, validation) and [TOKENS.md](TOKENS.md) (token role). One course identity cross every `lessons/*.html` and `reference/*.html` — set read as course, not pile one-offs. Voice: dropped-article style deliberate, load-bearing — preserve in edit.

Every component here is plain HTML + the shared stylesheet; nothing needs a new script. Offline-only, print-friendly — see [DESIGN.md § Constraints](DESIGN.md#constraints).

## Lesson route

`.toc`, four ordered stops: Recall, Understand, Practice, Continue. Each anchor own square number; route show lesson scope before cold open, never use it as dense global navigation. Each stop link carry a trailing `chevron-right` `<svg class="icon">` (decorative, `aria-hidden="true"`) — the stop circle and number carry the meaning, chevron reinforces "next stop in this direction." Four-stop route is load-bearing — do not add a fifth stop. Synthesis (below) close the lesson but is not a route stop.

## Cold open

`.cold-open`, `--paper-2` calibration field, transit-blue top rule, fine frame. Label it `Recall check`; one plain sentence explain answer-from-memory and release condition. Hold quiz. Field span both column; what it hold stay bound to `--measure`, so cold-open quiz and practice quiz further down same lesson one component at one width, ✓ mark stay next to word it mark.

## Lead

`.lead` on opening paragraph. One thing lesson land, set above body size. At body size it read as first paragraph, not claim rest of page argue.

## Quiz

Shape only:

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
  <summary>In your own words: why does … hold?</summary>
  <div class="self-explain-model">…model answer…</div>
</details>
```

Distinct from cold open: cold open test prior record; self-explanation elaborate the current lesson. Keep one per non-trivial worked step or concept; not a new widget, just `<details>` with the shared style. Summary carry a closed/open icon pair as the first child — `arrow-uturn-left` (closed) and `arrow-uturn-right` (open) — decorative, both rendered, CSS toggle one off on `[open]`; `<summary>` text adjacent already names what unlocks. Lesson language switch carries the icon shape, not a CSS `+`/`−` glyph.

## Details — optional depth

Native `<details>`/`<summary>` for genuinely optional deeper content (a worked derivation, an edge case, a longer aside) inside the body. Offline, prints sensibly, no JS. Cap one nesting level. Label `summary` with real information scent ("How we chose this threshold"), never hide a prerequisite. Self-explanation (above) is its primary use; a plain `<details class="aside">` serve other optional depth. Same closed/open icon pair as self-explanation — see above.

## Synthesis

`<section class="synthesis">` between Skills and Where next — the consolidation slot. Student-led synthesis in the final stretch protect retention (Villarreal 2025; ICAP constructive above passive); re-stating the rule after practice consolidate the schema (LearnLab example-rule coordination). Not a route stop — the four-stop route stay four.

```html
<section class="synthesis" id="synthesis">
  <h2><svg class="icon" viewBox="0 0 24 24" aria-hidden="true">…sparkles…</svg>Synthesis</h2>
  <ul class="synthesis-points">
    <li>…core idea, one line…</li>
    …3–5…
  </ul>
  <p class="synthesis-rule">…re-state the core rule in light of what practice showed…</p>
  <p class="synthesis-prompt">Say it back in your own words — then ask your tutor to check it.</p>
</section>
```

The prompt is a retrieval nudge that feed the spaced-repetition loop. Keep "Where next" navigation-only; synthesis carry consolidation.

## Callout

`.callout`, a typed aside for a common pitfall, a by-the-way, an optional better way, or an irreversible action. No sanctioned home for these existed, so warning got buried as prose or bold got abused.

```html
<div class="callout" data-type="warning" role="note">
  <p>…</p>
</div>
```

`data-type`: `note` (by-the-way), `tip` (optional better way), `warning` (common pitfall), `caution` (irreversible / data-loss). Left rule reuses `--accent`/`--signal`/`--wrong` by type; sans label, kept short. Cap one or two per lesson, never stacked, placed beside the content it qualify — visually distinct from citation sidenote (full-width block, not margin). Each callout carry a type-specific `<svg class="icon">` as the first child — `information-circle` (note), `light-bulb` (tip), `exclamation-triangle` (warning), `lock-closed` (caution) — decorative (`aria-hidden="true"`); adjacent text label and stripe color carry the meaning. Path data copy from heroicons/24/outline.

## Figure — diagram

Optional `<figure class="diagram">` for inline SVG or a local `assets/` image. Words + images beat words alone — the most robust CTML finding (Mayer 2024, 200+ experiments) — and inline SVG fit `file://` with no dependency. Gate on record state like the worked-example rule: graphic help low-knowledge learner but **hamper** high-knowledge (Vogt 2020, expertise reversal), so do not add a diagram to a lesson a competent learner see.

```html
<figure class="diagram">
  <img src="assets/…png" alt="…" />
  <figcaption>
    …caption; cite the claim it illustrate via <a class="cite" href="#n1">1</a>…
  </figcaption>
</figure>
```

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

Final block: one primary source (highest-trust thing found), cross-link to related lesson and reference doc by anchor, line invite follow-up question. Navigation only — consolidation live in [Synthesis](#synthesis).

## Icon — shell set

Inline heroicons (`@heroicons/react@2.2.0/24/outline`, MIT, source `tailwindlabs/heroicons`). One `<svg class="icon">` per anchor, `aria-hidden="true"`, path data copied verbatim from `heroicons/optimized/24/outline/<name>.svg`. Color via `stroke="currentColor"` — callout and route hooks set `color` token-specific. The selection is the only sanctioned shell set; a lesson reach for a different icon only at `<figure class="diagram">` (which gate on record state per [Figure](#figure--diagram)) with the same inline approach.

| Icon                   | Where                                     | Why                                        |
| ---------------------- | ----------------------------------------- | ------------------------------------------ |
| `academic-cap`         | `.lesson-header > .eyebrow`               | "Lesson" affordance — study instrument     |
| `chevron-right`        | each `.toc a`                             | forward direction on the route             |
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
