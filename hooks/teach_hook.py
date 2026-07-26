#!/usr/bin/env python3
"""teach_hook.py — SessionStart/Stop hook entry point for the teach plugin.

Wired from hooks/hooks.json; never invoked by the model. The deterministic state
it reads (ledger line, learning records, mission) is owned by
skills/teach/scripts/teach.py — this file only decides what a hook event should
say about that state, and stays a silent no-op outside a teach workspace.

Usage:
  teach_hook.py --event session-start|stop     (hook payload JSON on stdin)

Exit: 0 always for a well-formed event; 2 on usage error (argparse).
"""

import argparse
import json
import os
import sys

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
    load_records,
    mission_status,
    parse_ledger_line,
    read_notes,
    read_text,
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


def event_session_start(cwd):
    ledger = parse_ledger_line(read_notes(cwd))
    t = today()
    due = len(split_records(load_records(cwd))[2])
    mission = (
        "provisional" if mission_status(cwd) == "provisional" else "settled"
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
    # ponytail: plain stdout -> added to Claude's context (verified). SessionStart
    # cannot block. If a future harness requires hookSpecificOutput wrapping,
    # wrap here — one-line change.
    print("\n".join(lines))
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
            os.remove(guard)  # loop closed => re-arm for the next lesson
        return 0
    try:
        last = read_text(guard).strip() if os.path.isfile(guard) else ""
    except OSError:
        last = ""
    if last == ledger["lesson"]:
        return 0  # already said it once for this lesson
    write_text(guard, ledger["lesson"])
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
    p.add_argument("--event", required=True, choices=["session-start", "stop"])
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
        return event_stop(cwd, payload)
    except TeachError as e:
        print(f"teach: {e.msg}", file=sys.stderr)
        return e.code
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
