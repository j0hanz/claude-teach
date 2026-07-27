# claude-teach

## Conventions

This repo is the plugin, never a teaching workspace — never create `MISSION.md`, `lessons/` or `learning-records/` here.

Prose in `skills/` and `templates/` uses a deliberate dropped-article voice. Preserve it; do not normalize to standard English.

Python here is stdlib-only. `hooks/teach_hook.py` and `skills/teach/scripts/*.py` run under whatever `python` is on the user's PATH — add no runtime dependency, and keep syntax parseable by the `target-version` floor in `pyproject.toml`.

`${CLAUDE_PLUGIN_ROOT}` in skill and hook content is substituted at runtime. Leave it; do not resolve it to a relative path.

`templates/` is the single source for lesson CSS, JS and HTML. The design system is split across `skills/teach/references/`: `TOKENS.md` names token roles (never their values), `COMPONENTS.md` specs every reusable block a generated lesson emit, `DESIGN.md` holds layout, the retrieval-gate signature, constraints and validation.

## Commands

`python skills/teach/scripts/check_lesson.py --self` — validates `templates/lesson.html` against the validator contract. Run after editing `templates/` or the validator. It is the only automated check here; there is no test suite.

## Serve mode

`teach.py serve` (stdlib `http.server`, `127.0.0.1` only, no new runtime dep) is an optional loopback server. A served lesson POSTs its cold-open result back itself; the `file://` copy-button paste flow is the fallback. Session hook starts/stops it; absent server regresses nothing.

## More

Lesson design system and rationale: `skills/teach/references/DESIGN.md`, `COMPONENTS.md`, `TOKENS.md`
Session flow and workspace layout: `skills/teach/SKILL.md`
