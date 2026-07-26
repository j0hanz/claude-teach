# claude-teach

## Conventions

This repo is the plugin, never a teaching workspace — never create `MISSION.md`, `lessons/` or `learning-records/` here.

Prose in `skills/` and `templates/` uses a deliberate dropped-article voice. Preserve it; do not normalize to standard English.

Python here is stdlib-only. `hooks/teach_hook.py` and `skills/teach/scripts/*.py` run under whatever `python` is on the user's PATH — add no runtime dependency, and keep syntax parseable by the `target-version` floor in `pyproject.toml`.

`${CLAUDE_PLUGIN_ROOT}` in skill and hook content is substituted at runtime. Leave it; do not resolve it to a relative path.

`templates/` is the single source for lesson CSS, JS and HTML. `skills/teach/DESIGN.md` names token roles, never their values.

## Commands

`python skills/teach/scripts/check_lesson.py --self` — validates `templates/lesson.html` against the validator contract. Run after editing `templates/` or the validator. It is the only automated check here; there is no test suite.

## More

Lesson design system and rationale: `skills/teach/DESIGN.md`
Session flow and workspace layout: `skills/teach/SKILL.md`
