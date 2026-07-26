# Workspace Formats

Four root docs capture workspace stable content state — created lazy, each when first need. Together answer: why learn this ([Mission](#mission)), where knowledge come from ([Resources](#resources)), what words mean ([Glossary](#glossary)), how user want sessions run ([Notes](#notes)). Every teaching decision trace back to these.

| File           | Holds                                                  | Spec                    |
| -------------- | ------------------------------------------------------ | ----------------------- |
| `MISSION.md`   | Why user learns this. Grounds every teaching decision. | [Mission](#mission)     |
| `RESOURCES.md` | Trusted sources for knowledge, communities for wisdom. | [Resources](#resources) |
| `GLOSSARY.md`  | Canonical language of topic.                           | [Glossary](#glossary)   |
| `NOTES.md`     | User preferences and your working notes.               | [Notes](#notes)         |

All four live at workspace root. Create each when session flow in [SKILL.md](../SKILL.md) first need it — never speculative. [Learning record](RECORDS.md) format separate; tracks what learned, not what workspace knows.

---

## Mission

`MISSION.md` captures _reason_ user learns topic — concrete real-world goal chased. Every teaching decision — what teach next, which resources surface, which exercises design — trace back to this doc. Without it, lessons feel abstract.

### Template

```md
# Mission: {Topic}

## Why

{1-3 sentences. The concrete real-world goal the user is chasing. What changes in their life or work when they have this skill? Avoid abstract framings like "to understand X" — push for the underlying outcome.}

## Success looks like

- {A specific, observable thing the user will be able to do}
- {Another specific thing}
- {…}

## Constraints

- {Time, budget, prior commitments, learning preferences, anything that bounds the approach}

## Out of scope

- {Adjacent topics the user explicitly does not want to chase right now — protects the zone of proximal development}
```

### Rules

- **One mission per workspace.** User want learn two unrelated things = two workspaces.
- **Concrete over abstract.** "Run a half marathon by October" beat "get fitter." "Ship a Rust CLI to my team" beat "learn Rust."
- **Push back on vagueness.** User cannot say why? Interview first, write nothing. Bad mission worse than no mission.
- **Revise when reality shifts.** Missions change. Goal move = update file. No stale mission steer future sessions. Mission shift from learning = also write [learning record](RECORDS.md) capturing shift, cross-linked here.
- **Keep it short.** `MISSION.md` past one screen = not compass anymore, now plan.
- **Mark provisional missions.** User decline interview: write narrowest mission their words support, put `**Provisional**` on own line directly under `# Mission:` heading, reopen next session. Provisional mission reopens once, then proceeds — second session with `**Provisional**` still on it, treat settled, teach. Provisional mission steers teaching, never settles it.

---

## Resources

`RESOURCES.md` curated set of trusted sources for topic. Lesson knowledge come from here, never parametric guess. Wisdom come from communities listed here. See [SKILL.md](../SKILL.md) step 3 — thin resources means find sources before teach anything.

### Template

```md
# {Topic} Resources

## Knowledge

- [Book: _The Science and Practice of Strength Training_ — Zatsiorsky & Kraemer](https://example.com)
  Foundational text on programming and adaptation. Use for: anything to do with periodisation, recovery, intensity zones.
- [Article: "How Much Should I Train?" — Greg Nuckols (Stronger By Science)](https://example.com)
  Evidence-based review of volume landmarks. Use for: weekly set targets per muscle group.

## Wisdom (Communities)

- [r/weightroom](https://reddit.com/r/weightroom)
  High-signal subreddit, moderated against bro-science. Use for: programme critique, plateau troubleshooting.
- Local: Tuesday strength class at {gym name}
  Use for: real-time coaching feedback on lifts.
```

### Rules

- **High-trust only.** Prefer primary sources, recognised experts, peer-reviewed work, communities strong moderation. Resource marketing dressed as education: leave out.
- **Annotate every entry.** Bare link useless in three months. Add one line: what covers, when reach for it.
- **Group by Knowledge / Wisdom.** Mirrors philosophy in [SKILL.md](../SKILL.md) — knowledge captured, wisdom borrowed from practitioners. Fine for resource appear in one group only.
- **Surface gaps explicitly.** No good resource for area mission needs: write `## Gaps` section listing what missing. Drives future search.
- **Prune ruthlessly.** Resource wrong, shallow, or off-mission: remove, not bury. Better five sharp sources than thirty mediocre.
- **Record community preferences.** User opt out joining communities: note here so future sessions stop proposing them.

---

## Glossary

`GLOSSARY.md` canonical language for this teaching workspace. All lessons, exercises, learning records follow its terms. Building it _is_ learning: compress concept into tight definition prove user understands it.

Term enter glossary only after user demonstrates understanding — see [SKILL.md](../SKILL.md) step 8, where evidence exists. Once term in, use it every lesson. Promotion before evidence = dictionary user reads to learn, not record of what they know.

### Template

```md
# {Topic} Glossary

{One or two sentence description of the topic this glossary covers.}

## Terms

**Hypertrophy**:
Muscle growth driven by mechanical tension and metabolic stress over repeated training sessions.
_Avoid_: Bulking, getting big

**Progressive overload**:
Systematically increasing the demand on a muscle over time — via load, volume, or intensity.
_Avoid_: Pushing harder, levelling up

**RPE (Rate of Perceived Exertion)**:
A 1–10 self-rating of how hard a set felt, where 10 is failure and 8 means two reps left in the tank.
_Avoid_: Effort score, intensity rating
```

### Rules

- **Add a term only when the user understands it.** Glossary records compressed knowledge, not dictionary user reads to learn. User just met concept: wait til they use it correctly before promoting here.
- **Be opinionated.** Many words for same concept: pick best, list rest as aliases to avoid. That how language compresses.
- **Keep definitions tight.** One or two sentences. Define what term _is_, not what it does or how to do it.
- **Use the glossary's own terms inside definitions.** Term in glossary: prefer it everywhere, including inside other definitions. Makes complex terms easier later.
- **Group under subheadings** when natural clusters emerge (e.g. `## Anatomy`, `## Programming`). Flat list fine when terms cohere.
- **Flag ambiguities explicitly.** Term used loosely in wider field: note resolution: "In this workspace, 'set' always means a working set — warm-ups are tracked separately."
- **Revise as understanding deepens.** Definition from week one may be wrong by week six. Update in place; no stale entries.

---

## Notes

`NOTES.md` hold two things that steer sessions but belong in no other doc: what user prefer, and what you must remember across a session boundary. Two headings, nothing else.

### Template

```md
# Notes

## Preferences

- Evenings only, 20 minutes tops.
- No community suggestions — already declined (also noted in `RESOURCES.md`).
- spacing: { doubling: 2, ceiling: 90 }

## Working notes

- unscored cold open: lessons/0007-x.html tests 0003-a, 0005-b (asked: 0)
- Kept confusing tempo with cadence in session 4; watch for it.
```

### Rules

- **Preference goes under `## Preferences`, never buried in prose.** Preference buried in prose is preference you miss. Read every session, obeyed.
- **One structured value, exact shape.** `spacing: { doubling: N, ceiling: N }` override cold-open schedule — `doubling` default 2, `ceiling` default 90. Step 8 of [SKILL.md](../SKILL.md) read it as value, not as prose; any other shape not parse. Everything else under `## Preferences` is free text.
- **Working notes are scratch that must outlive the session.** Cold-open ledger line live here — see [SKILL.md](../SKILL.md) § Cold-open ledger. Anything that die with the session belong in the session, not in the file.
- **Prune.** Preference user reverse: delete it, do not annotate it. Working note whose session is done: delete it.
- **Never a journal.** Session-by-session activity log belong nowhere in this workspace — not here, not in [learning records](RECORDS.md).
