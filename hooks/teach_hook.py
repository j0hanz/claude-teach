#!/usr/bin/env python3
"""teach_hook.py — SessionStart/Stop hook entry point for the teach plugin.

Wired from hooks/hooks.json; never invoked by the model. The deterministic state
it reads (ledger line, learning records, mission) is owned by
skills/teach/scripts/teach.py — this file only decides what a hook event should
say about that state, and stays a silent no-op outside a teach workspace.

Usage:
  teach_hook.py --event session-start|session-end|stop     (hook payload JSON on stdin)

Exit: 0 always for a well-formed event; 2 on usage error (argparse).
"""

import argparse
import contextlib
import json
import os
import subprocess
import sys
import time

# teach.py is the state layer; it lives under skills/, not here.
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        os.pardir,
        "skills",
        "teach",
        "scripts",
    ),
)

# resolved by the sys.path line above, which no static analyzer follows
from teach import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    TeachError,
    is_workspace,
    kill_pid,
    load_records,
    mission_status,
    parse_ledger_line,
    pid_alive,
    read_notes,
    read_serve_state,
    read_text,
    resume_target,
    serve_json_path,
    split_records,
    today,
    write_text,
)


def _guard_path():
    """Path to the Stop hook's one-shot guard, or None when unavailable.

    ${CLAUDE_PLUGIN_DATA} reaches hook processes and MCP/LSP subprocesses only —
    never the Bash tool the model runs `ledger` and `score` from. So only hook
    code may depend on it, and the workspace ledger line stays the single source
    of truth for whether a cold open is outstanding.
    """
    d = os.environ.get("CLAUDE_PLUGIN_DATA")
    return os.path.join(d, "nagged.txt") if d else None


def _plugin_root():
    # hooks/ lives one level under the plugin root; the sys.path insert above
    # walks the same chain to reach skills/teach/scripts.
    return os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
    )


def _ensure_server(cwd):
    """Reuse, respawn, or spawn the teach serve server for cwd.

    Prints the serve URL on success, a one-line stderr note on failure. Never
    raises and never blocks SessionStart (REQ-008): a spawn that does not bind
    in ~0.8s is reported and skipped."""
    script = os.path.join(
        _plugin_root(), "skills", "teach", "scripts", "teach.py"
    )
    # teach.py serve stores workspace as os.path.abspath; compare on that form
    # so a forward-slash cwd from the hook matches the backslash form on Windows.
    ws = os.path.abspath(cwd)
    state = read_serve_state()
    pid = state.get("pid")
    if pid and pid_alive(pid) and state.get("workspace") == ws:
        print(f"serve: http://127.0.0.1:{state['port']}")
        return
    if pid:
        kill_pid(pid)  # stale PID or workspace mismatch -> respawn
    # Detached spawn: stdio sunk so the child never inherits the hook's pipes.
    # Built per-branch (not a **kwargs splat) so the platform-specific flag
    # picks the right Popen overload instead of a loosely-typed dict.
    with contextlib.suppress(OSError):
        if os.name == "nt":
            subprocess.Popen(
                [sys.executable, script, "serve", "--workspace", cwd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=(
                    subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                ),
            )
        else:
            subprocess.Popen(
                [sys.executable, script, "serve", "--workspace", cwd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
    time.sleep(0.8)
    state = read_serve_state()
    if state.get("port"):
        print(f"serve: http://127.0.0.1:{state['port']}")
    else:
        print("teach: serve did not start", file=sys.stderr)


def event_session_start(cwd):
    ledger = parse_ledger_line(read_notes(cwd))
    t = today()
    due = len(split_records(load_records(cwd))[2])
    ms = mission_status(cwd)
    mission = (
        "provisional"
        if ms == "provisional"
        else ("absent" if ms == "absent" else "settled")
    )
    lines = [
        "teach: workspace live",
        f"date: {t.isoformat()}",
        (
            f"ledger: OPEN {ledger['lesson']} tests "
            f"{', '.join(ledger['tests'])} asked={ledger['asked']}"
            if ledger
            else "ledger: closed"
        ),
        f"due: {due}",
        f"mission: {mission}",
    ]
    rt = resume_target(cwd)
    if rt is None:
        resume_s = "—"
    elif rt["missing"]:
        resume_s = f"{rt['lesson']} file-missing"
    else:
        resume_s = f"{rt['lesson']} paste-pending" + (
            f" asked={rt['asked']}" if rt["asked"] else ""
        )
    lines.append(f"resume: {resume_s}")
    # The state above is inert without the skill: a returning learner does not
    # retype a slash command, and a model that only sees "workspace live" will
    # improvise a lesson with no retrieval gate, no validator and no ledger.
    # Name the entry point so the loop survives the session boundary.
    lines.append("next: load the claude-teach:teach skill before teaching")
    # ponytail: plain stdout -> added to Claude's context (verified). SessionStart
    # cannot block. If a future harness requires hookSpecificOutput wrapping,
    # wrap here — one-line change.
    print("\n".join(lines))
    _ensure_server(cwd)
    return 0


def event_session_end(cwd):
    # REQ-009: stop the server for this workspace and clear the stale lockfile.
    # Silent no-op when no serve.json or it belongs to a different workspace.
    state = read_serve_state()
    pid = state.get("pid")
    ws = os.path.abspath(cwd)
    if pid and pid_alive(pid) and state.get("workspace") == ws:
        kill_pid(pid)
    if state.get("workspace") == ws:
        with contextlib.suppress(OSError):
            os.remove(serve_json_path())
    return 0


def event_stop(cwd, payload):
    # The ledger line in NOTES.md is the state. The guard file only stops a
    # still-open ledger from blocking every single turn.
    if payload.get("stop_hook_active"):
        return 0
    ledger = parse_ledger_line(read_notes(cwd))
    guard = _guard_path()
    if guard is None:
        # loud on stderr, never on stdout, and only when there was something to
        # block on: without a guard file the block below would repeat every
        # turn, so the gate disables itself — say so, or the gate is silently
        # absent for the life of the install.
        # ASCII only: stderr goes to the raw console, which is cp1252 on Windows.
        if ledger is not None:
            print(
                "teach: CLAUDE_PLUGIN_DATA unset - Stop gate disabled "
                "(no guard file, cannot block once per lesson)",
                file=sys.stderr,
            )
        return 0
    if ledger is None:
        if os.path.isfile(guard):
            with contextlib.suppress(OSError):
                os.remove(guard)  # loop closed => re-arm for the next lesson
        return 0
    try:
        last = read_text(guard) if os.path.isfile(guard) else ""
    except OSError:
        last = ""
    seen, _, nagged = last.partition("\n")
    if seen.strip() != ledger["lesson"]:
        # First Stop after the ledger opened is the turn that shipped the
        # lesson — the learner has not had a chance to open it, let alone
        # answer. Arm and say nothing; blocking here nags before there is
        # anything to nag about, and burns an `asked` the abandon path counts.
        write_text(guard, ledger["lesson"])
        return 0
    if nagged.strip() == "nagged":
        return 0  # already said it once for this lesson
    if ledger["asked"]:
        return 0  # model already asked and logged it; nothing to catch
    write_text(guard, ledger["lesson"] + "\nnagged")
    # ponytail: decision:block feeds the reason to the model and continues the
    # conversation rather than ending the turn; the guard above is what keeps
    # that to once per lesson.
    msg = (
        f"teach: lesson {ledger['lesson']} shipped without closing the loop — "
        f"ask the user for the cold-open result line, then run "
        f'`teach.py score "<result line>"`, or `teach.py score "abandon"` '
        f"if the answer never came."
    )
    print(json.dumps({"decision": "block", "reason": msg}))
    return 0


def main(argv):
    p = argparse.ArgumentParser(
        prog="teach_hook.py", description="teach SessionStart/Stop hook"
    )
    p.add_argument(
        "--event", required=True, choices=["session-start", "session-end", "stop"]
    )
    p.add_argument("--workspace", default=None)
    args = p.parse_args(argv[1:])

    payload = {}
    if not sys.stdin.isatty():
        try:
            payload = json.load(sys.stdin)
        except Exception:
            payload = {}
    cwd = payload.get("cwd") or args.workspace or os.getcwd()
    if not is_workspace(cwd):
        return 0  # silent no-op outside a teach workspace
    try:
        if args.event == "session-start":
            return event_session_start(cwd)
        if args.event == "session-end":
            return event_session_end(cwd)
        return event_stop(cwd, payload)
    except TeachError as e:
        print(f"teach: {e.msg}", file=sys.stderr)
        return e.code
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
