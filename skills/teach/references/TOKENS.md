# Lesson HTML Design — Tokens

Token role and rationale for lesson CSS. Companion to [DESIGN.md](DESIGN.md); [COMPONENTS.md](COMPONENTS.md) spec every block this skill emit. Value live in [`templates/assets/roots.css`](../../../templates/assets/roots.css) `:root` — single source. Edit there; never restate value here or anywhere.

Name and role only — no value here, on purpose. Value drift when restated.

| Token        | Role                                 |
| ------------ | ------------------------------------ |
| `--paper`    | cool blue-gray page surface          |
| `--paper-2`  | pale field, cold-open field, code    |
| `--paper-3`  | deeper field, route bar              |
| `--ink`      | graphite body text                   |
| `--ink-soft` | secondary text, marginalia           |
| `--rule`     | hairlines                            |
| `--rule-2`   | control boundaries (quiz options)    |
| `--accent`   | cobalt — gate, correct, links        |
| `--accent-2` | deep cobalt — hover, secondary marks |
| `--signal`   | vermilion — route stop, release edge |
| `--wrong`    | wrong (muted brick, never alarm-red) |
| `--success`  | correct (muted green)                |
| `--serif`    | body face (sustained reading)        |
| `--sans`     | labels and marginalia face           |
| `--mono`     | code and result-line face            |
| `--s-1`…`7`  | space ladder — margins and padding   |
| `--measure`  | body line length                     |
| `--margin-w` | sidenote column width                |
| `--radius`   | corner radius, controls and code     |
| `--tap`      | minimum touch target (44px)          |

Why these token, not others:

- **System-only type stacks.** Web font banned on `file://` — no CDN, no remote `@import`, cable unplugged, page still render. Serif stack ship on Windows + macOS, degrade clean; sans and mono ride OS default. No web font worth network dependency brief forbid.
- **`--measure` bound line length** for sustained reading. Width typographic decision, not layout accident — body column past ~36rem stop being read, start being scanned.
- **`--margin-w` earn its width** because every claim cite. Citation live beside claim as sidenote, not bunch as inline footnote bomb. Margin structural, not decorative.
- **`--wrong` muted oxblood, never alarm-red.** Wrong answer teaching signal, not emergency. Red shout; oxblood correct quiet, keep page calm.
- **One space ladder, not free value.** Structural gap come off `--s-*`; rare quarter-rem optical adjustment stay beside component it tune. Type size live at use — page has few roles, named ladder hide more than it help.
- **`--rule-2` exist because `--rule` too faint to be edge.** Hairline separate; control boundary must be _found_. Quiz option border only thing saying "this is clickable", `--rule` sit near 1.5:1 on paper — under 3:1 control boundary owe. Two token, two job; never use `--rule` on interactive edge.

Token value live in [`templates/assets/roots.css`](../../../templates/assets/roots.css) `:root` — single source. Edit there; never restate value here.
