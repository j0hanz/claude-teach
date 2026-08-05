# Lesson HTML Design — Tokens

Token role and rationale for lesson CSS. Companion to [DESIGN.md](DESIGN.md); [COMPONENTS.md](COMPONENTS.md) spec every block this skill emit. Value live in [`templates/assets/roots.css`](../../../templates/assets/roots.css) `:root` — single source. Edit there; never restate value here or anywhere.

Name and role only — no value here, on purpose. Value drift when restated.

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

Two attribute on `<html>`, both optional, both a **name from a closed set** — never a value. Value live in `roots.css` beside the token they move, so one edit there move every lesson that pick that name. Rationale and the identity limit: [DESIGN.md § Variation](DESIGN.md#variation).

| Attribute      | Values                                       | Moves                                                                                 |
| -------------- | -------------------------------------------- | ------------------------------------------------------------------------------------- |
| `data-accent`  | `cobalt` (default), `teal`, `violet`, `plum` | `--accent-h`, and so `--accent` (and `--accent-bg` in dark, where the tint carry hue) |
| `data-density` | `compact`, `roomy`                           | `--s-5`, `--s-6`, `--s-7` — section rhythm                                            |

Attribute absent read as the default; a lesson that want the default drop the attribute rather than spell it. Density has no `default` name for that reason — the base `:root` is it, and a name would restate values that already live there.

`check_lesson.py` read the allowed name straight out of the linked CSS and fail a lesson that use any other (`unknown-accent`, `unknown-density`) — a misspelt name would otherwise render the default and look correct. Add a name to `roots.css` and it is allowed; this table is documentation, never the source, and the one table — template and [COMPONENTS.md](COMPONENTS.md#template-arguments) point here rather than restate the names, so a fifth copy cannot drift.

`<html>` carry a third kind of hook that is no token: the `data-*` overrides for words `quiz.js` write, which the `QUIZ-STRINGS` slot above the tag exist to remind ([COMPONENTS.md § Quiz](COMPONENTS.md#quiz)). Same element, different layer — string, not value.

`--signal` take no hook: vermilion mark route stop and release edge in every lesson, and that is course identity, not lesson choice.

Token value live in [`templates/assets/roots.css`](../../../templates/assets/roots.css) `:root` — single source. Edit there; never restate value here.
