# Specs — teach learner-loop UX

Status: APPROVED
Depth: contract
Origin: plan

Source design: [docs/design/2026-07-27-teach-learner-loop-design.md](../design/2026-07-27-teach-learner-loop-design.md)

The approved design adds an OPTIONAL local course server. A served lesson closes its
cold-open loop in the browser without a paste-back; a `file://` lesson keeps today's
copy-button paste flow unchanged as the fallback. The server is opt-in friction-removal,
not a hard dependency — nothing regresses when it is absent.

#### REQ-001: serve subcommand

Detail: `teach.py serve [--workspace <cwd>] [--port 0]` starts a stdlib `http.server`
bound to `127.0.0.1` only, on an OS-assigned ephemeral port, for one workspace. It writes
`${CLAUDE_PLUGIN_DATA}/serve.json` = `{pid, port, token, workspace}` and prints
`serve: http://127.0.0.1:PORT`.

#### REQ-002: same-origin lesson serving with token

Detail: `GET /lessons/NNNN-slug.html` serves the workspace lesson with a per-process random
token injected just before `</body>` as `<script>window.__TEACH_TOKEN="..."; window.__TEACH_SERVE=1;</script>`.
No `Access-Control-Allow-Origin` header is sent on GET, so cross-origin reads are blocked.

#### REQ-003: POST /score scoring

Detail: `POST /score` accepts JSON `{lesson, line, token}`. Token absent/mismatch → `401`.
The handler binds `lesson` to the open ledger (refuses no-ledger/mismatch → `409`) and reuses
the existing scoring core (`parse_result_line` + `score_record` + `delete_ledger_line` +
`save_record` + `build_index`). Schedule + index writes are atomic. `teach.py score` remains
the only writer of schedule fields.

#### REQ-004: POST /score idempotency

Detail: a re-POST whose ledger is already closed AND whose `line` equals the last line scored
for that lesson → `200 {scored: true, already: true, schedule: ...}` (not a failure). A closed
ledger with a different line → `409 {error: "ledger closed, different line"}`.

#### REQ-005: schedule snippet in response

Detail: every `2xx` `POST /score` response carries `schedule: [{id, interval, next, lapses}, ...]`
for the records just scored, so the client can show the updated schedule in-page.

#### REQ-006: quiz.js serve/paste branching

Detail: on `finish()`, if `window.__TEACH_SERVE` and `window.__TEACH_TOKEN` are present, quiz.js
`POST /score` with `{lesson, line, token}`; otherwise it runs today's copy-button paste flow
unchanged. The result-line shape is unchanged in both paths.

#### REQ-007: quiz.js response handling + fallbacks

Detail: on `2xx` quiz.js unseals the lesson body, shows "Scored. Schedule updated.", and renders
the `schedule` snippet. On `401` it shows "Session restarted — reload this lesson to reconnect"
and reveals the copy button (paste fallback). On any other non-2xx it keeps the body sealed,
shows an in-page error, persists the result line to `localStorage`, and offers retry. The line
is never discarded on a non-2xx.

#### REQ-008: SessionStart hook starts/reuses server

Detail: for a teach workspace, the SessionStart hook reads `serve.json`; if its PID is alive it
reuses the running server, if stale it kills and restarts, if absent it spawns
`teach.py serve --workspace <cwd>` detached. It prints the serve URL alongside the existing
status lines.

#### REQ-009: SessionEnd hook stops server

Detail: a SessionEnd hook stops the server for the workspace (kill the PID in `serve.json`,
with stale-lockfile cleanup). Registered in `hooks/hooks.json`.

#### REQ-010: scoring invariant + chat-side abandon preserved

Detail: The scoring core (`cmd_score` / `score_open_cold_open`) is the single writer of schedule
fields; the `POST /score` handler calls that core, it does not write schedule fields independently.
`asked`/abandon stay chat-side (the model runs `teach.py asked` / `teach.py score "abandon"`). The
server handles only the happy-path score. The load-bearing invariant's intent (no model-fabricated
scores) is preserved because the browser records the taps.

#### REQ-011: serve-path self-check

Detail: a runnable self-check exercises token-reject, ledger-bind, idempotent-duplicate, and the
same-origin-no-CORS assertion without binding a socket; exits 0 on pass.

#### REQ-012: docs updated

Detail: `SKILL.md` session flow opens the served lesson URL when the server is up, with `file://`

- paste as the fallback; its Hooks section documents SessionEnd + server lifecycle.
  `COMPONENTS.md` Quiz section documents the serve POST, the file:// paste branching, the in-page
  status/schedule elements, the 401 reload+paste fallback, and that the copy button is retained.
  `README.md`/`AGENTS.md` note the optional serve mode.

#### REQ-013: file:// lessons unchanged (backward compatible)

Detail: `file://` lessons keep today's copy-button paste flow with no behavioral change.
`check_lesson.py --self` still passes on `templates/lesson.html`. Existing workspaces keep
working without the server.

#### REQ-014: loopback only, network-off safe

Detail: the server binds `127.0.0.1` only (never `0.0.0.0`), so no Windows firewall prompt is
triggered and the loop closes with the network cable out.
