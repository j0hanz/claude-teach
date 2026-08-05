#!/usr/bin/env python3
"""teach_hook.py — SessionStart/SessionEnd/Stop hook entry point for the teach plugin.

Wired from hooks/hooks.json; never invoked by the model. The deterministic state
it reads (ledger line, learning records, mission) is owned by
skills/teach/scripts/teach.py — this file only decides what a hook event should
say about that state, and stays a silent no-op outside a teach workspace.

Usage:
  teach_hook.py --event session-start|session-end|stop|stop-sweep
                                                (hook payload JSON on stdin)
  teach_hook.py --event selfcheck               (no payload; exercises the sweep)

Exit: 0 always for a well-formed event — a hook that cannot evaluate must not
deny, and on Stop any non-zero exit is a block whose message is stderr. 2 only
on usage error (argparse).
"""

import argparse
import contextlib
import glob
import io
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
    LEDGER_RE,
    TeachError,
    find_cold_open_comment,
    is_workspace,
    kill_pid,
    ledger_body,
    load_records,
    mission_status,
    parse_frontmatter,
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


def _plugin_data_path(name):
    """Path to a file under ${CLAUDE_PLUGIN_DATA}, or None when unset.

    ${CLAUDE_PLUGIN_DATA} reaches hook processes and MCP/LSP subprocesses only
    — never the Bash tool the model runs `ledger` and `score` from. So only hook
    code may depend on it; the workspace ledger line stays the single source of
    truth for whether a cold open is outstanding. Without the data dir there is
    no way to remember state between turns, so each gate that uses it disables
    itself rather than trap the session in a loop it cannot exit by complying.
    """
    d = os.environ.get("CLAUDE_PLUGIN_DATA")
    return os.path.join(d, name) if d else None


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
        # force-kill skips cmd_serve's finally, so serve.json stays stale —
        # clear it or the re-read below prints a dead port as the live URL.
        with contextlib.suppress(OSError):
            os.remove(serve_json_path())
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
                    subprocess.DETACHED_PROCESS
                    | subprocess.CREATE_NEW_PROCESS_GROUP
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
    guard = _plugin_data_path("nagged.txt")
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
    # The repair has to name `asked`, not jump to abandon: this gate keys its
    # own silence on ledger["asked"], and RECORDS.md puts abandon at asked: 2.
    # A message that skips the counter teaches the model to drop a record's
    # rotation with no credit and no lapse, on the first ask.
    msg = (
        f"teach: lesson {ledger['lesson']} shipped without closing the loop — "
        f"ask the user for the cold-open result line, then run "
        f'`teach.py score "<result line>"`. Nothing came back? Run '
        f"`teach.py asked` (never hand-edit the line); only at `asked: 2` run "
        f'`teach.py score "abandon"`.'
    )
    print(json.dumps({"decision": "block", "reason": msg}))
    return 0


# --- stop sweep --------------------------------------------------------------
# Second Stop handler, own guard file, own failure mode. The gate above blocks
# on an open ledger; this one blocks on a workspace that stopped matching its
# own contract. Kept apart because they fail differently: the gate is silent
# when no ledger is open, which is exactly when several of these faults happen.
#
# Every check here is an existing exact rule, never a judgement — check_lesson's
# exit code, LEDGER_RE, cold_open_pairs, the frontmatter keys RECORDS.md
# requires. Nothing in it writes workspace state; teach.py still owns that.

# Cold start: a file with no recorded signature counts as new only if it was
# touched recently, so installing this hook over a 40-lesson course does not
# open with a wall of pre-existing faults.
SWEEP_WINDOW_S = 900
MAX_FAULTS = 20


def _rel(cwd, path):
    try:
        return os.path.relpath(path, cwd).replace(os.sep, "/")
    except ValueError:  # different drives on Windows
        return path


def _key(path):
    """Signature-dict key. normcase+abspath for the same reason _ensure_server
    compares on abspath: the hook payload's cwd may arrive forward-slashed
    while glob returns the Windows form, and the loop guard is the
    safety-critical half — keyed on the raw path it re-arms on path form alone
    and blocks every turn on a fault it already reported.
    """
    return os.path.normcase(os.path.abspath(path))


def _changed(paths, seen, now):
    """[(path, signature), ...] for files whose bytes moved since last sweep.

    Doubles as the loop guard and as the cursor: a fault reported once is not
    reported again until the file actually changes.
    """
    out = []
    for p in paths:
        try:
            st = os.stat(p)
        except OSError:
            continue
        sig = f"{st.st_mtime_ns}:{st.st_size}"
        k = _key(p)
        if k in seen:
            if seen[k] != sig:
                out.append((p, sig))
        elif now - st.st_mtime < SWEEP_WINDOW_S:
            out.append((p, sig))
    return out


def _lesson_faults(cwd, path):
    """check_lesson.py's own verdict on one lesson, as report lines.

    Run in-process — this module already puts scripts/ on sys.path — so the
    sweep costs no extra interpreter. stdout is captured because the Stop
    channel is JSON and must not carry anything else.
    """
    import check_lesson  # pyright: ignore[reportMissingImports]

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check_lesson.main(["check_lesson.py", path])
    if not rc:
        return []
    lines = buf.getvalue().splitlines()
    if not lines:  # rc 2: unreadable or unparseable, detail went to stderr
        return [f"{_rel(cwd, path)}: check_lesson.py exited {rc}"]
    return [ln.replace(path, _rel(cwd, path), 1) for ln in lines]


def _unopened_ledger_faults(cwd, lesson_paths):
    """Cold open built, no ledger line open, records it tests still due.

    The mirror of the Stop gate, which fires only when a ledger IS open — so
    today this half is silent: `score` has nothing to close, the learner's
    paste has nowhere to land, and the due records stay overdue for good.
    Self-clearing: a cold open already scored this turn left its records
    not-due, so it does not report.
    """
    if parse_ledger_line(read_notes(cwd)) is not None:
        return []
    from check_lesson import (  # pyright: ignore[reportMissingImports]
        cold_open_pairs,
    )

    due_nums = None
    out = []
    for p in lesson_paths:
        try:
            pairs = cold_open_pairs(find_cold_open_comment(read_text(p)))
        except Exception:
            continue  # unparseable lesson is _lesson_faults' report, not this
        if not pairs:
            continue
        if due_nums is None:
            due_nums = {
                os.path.basename(r["path"])[:4]
                for r in split_records(load_records(cwd))[2]
            }
        if any(rid[:4] in due_nums for _, rid in pairs):
            rel = _rel(cwd, p)
            out.append(
                f"{rel}: cold open built but no ledger line is open — run "
                f"`teach.py ledger {rel}`. Until then the result line cannot "
                f"be scored and the records it tests stay overdue."
            )
    return out


def _ledger_line_faults(cwd):
    """A NOTES.md line that says 'unscored cold open' but no longer parses.

    Silent by construction: parse_ledger_line cannot see it, so `state` reports
    the ledger closed, the Stop gate goes quiet, and the cold open ceases to
    exist. Nothing else anywhere says so.
    """
    out = []
    for ln in read_notes(cwd).split("\n"):
        s = ledger_body(ln)
        if s.lower().startswith("unscored cold open") and not LEDGER_RE.match(
            s
        ):
            out.append(
                f"NOTES.md: ledger line does not parse: {s!r} — the shape is "
                f"`unscored cold open: lessons/NNNN-slug.html tests NNNN-a, "
                f"NNNN-b (asked: 0)`. Never hand-edit it; use `teach.py "
                f"ledger`, `teach.py asked`, `teach.py score`."
            )
    return out


def _record_faults(cwd, record_paths):
    """A learning record with no `next:` loads clean, counts as active, and is
    never due — so it is never retested and nothing reports it. Unlike a
    malformed record, which load_records at least names on stderr."""
    out = []
    for p in record_paths:
        try:
            fm = parse_frontmatter(read_text(p))[0]
        except (TeachError, OSError):
            continue  # load_records already names unparseable records
        if not fm.get("next", "").strip():
            out.append(
                f"{_rel(cwd, p)}: frontmatter has no `next:` — the record "
                f"loads clean and counts as active, but never becomes due, so "
                f"it is never retested. Add `next: YYYY-MM-DD`, `interval:` "
                f"and `lapses:` (references/RECORDS.md)."
            )
    return out


def sweep(cwd, seen, now):
    """Every fault in the workspace worth blocking on, plus the signatures to
    remember. Pure apart from reading the workspace — selfcheck drives it."""
    lessons = _changed(
        sorted(glob.glob(os.path.join(cwd, "lessons", "*.html"))), seen, now
    )
    records = _changed(
        sorted(glob.glob(os.path.join(cwd, "learning-records", "*.md"))),
        seen,
        now,
    )
    notes = _changed([os.path.join(cwd, "NOTES.md")], seen, now)

    faults = []
    for p, _ in lessons:
        faults += _lesson_faults(cwd, p)
    faults += _unopened_ledger_faults(cwd, [p for p, _ in lessons])
    faults += _record_faults(cwd, [p for p, _ in records])
    if notes:
        faults += _ledger_line_faults(cwd)
    return faults, lessons + records + notes


def event_stop_sweep(cwd, payload):
    if payload.get("stop_hook_active"):
        return 0
    state_path = _plugin_data_path("swept.json")
    if state_path is None:
        # ASCII only: stderr goes to the raw console, cp1252 on Windows.
        print(
            "teach: CLAUDE_PLUGIN_DATA unset - workspace sweep disabled "
            "(no signature file, cannot report a fault only once)",
            file=sys.stderr,
        )
        return 0
    try:
        seen = json.loads(read_text(state_path))
        if not isinstance(seen, dict):
            seen = {}
    except (OSError, ValueError):
        seen = {}
    faults, fresh = sweep(cwd, seen, time.time())
    for p, sig in fresh:
        seen[_key(p)] = sig
    with contextlib.suppress(OSError):
        write_text(state_path, json.dumps(seen))
    if not faults:
        return 0
    shown = faults[:MAX_FAULTS]
    msg = "teach: workspace check failed —\n" + "\n".join(shown)
    if len(faults) > MAX_FAULTS:
        msg += f"\n… and {len(faults) - MAX_FAULTS} more"
    print(json.dumps({"decision": "block", "reason": msg}))
    return 0


def selfcheck():
    """Exercise every sweep detector against a throwaway workspace, no payload.

    The sweep never runs by hand — it needs a Stop event and a plugin data dir —
    so this is the one runnable check that fails if a detector stops detecting.
    Exit 0 only if every assertion passes.
    """
    import shutil
    import tempfile

    base = tempfile.mkdtemp(prefix="teach-sweep-")
    fails = []

    def want(name, got, ok):
        if not ok:
            fails.append(f"{name}: {got!r}")

    try:
        os.makedirs(os.path.join(base, "lessons"))
        os.makedirs(os.path.join(base, "learning-records"))
        write_text(
            os.path.join(base, "learning-records", "0001-x.md"),
            "---\nnext: 2020-01-01\ninterval: 1\nlapses: 0\n---\n\n# x\n",
        )
        write_text(
            os.path.join(base, "learning-records", "0002-y.md"),
            "---\ninterval: 1\nlapses: 0\n---\n\n# y\n",
        )
        # no lang attribute -> check_lesson reports a11y-lang
        write_text(
            os.path.join(base, "lessons", "0001-x.html"),
            "<!doctype html><html><head><title>x</title></head><body>"
            '<div class="cold-open"><!-- cold-open: 1=0001-x --></div>'
            "</body></html>",
        )

        f = _lesson_faults(base, os.path.join(base, "lessons", "0001-x.html"))
        want("lesson-invalid", f, any("a11y-lang" in x for x in f))

        lessons = [os.path.join(base, "lessons", "0001-x.html")]
        f = _unopened_ledger_faults(base, lessons)
        want("ledger-unopened", f, len(f) == 1)

        write_text(
            os.path.join(base, "NOTES.md"),
            "# Notes\n\n## Working notes\n\n- unscored cold open: "
            "lessons/0001-x.html tests 0001-x (asked: 0)\n",
        )
        f = _unopened_ledger_faults(base, lessons)
        want("ledger-open-silent", f, f == [])
        f = _ledger_line_faults(base)
        want("ledger-line-ok", f, f == [])

        write_text(
            os.path.join(base, "NOTES.md"),
            "# Notes\n\n- unscored cold open: lessons/0001-x.html tests "
            "0001-x asked 0\n",
        )
        f = _ledger_line_faults(base)
        want("ledger-line-mangled", f, len(f) == 1)

        recs = sorted(
            glob.glob(os.path.join(base, "learning-records", "*.md"))
        )
        f = _record_faults(base, recs)
        want("record-no-next", f, len(f) == 1 and "0002-y" in f[0])

        # loop guard: a fault reported once must not report again unchanged
        seen = {}
        now = time.time()
        first, fresh = sweep(base, seen, now)
        want("sweep-reports", first, len(first) > 0)
        for p, sig in fresh:
            seen[_key(p)] = sig
        second, _ = sweep(base, seen, now)
        want("sweep-idempotent", second, second == [])

        # cold start: a file older than the window is seeded, not reported
        old = now - SWEEP_WINDOW_S - 60
        for p in [*lessons, *recs, os.path.join(base, "NOTES.md")]:
            os.utime(p, (old, old))
        want("cold-start-quiet", None, sweep(base, {}, now)[0] == [])
    finally:
        shutil.rmtree(base, ignore_errors=True)

    if fails:
        for line in fails:
            print(f"selfcheck FAIL {line}", file=sys.stderr)
        return 1
    print("selfcheck OK")
    return 0


def main(argv):
    p = argparse.ArgumentParser(
        prog="teach_hook.py", description="teach session hooks"
    )
    p.add_argument(
        "--event",
        required=True,
        choices=[
            "session-start",
            "session-end",
            "stop",
            "stop-sweep",
            "selfcheck",
        ],
    )
    p.add_argument("--workspace", default=None)
    args = p.parse_args(argv[1:])
    if args.event == "selfcheck":
        return selfcheck()

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
        if args.event == "stop-sweep":
            return event_stop_sweep(cwd, payload)
        return event_stop(cwd, payload)
    # Exit 0 on every failure, never e.code: on Stop a non-zero exit is a block
    # whose message is stderr, so an unexpected parse or IO failure would turn
    # into a spurious turn block. A hook that cannot evaluate must not deny.
    except BrokenPipeError:
        return 0
    except TeachError as e:
        print(f"teach: {e.msg}", file=sys.stderr)
        return 0
    except OSError as e:
        print(f"teach: {e}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
