# AGENTS.md

## Commands

`python skills/teach/scripts/check_lesson.py --self` — validates `templates/lesson.html` against the validator contract. Run after editing `templates/` or the validator.

`python skills/teach/scripts/test_teach.py` — the scoring table and the Stop gate's state machine, plain asserts. Run after editing `teach.py` or `hooks/teach_hook.py`.

`ruff check .` — no CI runs any of these, so run them yourself. These three are every check the repo has.

## Conventions

This repo is the plugin, never a teaching workspace — never create `MISSION.md`, `lessons/` or `learning-records/` here.

Prose in `skills/` and `templates/` uses a deliberate dropped-article voice. Preserve it; do not normalize to standard English.

Python here is stdlib-only. `hooks/teach_hook.py` and `skills/teach/scripts/*.py` run under whatever `python` is on the user's PATH — add no runtime dependency, and keep syntax inside the `target-version` floor in `pyproject.toml`.

`${CLAUDE_PLUGIN_ROOT}` in skill and hook content is substituted at runtime. Leave it; never resolve it to a relative path.

`templates/` is the single source for lesson HTML, CSS and JS, and `lesson.html` carries no lesson copy — every word arrives as a `{{ARGUMENT}}`. Its whole contract — design, tokens, components — is `skills/teach/references/DESIGN.md`, one file so a change that touches all three parts is one edit.

## More

Session flow, workspace layout, hooks: `skills/teach/SKILL.md`
