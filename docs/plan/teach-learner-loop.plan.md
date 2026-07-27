# Plan — teach learner-loop UX

Status: APPROVED
Depth: contract
Origin: plan

Source design: [docs/design/2026-07-27-teach-learner-loop-design.md](../design/2026-07-27-teach-learner-loop-design.md)
Specs: [teach-learner-loop.specs.md](teach-learner-loop.specs.md)

<!-- Validation: 3-chunk critic fan-out → REVISE (8 Meds: TASK-003 atomicity + only-writer
wording, missing TASK-003 transitive dep on TASK-004/005/010, TASK-006 .quiz-error, two weak
grep Validates). Fixes: REQ-010 reframed (scoring core = single writer, server calls it);
TASK-003 Action states atomicity + absent-token 401; TASK-004 Depends on TASK-002, TASK-003;
TASK-006 adds .quiz-error; TASK-009/010/011 Validates anchored on distinctive strings + grep -cE.
Re-validation round (1 critic per lens): all 12 findings resolved, no new Highs → APPROVED.
Lows noted: TASK-011→TASK-009 over-serialization kept as drift guard. -->

Tasks are haiku-sized (one behavior, ≤3 files). Validate commands use a throwaway workspace
under `C:\tmp` because the repo is never a teaching workspace (AGENTS.md).

### TASK-001: Refactor scoring core out of cmd_score

Depends on: none
Files: [skills/teach/scripts/teach.py](../../skills/teach/scripts/teach.py)
Symbols: [cmd_score](../../skills/teach/scripts/teach.py#L1032), score_open_cold_open
Satisfies: REQ-003, REQ-010
Action: Extract the ledger-parse + `parse_result_line` + `score_record` + `delete_ledger_line` + `save_record` + `build_index` body of `cmd_score` into a reusable `score_open_cold_open(cwd, result_line)` returning structured per-record results. `cmd_score` calls it and prints the existing lines unchanged. No behavioral change.
Validate: `python skills/teach/scripts/teach.py score --help` exits 0; in a temp workspace under `C:\tmp\teach-verify` (MISSION.md + one learning-record + an open ledger line) run `python skills/teach/scripts/teach.py score "Cold open 0001-x: 1 right"` and confirm output matches the pre-refactor format.
Expected result: `score` output byte-identical to before the refactor; exit 0.

### TASK-002: Add teach.py serve subcommand (skeleton + GET /lessons/)

Depends on: none
Files: [skills/teach/scripts/teach.py](../../skills/teach/scripts/teach.py)
Symbols: cmd_serve, ServeHandler
Satisfies: REQ-001, REQ-002, REQ-014
Action: Add `cmd_serve` and a `http.server.BaseHTTPRequestHandler` subclass. Bind `127.0.0.1` on an OS-assigned ephemeral port (`--port 0`). Generate `secrets.token_urlsafe(32)`. Write `${CLAUDE_PLUGIN_DATA}/serve.json` = `{pid, port, token, workspace}`. Print `serve: http://127.0.0.1:PORT`. `GET /lessons/<rel-path>` serves the workspace file (refuse path-escape) with the token script injected before `</body>`; send NO `Access-Control-Allow-Origin` header.
Validate: in a temp workspace `C:\tmp\teach-verify` with one lesson, start `python skills/teach/scripts/teach.py serve --workspace C:\tmp\teach-verify` in the background; `curl -s http://127.0.0.1:PORT/lessons/0001-x.html | grep __TEACH_TOKEN` hits; `curl -s -H "Origin: https://evil.example" -I http://127.0.0.1:PORT/lessons/0001-x.html` shows no `Access-Control-Allow-Origin`; then kill the server.
Expected result: served HTML contains `__TEACH_TOKEN`; no ACAO header on cross-origin GET.

### TASK-003: POST /score handler with idempotency + schedule response

Depends on: TASK-001, TASK-002
Files: [skills/teach/scripts/teach.py](../../skills/teach/scripts/teach.py)
Symbols: ServeHandler, score_open_cold_open
Satisfies: REQ-003, REQ-004, REQ-005, REQ-010
Action: Add a `POST /score` handler on `ServeHandler`. Parse JSON `{lesson, line, token}`. `401` if token is absent or != `serve.json` token. Normalize `lesson` against the workspace; `409` if no open ledger or `ledger["lesson"]` mismatches. Call `score_open_cold_open`; the handler never writes schedule/index fields directly — `score_open_cold_open` is the writer, atomic via the existing `write_text` (tmp + `os.replace`). Remember the last `(lesson, line)` scored in `serve.json` for idempotency. Respond `200 {scored: true, schedule: [{id, interval, next, lapses}, ...]}`. On a re-POST with a closed ledger whose `line` == last scored → `200 {scored: true, already: true, schedule: ...}`; closed ledger + different line → `409 {error: "ledger closed, different line"}`.
Validate: temp workspace with an open ledger; `curl -X POST http://127.0.0.1:PORT/score -d '{"lesson":"lessons/0001-x.html","line":"Cold open 0001-x: 1 right","token":"<T>"}'` → `200` + `schedule`; re-POST same line → `200` with `already:true`; POST with wrong token → `401`.
Expected result: status codes and `schedule` JSON match REQ-003/004/005.

### TASK-004: quiz.js serve-mode POST + file:// paste branching

Depends on: TASK-002, TASK-003
Files: [templates/assets/quiz.js](../../templates/assets/quiz.js)
Symbols: finish, initQuiz
Satisfies: REQ-006
Action: In `finish()`, if `window.__TEACH_SERVE && window.__TEACH_TOKEN`, build `{lesson: data-lesson, line, token}` and `fetch('/score', {method:'POST', ...})`; otherwise run the existing copy-button paste path unchanged. Result-line shape unchanged. Bump the `teach-template-version` stamp.
Validate: `python skills/teach/scripts/check_lesson.py --self` exits 0; open a served lesson in a browser, answer the cold open, confirm a `POST /score` lands (server writes schedule); open the same lesson from `file://`, confirm the copy button works and no POST fires.
Expected result: served → POST scores; file:// → copy button, no POST.

### TASK-005: quiz.js response handling + 401 reload + non-2xx fallback

Depends on: TASK-004
Files: [templates/assets/quiz.js](../../templates/assets/quiz.js)
Symbols: finish, unseal
Satisfies: REQ-007
Action: On `2xx` from `/score`: unseal the body, show "Scored. Schedule updated.", render the `schedule` snippet. On `401`: keep/show a "Session restarted — reload this lesson to reconnect" message and reveal the copy button (paste fallback). On any other non-2xx: keep the body sealed, show an in-page error, persist the result line to `localStorage` under the seal key, offer a retry button. Never discard the line on non-2xx.
Validate: served lesson, POST `2xx` → body unseals + schedule shown; stop the server mid-quiz, finish → body stays sealed + error shown + line in `localStorage`; restart server with a new token → POST `401` → reload hint + copy button visible.
Expected result: unseal/seal and fallback behavior match REQ-007 per status code.

### TASK-006: styles for status / schedule / reconnect elements

Depends on: TASK-005
Files: [templates/assets/styles.css](../../templates/assets/styles.css)
Symbols: .quiz-status, .quiz-schedule, .quiz-reconnect, .quiz-error
Satisfies: REQ-007
Action: Add `.quiz-status`, `.quiz-schedule`, `.quiz-reconnect`, `.quiz-error` rules using existing token roles from `skills/teach/references/TOKENS.md` (no new tokens); `.quiz-error` covers the in-page error + retry affordance REQ-007 requires on non-2xx, tinted with the existing `--wrong`/`--signal` role. Keep the set reading as one course. Bump the `teach-template-version` stamp in `styles.css`.
Validate: `python skills/teach/scripts/check_lesson.py --self` exits 0; a served lesson that scores renders the status + schedule block in course styles, not unstyled.
Expected result: validator passes; new elements styled with existing tokens.

### TASK-007: SessionStart starts/reuses server; SessionEnd stops it

Depends on: TASK-002
Files: [hooks/teach_hook.py](../../hooks/teach_hook.py), [hooks/hooks.json](../../hooks/hooks.json)
Symbols: event_session_start, event_session_end, _guard_path
Satisfies: REQ-008, REQ-009
Action: In `event_session_start`, after the existing status lines, read `serve.json`; if PID alive reuse, if stale kill+restart, if absent spawn `teach.py serve --workspace <cwd>` detached; print the serve URL. Add `event_session_end` that kills the PID in `serve.json` and clears the stale lockfile. Add a `SessionEnd` entry to `hooks/hooks.json` invoking the hook with `--event session-end`.
Validate: in a temp workspace, pipe a session-start payload to `python hooks/teach_hook.py --event session-start` and assert `serve.json` is written and `http://127.0.0.1:PORT` is reachable; pipe a session-end payload and assert the PID is no longer alive.
Expected result: server starts on session-start, stops on session-end.

### TASK-008: serve-path self-check

Depends on: TASK-003
Files: [skills/teach/scripts/teach.py](../../skills/teach/scripts/teach.py)
Symbols: cmd_serve
Satisfies: REQ-011
Action: Add `teach.py serve --check` (no socket bind) that asserts: a missing/wrong token is rejected, the ledger-bind accepts a matching lesson and refuses a mismatch, an idempotent duplicate returns `already:true`, and the same-origin-no-CORS invariant holds (handler sends no ACAO). Exits 0 on pass, 1 on failure, printing the failing assertion.
Validate: `python skills/teach/scripts/teach.py serve --check` exits 0.
Expected result: self-check passes; exit 0.

### TASK-009: SKILL.md session flow + Hooks section update

Depends on: TASK-007
Files: [skills/teach/SKILL.md](../../skills/teach/SKILL.md)
Symbols: Session flow step 6, Hooks
Satisfies: REQ-012, REQ-013
Action: In session flow step 6, state that when the serve URL is available the lesson is opened at `http://127.0.0.1:PORT/lessons/NNNN-slug.html`; if the server is absent, fall back to the existing `file://` open + paste. In the Hooks section, document SessionEnd and the server lifecycle. State explicitly that the paste flow remains the fallback and `file://` lessons are unchanged.
Validate: `python skills/teach/scripts/check_lesson.py --self` exits 0; `grep -c "127.0.0.1" skills/teach/SKILL.md` ≥ 1 and `grep -c "SessionEnd" skills/teach/SKILL.md` ≥ 1.
Expected result: docs describe served open + paste fallback + SessionEnd.

### TASK-010: COMPONENTS.md Quiz section update

Depends on: TASK-005
Files: [skills/teach/references/COMPONENTS.md](../../skills/teach/references/COMPONENTS.md)
Symbols: Quiz, Cold open
Satisfies: REQ-012
Action: Document in the Quiz section: the serve-mode `POST /score` on `finish()`, the `file://` copy-button paste branching, the in-page status + schedule elements, the `401` reload + paste fallback, and that the `.quiz-copy` button is retained as the fallback. Note there is no static-HTML change — the new elements are JS-created.
Validate: `grep -cE "POST /score|__TEACH_SERVE|paste fallback" skills/teach/references/COMPONENTS.md` ≥ 1; `python skills/teach/scripts/check_lesson.py --self` exits 0.
Expected result: component spec documents both paths and the fallback.

### TASK-011: README + AGENTS note optional serve mode

Depends on: TASK-009
Files: [README.md](../../README.md), [AGENTS.md](../../AGENTS.md)
Symbols: Install, Day one
Satisfies: REQ-012
Action: Add a short note to README and AGENTS.md: an optional local `teach.py serve` mode closes the cold-open loop in the browser; the copy-button paste flow remains the fallback; no new runtime dependency is introduced.
Validate: `grep -c "teach.py serve" README.md` ≥ 1 and `grep -c "teach.py serve" AGENTS.md` ≥ 1.
Expected result: both docs mention the optional serve mode.
