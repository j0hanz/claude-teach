#!/usr/bin/env python3
"""teach.py — stdlib-only course runtime for the teach plugin.

Owns the deterministic state over a learner workspace: schedule, ledger, scoring
arithmetic, invariants. The judgement stays in SKILL.md; this is the half with one
right answer that does not depend on the learner.

Usage:
  python teach.py state
  python teach.py score "<result line verbatim>"
  python teach.py ledger lessons/NNNN-slug.html
  python teach.py asked
  python teach.py index

The SessionStart/Stop hooks are a separate entry point — hooks/teach_hook.py at the
plugin root — which imports this module for state and owns nothing itself.

Workspace = the current working directory (the learner's project). A directory is a
teach workspace if MISSION.md or learning-records/ exists in it.

Exit: 0 ok, 1 ambiguity/workspace-violation (refuse, write nothing), 2 usage/parse error.
"""

import contextlib
import glob
import os
import re
import sys
from datetime import date, timedelta
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    import argparse

# ponytail: one guard at the stream, not an ASCII hunt through every string.
# The report prints em dashes; a cp437 console (still the OEM default in
# cmd.exe) and cp932 cannot encode U+2014, and `teach.py state` is step 1 of
# every session — a traceback there kills the session before it starts. This
# sits at module level on purpose: hooks/teach_hook.py imports this module and
# prints the same characters, so importing teach fixes the hook process too.
# Ceiling: an unencodable character becomes "?", not a transliteration.
# File writes are unaffected — write_text pins encoding="utf-8".
for _stream in (sys.stdout, sys.stderr):
    with contextlib.suppress(AttributeError, OSError, ValueError):
        _stream.reconfigure(errors="replace")


# --- types ------------------------------------------------------------------
class RecordDict(TypedDict):
    path: str
    fm: dict[str, str]
    raw: list[str]
    body: str
    quotes: dict[str, str | None]
    interval: int | float
    lapses: int
    lesson: str | None
    status: str
    next: date | None
    title: str


class LedgerLine(TypedDict):
    lesson: str
    tests: list[str]
    asked: int


class ResumeTarget(TypedDict):
    lesson: str
    missing: bool
    asked: int


# --- constants ---------------------------------------------------------------
DEFAULT_DOUBLING = 2
DEFAULT_CEILING = 90
PROJECT_MARKERS = (
    ".git",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    ".hg",
    ".svn",
)

# Notes line, exact shape only — any other shape does not parse (WORKSPACE.md § Notes).
SPACING_RE = re.compile(
    r"^-?\s*spacing:\s*\{\s*doubling:\s*([0-9]+(?:\.[0-9]+)?)\s*,\s*"
    r"ceiling:\s*([0-9]+(?:\.[0-9]+)?)\s*\}\s*$"
)

# ledger: "unscored cold open: lessons/NNNN-x.html tests 0003-a, 0005-b (asked: 0)"
LEDGER_RE = re.compile(
    r"^unscored cold open:\s+(lessons/\S+)\s+tests\s+(.+?)\s+\(asked:\s*(\d+)\)\s*$"
)

# lesson cold-open comment: "cold-open: 1=0003-slug 2=0007-slug"
COLD_OPEN_RE = re.compile(r"(\d+)=([0-9A-Za-z][0-9A-Za-z\-]*)")
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S | re.I)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")

TODAY: date | None = None  # tests override; None => datetime.date.today()


def today() -> date:
    return TODAY if TODAY is not None else date.today()


def num_str(x: int | float | str) -> str:
    """'4' not '4.0'; '4.5' stays."""
    f = float(x)
    return str(int(f)) if f == int(f) else str(f)


def _parse_interval(s: str | None) -> int | float:
    """Interval is float-tolerant on reload. score_record writes fractional
    intervals via num_str whenever doubling or ceiling is fractional, so an
    int-only guard here rejects them on the next load and silently resets the
    schedule to 1. Preserve int when integral to match num_str's output.

    nan/inf fall back to 1: float() accepts them, but int(nan) raises
    ValueError and int(inf) raises OverflowError, and a hand-edited
    `interval: nan` must not crash load_record."""
    if s is None:
        return 1
    try:
        v = float(s)
    except (ValueError, TypeError):
        return 1
    if v < 1 or v != v or v == float("inf") or v == float("-inf"):
        return 1
    return int(v) if v == int(v) else v


def parse_date(s: str) -> date:
    try:
        return date.fromisoformat(s.strip())
    except (ValueError, AttributeError):
        raise TeachError(
            2, f'unparseable date "{s}" (want YYYY-MM-DD)'
        ) from None


class TeachError(Exception):
    """carry exit code + message; 2 = usage/parse, 1 = ambiguity/violation."""

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(msg)
        self.code = code
        self.msg = msg


# --- IO ---------------------------------------------------------------------
def read_text(path: str) -> str:
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write_text(path: str, text: str) -> None:
    """atomic write — the multi-file score write is the load-bearing reason."""
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


# --- frontmatter (the load-bearing contract) -------------------------------
def parse_frontmatter(
    text: str,
) -> tuple[dict[str, str], list[str], str, dict[str, str | None]]:
    """Return (fm_dict, raw_lines, body, quotes).

    raw_lines are the lines between the fences, verbatim (trailing \r preserved
    so CRLF round-trips). body is the bytes after the closing fence, verbatim.
    fm_dict maps key->value for non-comment, non-blank lines. quotes maps key->
    '"'|"'"|None for the value's quote style.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, [], text, {}
    close = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close = i
            break
    if close is None:
        raise TeachError(2, "unterminated frontmatter (no closing ---)")
    raw = lines[1:close]
    body = "\n".join(lines[close + 1 :])
    fm: dict[str, str] = {}
    quotes: dict[str, str | None] = {}
    for ln in raw:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if ":" not in s:
            continue
        k, _, v = s.partition(":")
        k = k.strip()
        v = v.strip()
        q = None
        if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
            q = v[0]
            v = v[1:-1]
        fm[k] = v
        quotes[k] = q
    return fm, raw, body, quotes


def serialize_frontmatter(
    fm: dict[str, str],
    raw: list[str],
    body: str,
    quotes: dict[str, str | None],
    changed: set[str],
) -> str:
    """Re-emit raw byte-for-byte except lines whose key is in `changed`."""
    out = []
    written: set[str] = set()
    for ln in raw:
        s = ln.strip()
        key = None
        if s and not s.startswith("#") and ":" in s:
            key = s.partition(":")[0].strip()
        if key in changed:
            written.add(key)
            v = fm[key]
            qs = quotes.get(key)
            vstr = (qs + str(v) + qs) if qs else str(v)
            line = f"{key}: {vstr}"
            if ln.endswith("\r"):
                line += "\r"
            out.append(line)
        else:
            out.append(ln)
    for key in sorted(changed - written):
        v = fm[key]
        qs = quotes.get(key)
        vstr = (qs + str(v) + qs) if qs else str(v)
        out.append(f"{key}: {vstr}")
    return "\n".join(["---"] + out + ["---"]) + "\n" + body


def load_record(path: str) -> RecordDict:
    fm, raw, body, quotes = parse_frontmatter(read_text(path))
    rec: RecordDict = {
        "path": path,
        "fm": fm,
        "raw": raw,
        "body": body,
        "quotes": quotes,
        "interval": _parse_interval(fm.get("interval")),
        "lapses": (
            int(fm["lapses"])
            if "lapses" in fm and fm["lapses"].lstrip("-").isdigit()
            else 0
        ),
        "lesson": fm.get("lesson"),
        "status": fm.get("status", "active"),
        "next": (
            parse_date(fm["next"])
            if "next" in fm and fm["next"].strip()
            else None
        ),
        "title": _title(body),
    }
    return rec


def _title(body: str) -> str:
    for ln in body.split("\n"):
        s = ln.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return "(no title)"


def save_record(rec: RecordDict, changed: set[str]) -> None:
    out = serialize_frontmatter(
        rec["fm"], rec["raw"], rec["body"], rec["quotes"], changed
    )
    write_text(rec["path"], out)


# --- spacing ----------------------------------------------------------------
def resolve_spacing(notes_text: str) -> tuple[float, float, str]:
    """NOTES.md spacing: (exact shape) > built-in. Returns (d, c, source)."""
    for ln in notes_text.split("\n"):
        m = SPACING_RE.match(ln.strip())
        if m:
            return float(m.group(1)), float(m.group(2)), "NOTES.md"
    return float(DEFAULT_DOUBLING), float(DEFAULT_CEILING), "built-in"


# --- workspace / NNNN / ledger ----------------------------------------------
def is_workspace(cwd: str) -> bool:
    return os.path.isfile(os.path.join(cwd, "MISSION.md")) or os.path.isdir(
        os.path.join(cwd, "learning-records")
    )


def read_notes(cwd: str) -> str:
    p = os.path.join(cwd, "NOTES.md")
    return read_text(p) if os.path.isfile(p) else ""


def load_records(cwd: str) -> list[RecordDict]:
    """Every learning record, sorted by filename. A malformed one is skipped
    rather than raised — it must not cost the learner the report or the index
    — but never silently: a skipped record vanishes from the due pool, from
    the report's counts and from index.html, and nothing else would say so."""
    lr_dir = os.path.join(cwd, "learning-records")
    out: list[RecordDict] = []
    if os.path.isdir(lr_dir):
        for name in sorted(os.listdir(lr_dir)):
            if name.endswith(".md"):
                try:
                    out.append(load_record(os.path.join(lr_dir, name)))
                except (TeachError, OSError) as e:
                    # stderr, not the report: cmd_state's stdout has a fixed
                    # shape its readers parse positionally.
                    print(
                        f"teach: skipping learning-records/{name}: {e}",
                        file=sys.stderr,
                    )
    return out


def split_records(
    records: list[RecordDict],
) -> tuple[list[RecordDict], list[RecordDict], list[RecordDict]]:
    """(active, retired, due) — one status rule, so every caller agrees."""
    active = [
        r for r in records if r["status"] not in ("retired", "superseded")
    ]
    retired = [r for r in records if r["status"] in ("retired", "superseded")]
    t = today()
    due = [r for r in active if r["next"] is not None and r["next"] <= t]
    return active, retired, due


def due_pool(due: list[RecordDict]) -> list[RecordDict]:
    """At most three due records, distinct source lessons first — a cold open
    interleaves rather than retesting one lesson three times (SKILL.md step 5)."""
    seen: set[str | None] = set()
    first: list[RecordDict] = []
    rest: list[RecordDict] = []
    for r in due:
        if r["lesson"] in seen:
            rest.append(r)
        else:
            seen.add(r["lesson"])
            first.append(r)
    return (first + rest)[:3]


def next_number(dirpath: str) -> int:
    hi = 0
    if os.path.isdir(dirpath):
        for name in os.listdir(dirpath):
            m = re.match(r"(\d{4})-", name)
            if m:
                hi = max(hi, int(m.group(1)))
    return hi + 1


def parse_ledger_line(notes_text: str) -> LedgerLine | None:
    """Return {'lesson':..., 'tests':[id,...], 'asked':N} or None."""
    for ln in notes_text.split("\n"):
        s = ln.strip()
        if s.startswith("- "):
            s = s[2:].strip()
        m = LEDGER_RE.match(s)
        if m:
            lesson = m.group(1)
            tests = [t.strip() for t in m.group(2).split(",") if t.strip()]
            asked = int(m.group(3))
            return {"lesson": lesson, "tests": tests, "asked": asked}
    return None


def delete_ledger_line(notes_text: str) -> str:
    out = []
    removed = 0
    for ln in notes_text.split("\n"):
        s = ln.strip()
        if s.startswith("- "):
            s = s[2:].strip()
        if LEDGER_RE.match(s):
            removed += 1
            continue
        out.append(ln)
    if removed != 1:
        raise TeachError(1, f"expected exactly 1 ledger line, found {removed}")
    return "\n".join(out)


def bump_asked(notes_text: str) -> tuple[str, int]:
    """Rewrite the open ledger line with asked+1. Returns (text, new_asked).

    Rebuilt from the regex's own groups, never from a hand-edit: the shape is
    strict (LEDGER_RE) and a line that stops matching is a cold open no
    consumer can see any more. Preserves the list marker, the indentation and
    a trailing \r, so a CRLF NOTES.md round-trips.
    """
    out = []
    hits = 0
    new_asked = None
    for ln in notes_text.split("\n"):
        s = ln.strip()
        prefix = ""
        if s.startswith("- "):
            prefix = "- "
            s = s[2:].strip()
        m = LEDGER_RE.match(s)
        if not m:
            out.append(ln)
            continue
        hits += 1
        new_asked = int(m.group(3)) + 1
        indent = ln[: len(ln) - len(ln.lstrip())]
        tail = "\r" if ln.endswith("\r") else ""
        out.append(
            f"{indent}{prefix}unscored cold open: {m.group(1)} "
            f"tests {m.group(2)} (asked: {new_asked}){tail}"
        )
    if hits != 1 or new_asked is None:
        raise TeachError(1, f"expected exactly 1 ledger line, found {hits}")
    return "\n".join(out), new_asked


def find_cold_open_comment(html: str) -> str | None:
    """Text of the cold-open mapping comment, or None. Reuses check_lesson's
    DocParser so the structural rule — the comment must sit inside a .cold-open
    ancestor — is the same one the validator enforces, not a substring scan that
    latches the first comment containing 'cold-open:' (a stray TODO note matches
    that and steals the slot from the real mapping)."""
    if "cold-open:" not in html:
        return None
    from check_lesson import DocParser

    p = DocParser()
    p.feed(html)
    p.close()
    return p.cold_open_comment[1] if p.cold_open_comment else None


def parse_cold_open_comment(html: str) -> list[tuple[int, str]]:
    """Return [(pos, record_id), ...] from the cold-open mapping comment.

    Positions may appear in any order — cmd_ledger sorts by position when it
    builds the tests list, so order is not semantically meaningful and an
    out-of-order comment is not a defect. Sorting here keeps the runtime
    lenient, matching check_lesson's sorted contiguity check. Position gaps
    and repeats (1,1,3) are rejected, and so is one record id appearing at
    two positions — scoring would write that record twice."""
    text = find_cold_open_comment(html)
    pairs = (
        [(int(n), rid) for n, rid in COLD_OPEN_RE.findall(text)]
        if text
        else []
    )
    if not pairs:
        raise TeachError(
            1, "no <!-- cold-open: N=ID ... --> comment in lesson"
        )
    positions = sorted(p for p, _ in pairs)
    if positions != list(range(1, len(pairs) + 1)):
        raise TeachError(
            1,
            f"cold-open positions {positions} must be 1..{len(pairs)} "
            f"contiguous",
        )
    ids = [rid for _, rid in pairs]
    dupes = sorted({r for r in ids if ids.count(r) > 1})
    if dupes:
        raise TeachError(
            1,
            f"cold-open comment maps {', '.join(dupes)} to more than one "
            f"position; a cold open tests one learning record per item, and "
            f"scoring would write that record twice keeping only the last "
            f"outcome. Fix the lesson's cold-open comment and quiz, then "
            f"re-run ledger.",
        )
    return pairs


# --- result line / scoring ---------------------------------------------------
def parse_result_line(line: str) -> tuple[str | None, list[tuple[int, str]]]:
    """'Cold open 0007-x: 1 right, 2 wrong' -> ('0007-x', [(1,'right'),(2,'wrong')]).

    The id in the head binds the line to the lesson that produced it. A line
    without one comes from a quiz.js older than template v3; cmd_score refuses it
    rather than guessing which ledger it belongs to.
    Abandon is a separate invocation (result arg == 'abandon'), not parsed here.
    """
    s = line.strip()
    if ":" not in s:
        raise TeachError(2, f'unparseable result line "{line}"')
    head, _, rest = s.partition(":")
    m = re.search(r"(\d{4}[0-9A-Za-z\-]*)\s*$", head.strip())
    lesson_id = m.group(1) if m else None
    rest = rest.strip()
    results = []
    for tok in rest.split(","):
        parts = tok.split()
        if len(parts) != 2:
            raise TeachError(2, f'unparseable outcome "{tok}" in "{line}"')
        pos_s, outcome = parts
        try:
            pos = int(pos_s)
        except ValueError:
            raise TeachError(
                2, f'bad position "{pos_s}" in "{line}"'
            ) from None
        if outcome not in ("right", "wrong"):
            raise TeachError(
                2, f'outcome "{outcome}" not right/wrong in "{line}"'
            )
        results.append((pos, outcome))
    positions = [p for p, _ in results]
    if positions != list(range(1, len(results) + 1)):
        raise TeachError(
            2, f"positions {positions} must be 1..{len(results)} contiguous"
        )
    return lesson_id, results


def score_record(
    rec: RecordDict, outcome: str, doubling: float, ceiling: float
) -> set[str]:
    """Apply one scoring row (RECORDS.md § Scoring). Mutates rec; returns set(changed keys)."""
    changed: set[str] = set()
    t = today()
    if outcome == "right":
        if rec["interval"] < ceiling:
            new_iv = min(rec["interval"] * doubling, ceiling)
            rec["fm"]["interval"] = num_str(new_iv)
            rec["interval"] = (
                int(new_iv) if float(new_iv).is_integer() else new_iv
            )
            rec["fm"]["next"] = (t + timedelta(days=new_iv)).isoformat()
            rec["next"] = t + timedelta(days=new_iv)
            rec["fm"]["lapses"] = "0"
            rec["lapses"] = 0
            changed |= {"interval", "next", "lapses"}
        else:  # at/over ceiling -> retire
            rec["fm"]["status"] = "retired"
            rec["status"] = "retired"
            rec["fm"]["lapses"] = "0"
            rec["lapses"] = 0
            changed |= {"status", "lapses"}
    elif outcome == "wrong":
        rec["fm"]["interval"] = "1"
        rec["interval"] = 1
        rec["fm"]["next"] = (t + timedelta(days=1)).isoformat()
        rec["next"] = t + timedelta(days=1)
        rec["fm"]["lapses"] = str(rec["lapses"] + 1)
        rec["lapses"] = rec["lapses"] + 1
        changed |= {"interval", "next", "lapses"}
    elif outcome == "abandon":
        rec["fm"]["next"] = (t + timedelta(days=rec["interval"])).isoformat()
        rec["next"] = t + timedelta(days=rec["interval"])
        changed.add("next")
    else:
        raise TeachError(2, f"unknown outcome {outcome}")
    return changed


def prior_cold_opens(cwd: str, rec_id: str) -> list[str]:
    """Lesson numbers whose cold-open comment names this record — the per-record
    Grep that used to live in SKILL.md, now in the report so the model reads titles,
    not bodies, for everything except the due few."""
    hits = []
    for p in glob.glob(os.path.join(cwd, "lessons", "*.html")):
        try:
            html = read_text(p)
        except OSError:
            continue
        text = find_cold_open_comment(html)
        if not text:
            continue
        for _, rid in COLD_OPEN_RE.findall(text):
            if rid == rec_id:
                hits.append(os.path.basename(p).split("-")[0])
    return sorted(set(hits))


def resolve_record_path(cwd: str, rec_id: str) -> str:
    direct = os.path.join(cwd, "learning-records", rec_id + ".md")
    if os.path.isfile(direct):
        return direct
    m = re.match(r"(\d{4})", rec_id)
    if not m:
        raise TeachError(1, f'record id "{rec_id}" has no NNNN prefix')
    matches = glob.glob(
        os.path.join(cwd, "learning-records", m.group(1) + "-*.md")
    )
    matches = [x for x in matches if not x.endswith(".tmp")]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise TeachError(1, f'no learning record matching "{rec_id}"')
    raise TeachError(1, f'ambiguous record id "{rec_id}": {matches}')


# --- subcommands ------------------------------------------------------------
def cmd_state(args: "argparse.Namespace") -> int:
    cwd = args.workspace
    if not is_workspace(cwd):
        print(f"teach-state 0  not a teach workspace  ({cwd})")
        return 0
    notes = read_notes(cwd)
    doubling, ceiling, src = resolve_spacing(notes)
    ledger = parse_ledger_line(notes)
    active, retired, due = split_records(load_records(cwd))
    t = today()
    due.sort(
        key=lambda r: (
            ((t - r["next"]).days, r["lesson"] or "")
            if r["next"] is not None
            else (0, "")
        )
    )
    pool = due_pool(due)
    distinct = len({r["lesson"] for r in pool})
    assets = asset_status(cwd)
    inv = inventory(cwd)
    print(f"teach-state 1  workspace={cwd}  today={t.isoformat()}")
    print(f"mission     {mission_status(cwd)}")
    print(f"project     {project_markers(cwd)}")
    print(
        f"spacing     doubling={num_str(doubling)} ceiling={num_str(ceiling)}  "
        f"(source: {src})"
    )
    if ledger:
        print(
            f"ledger      OPEN  {ledger['lesson']} tests "
            f"{', '.join(ledger['tests'])}  asked={ledger['asked']}"
        )
    else:
        print("ledger      closed")
    rt = resume_target(cwd)
    if rt is None:
        print("resume      —")
    elif rt["missing"]:
        print(f"resume      {rt['lesson']}  file-missing")
    else:
        print(
            f"resume      {rt['lesson']}  paste-pending"
            + (f" asked={rt['asked']}" if rt["asked"] else "")
        )
    print(
        f"due         {len(due)} of {len(active)} active records, "
        f"{distinct} distinct source lessons"
    )
    for r in pool:
        if r["next"] is not None:
            over = (t - r["next"]).days
            over_s = "today" if over == 0 else f"{over}d over"
        else:
            over_s = "unscheduled"
        reteach = "  RE-TEACH" if r["lapses"] >= 3 else ""
        rid = os.path.splitext(os.path.basename(r["path"]))[0]
        prior = prior_cold_opens(cwd, rid)
        prior_s = ", ".join(prior) if prior else "—"
        print(
            f"  {rid:<16} {over_s:<8} interval={r['interval']:<3} lapses={r['lapses']}  "
            f"from {r['lesson'] or '—'}  prior cold opens: {prior_s}{reteach}"
        )
    print(f"records     {len(active)} active, {len(retired)} retired")
    nl = next_number(os.path.join(cwd, "lessons"))
    nr = next_number(os.path.join(cwd, "learning-records"))
    print(f"next        lessons/{nl:04d}-   learning-records/{nr:04d}-")
    print("assets     " + "   ".join(f"{n} {st}" for n, st in assets))
    print("inventory   " + inv)
    return 0


def mission_status(cwd: str) -> str:
    p = os.path.join(cwd, "MISSION.md")
    if not os.path.isfile(p):
        return "absent"
    txt = read_text(p)
    if re.search(r"\*\*provisional\*\*", txt, re.I):
        return "provisional"
    return "ok, not provisional"


def project_markers(cwd: str) -> str:
    found = [
        m for m in PROJECT_MARKERS if os.path.exists(os.path.join(cwd, m))
    ]
    return ", ".join(found) if found else "no code-project markers in cwd"


def asset_status(cwd: str) -> list[tuple[str, str]]:
    """Reuse check_lesson's stamp parser and templates dir; per-asset ok/STALE."""
    from check_lesson import TEMPLATES_DIR, parse_stamp

    assets_dir = os.path.join(cwd, "assets")
    out = []
    for name in ("lesson.css", "quiz.js"):
        ws = os.path.join(assets_dir, name)
        if not os.path.isfile(ws):
            continue
        tmpl = os.path.join(TEMPLATES_DIR, name)
        try:
            wt = parse_stamp(read_text(ws))
            tt = parse_stamp(read_text(tmpl))
        except OSError:
            # loud on purpose: this check used to report 'ok' when it could not
            # read the template, which is how a wrong templates path stayed
            # invisible for the life of the file
            out.append((name, "UNKNOWN (template unreadable)"))
            continue
        if wt is None or tt is None:
            out.append((name, "UNKNOWN (no version stamp)"))
        elif wt == tt:
            out.append((name, "ok"))
        else:
            out.append(
                (name, f"STALE (v{wt}, current v{tt}) — re-copy the template")
            )
    if not out:
        return [("assets", "(none copied)")]
    return out


def inventory(cwd: str) -> str:
    lessons = len(glob.glob(os.path.join(cwd, "lessons", "*.html")))
    reference = len(glob.glob(os.path.join(cwd, "reference", "*.html")))
    know, comm = 0, 0
    rp = os.path.join(cwd, "RESOURCES.md")
    if os.path.isfile(rp):
        section = None
        for ln in read_text(rp).split("\n"):
            h = ln.strip().lower()
            if h.startswith("## "):
                section = h[3:]
            elif ln.strip().startswith("- ") and section:
                if "knowledge" in section:
                    know += 1
                elif "community" in section:
                    comm += 1
    return f"{lessons} lessons, {reference} reference docs, {know} knowledge + {comm} community sources"


def _doc_title(path: str) -> str:
    """First <h1>, else <title>, else the file stem. Tags stripped, entities
    decoded, space collapsed — esc() in build_index re-escapes, so decode here
    or an `&amp;` in a title ends up double-escaped on the page."""
    from html import unescape

    try:
        text = read_text(path)
    except OSError:
        return os.path.splitext(os.path.basename(path))[0]
    m = H1_RE.search(text) or TITLE_RE.search(text)
    if not m:
        return os.path.splitext(os.path.basename(path))[0]
    return " ".join(unescape(TAG_RE.sub("", m.group(1))).split())


def _topic(cwd: str) -> str:
    p = os.path.join(cwd, "MISSION.md")
    if os.path.isfile(p):
        m = re.search(r"^#\s*Mission:\s*(.+)$", read_text(p), re.M)
        if m:
            return m.group(1).strip()
    return os.path.basename(os.path.abspath(cwd)) or "Course"


def _lang(cwd: str) -> str:
    """Match the course's own language rather than assuming English."""
    for p in sorted(
        glob.glob(os.path.join(cwd, "lessons", "*.html")), reverse=True
    ):
        try:
            m = re.search(r'<html[^>]*\blang="([^"]+)"', read_text(p))
        except OSError:
            continue
        if m:
            return m.group(1)
    return "en"


def resume_target(cwd: str) -> ResumeTarget | None:
    """The open cold-open ledger's lesson, or None. One derivation shared by
    build_index, cmd_state, and the SessionStart hook — the resume signal is
    ledger-driven (exact), never guessed from lesson numbering.

    Returns {'lesson': <rel-path>, 'missing': bool, 'asked': N} or None when
    no cold-open ledger is open. `missing` is True when the ledger names a
    lesson file that is no longer on disk (dangling reference).
    """
    ledger = parse_ledger_line(read_notes(cwd))
    if ledger is None:
        return None
    lesson = ledger["lesson"]  # forward-slash rel path, per cmd_ledger
    full = lesson if os.path.isabs(lesson) else os.path.join(cwd, lesson)
    return {
        "lesson": lesson,
        "missing": not os.path.isfile(full),
        "asked": ledger["asked"],
    }


def resume_section(cwd: str) -> list[str]:
    """HTML lines for the 'Continue where you were' section, or [] if nothing
    pending. Isolated so a dangling or malformed ledger never breaks the page
    — any failure degrades to 'no section', never a half-rendered index."""
    from html import escape as esc

    try:
        target = resume_target(cwd)
    except Exception:
        return []
    if target is None:
        return []
    lesson = target["lesson"]
    if target["missing"]:
        return [
            "    <h2>Continue where you were</h2>",
            f"    <p>An open cold open names <code>{esc(lesson)}</code> "
            "but its file is missing — tell your tutor.</p>",
        ]
    title = _doc_title(os.path.join(cwd, lesson))
    asked = target["asked"]
    prompt = "paste your cold-open result line into your chat with your tutor."
    if asked > 0:
        prompt += (
            f" (your tutor has asked {asked} "
            + ("time" if asked == 1 else "times")
            + " and you have not pasted it back yet.)"
        )
    return [
        "    <h2>Continue where you were</h2>",
        f'    <p><a href="{esc(lesson)}">{esc(title)}</a> — {prompt}</p>',
    ]


def _format_links(paths: list[str], prefix: str) -> str:
    from html import escape as esc

    return "\n".join(
        f'      <li><a href="{esc(prefix + os.path.basename(p))}">'
        f"{esc(_doc_title(p))}</a></li>"
        for p in paths
    )


def _format_when(r: RecordDict, t: date) -> str:
    if r["status"] in ("retired", "superseded"):
        return "banked"
    if r["next"] is None:
        return "unscheduled"
    d = (r["next"] - t).days
    if d < 0:
        return f"{-d} d overdue"
    return "due today" if d == 0 else f"in {d} d"


def build_index(cwd: str) -> str:
    """Write the learner-facing course home page. Returns its path.

    Deterministic by construction — same workspace state, same bytes — which is
    why it lives here and not in the model's judgement (SKILL.md intro).
    """
    from html import escape as esc

    if not is_workspace(cwd):
        raise TeachError(1, f"not a teach workspace ({cwd})")
    lessons = sorted(glob.glob(os.path.join(cwd, "lessons", "*.html")))
    # Resume section is computed before the zero-lessons guard so a dangling
    # ledger (open cold open naming a lesson file that is gone) still renders
    # the "file is missing" line instead of crashing the rebuild — the only
    # lesson being the deleted one is exactly the case the guard would catch.
    resume = resume_section(cwd)
    if not lessons and not resume:
        raise TeachError(1, "no lessons yet — nothing to index")
    if not os.path.isfile(os.path.join(cwd, "assets", "lesson.css")):
        raise TeachError(
            1,
            "assets/lesson.css missing — copy templates/lesson.css "
            "into assets/ first",
        )
    reference = sorted(glob.glob(os.path.join(cwd, "reference", "*.html")))

    t = today()
    records = load_records(cwd)
    active, _, due = split_records(records)

    learned = "\n".join(
        f'      <li>{esc(r["title"])} <span class="eyebrow">{esc(_format_when(r, t))}</span></li>'
        for r in records
    )

    parts = [
        "<!doctype html>",
        f'<html lang="{esc(_lang(cwd))}">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        f"  <title>{esc(_topic(cwd))} — course</title>",
        '  <link rel="stylesheet" href="assets/lesson.css">',
        "</head>",
        "<body>",
        '  <main class="lesson">',
        f'    <p class="eyebrow">Course · {t.isoformat()}</p>',
        f"    <h1>{esc(_topic(cwd))}</h1>",
        f"    <p>{len(lessons)} lessons · {len(reference)} reference documents · "
        f"{len(active)} tracked, {len(due)} due today.</p>",
    ]
    if resume:
        parts += [""] + resume
    parts += [
        "",
        "    <h2>Lessons</h2>",
        "    <ul>",
        _format_links(lessons, "lessons/"),
        "    </ul>",
    ]
    if reference:
        parts += [
            "",
            "    <h2>Reference</h2>",
            "    <ul>",
            _format_links(reference, "reference/"),
            "    </ul>",
        ]
    if records:
        parts += [
            "",
            "    <h2>What you have worked through</h2>",
            "    <ul>",
            learned,
            "    </ul>",
        ]
    parts += ["  </main>", "</body>", "</html>", ""]
    out = os.path.join(cwd, "index.html")
    write_text(out, "\n".join(parts))
    return out


def cmd_index(args: "argparse.Namespace") -> int:
    print(f"index: {build_index(args.workspace)}")
    return 0


def cmd_score(args: "argparse.Namespace") -> int:
    cwd = args.workspace
    if not is_workspace(cwd):
        raise TeachError(1, f"not a teach workspace ({cwd})")
    notes = read_notes(cwd)
    ledger = parse_ledger_line(notes)
    if ledger is None:
        raise TeachError(1, "no open cold-open ledger line in NOTES.md")
    doubling, ceiling, _ = resolve_spacing(notes)
    if args.result.strip().lower() == "abandon":
        outcomes = [(i + 1, "abandon") for i in range(len(ledger["tests"]))]
    else:
        lesson_id, results = parse_result_line(args.result)
        ledger_id = os.path.splitext(os.path.basename(ledger["lesson"]))[0]
        if lesson_id is None:
            raise TeachError(
                1,
                "result line carries no lesson id — this workspace's "
                "assets/quiz.js predates template v3. Re-copy templates/quiz.js "
                "into assets/, rebuild the cold open, and ask for a fresh line.",
            )
        if lesson_id != ledger_id:
            raise TeachError(
                1,
                f'result line came from lesson "{lesson_id}" but the open ledger '
                f'tests "{ledger_id}" — scoring it would reschedule records the '
                f"learner never answered. Paste the line from {ledger['lesson']}.",
            )
        if len(results) != len(ledger["tests"]):
            raise TeachError(
                1,
                f"result has {len(results)} positions but ledger "
                f"tests {len(ledger['tests'])} records",
            )
        outcomes = results
    plan = []
    for pos, outcome in outcomes:
        rec = load_record(resolve_record_path(cwd, ledger["tests"][pos - 1]))
        plan.append(
            (rec, outcome, score_record(rec, outcome, doubling, ceiling))
        )
    write_text(os.path.join(cwd, "NOTES.md"), delete_ledger_line(notes))
    for rec, _, changed in plan:
        save_record(rec, changed)
    for rec, outcome, _ in plan:
        print(
            f"{os.path.basename(rec['path'])}: {outcome} -> "
            f"interval={rec['fm'].get('interval')} next={rec['fm'].get('next')} "
            f"lapses={rec['fm'].get('lapses')} status={rec['fm'].get('status', 'active')}"
        )
    try:
        print(f"index: {os.path.relpath(build_index(cwd), cwd)}")
    except TeachError as e:
        print(f"index: skipped ({e.msg})")
    return 0


def cmd_ledger(args: "argparse.Namespace") -> int:
    cwd = args.workspace
    lesson_path = args.lesson
    if not os.path.isabs(lesson_path):
        lesson_path = os.path.normpath(os.path.join(cwd, lesson_path))
    if not os.path.isfile(lesson_path):
        raise TeachError(2, f"lesson not found: {lesson_path}")
    notes = read_notes(cwd)
    if parse_ledger_line(notes) is not None:
        raise TeachError(
            1,
            "a cold-open ledger line is already open — score or "
            "abandon it first",
        )
    pairs = parse_cold_open_comment(read_text(lesson_path))
    tests = [rid for _, rid in sorted(pairs)]
    lesson_rel = os.path.relpath(lesson_path, cwd).replace(os.sep, "/")
    line = (
        f"- unscored cold open: {lesson_rel} "
        f"tests {', '.join(tests)} (asked: 0)"
    )
    write_text(os.path.join(cwd, "NOTES.md"), append_working_note(notes, line))
    print(f"ledger: {line}")
    try:
        print(f"index: {os.path.relpath(build_index(cwd), cwd)}")
    except TeachError as e:
        print(f"index: skipped ({e.msg})")
    return 0


def cmd_asked(args: "argparse.Namespace") -> int:
    cwd = args.workspace
    if not is_workspace(cwd):
        raise TeachError(1, f"not a teach workspace ({cwd})")
    notes = read_notes(cwd)
    ledger = parse_ledger_line(notes)
    if ledger is None:
        raise TeachError(1, "no open cold-open ledger line in NOTES.md")
    text, n = bump_asked(notes)
    write_text(os.path.join(cwd, "NOTES.md"), text)
    print(f"asked: {n}  {ledger['lesson']} tests {', '.join(ledger['tests'])}")
    if n >= 2:
        print(
            'abandon it now: teach.py score "abandon" — reschedules each '
            "record at its current interval, no credit and no lapse, and "
            "deletes the line"
        )
    try:
        print(f"index: {os.path.relpath(build_index(cwd), cwd)}")
    except TeachError as e:
        print(f"index: skipped ({e.msg})")
    return 0


def append_working_note(notes: str, line: str) -> str:
    """Append `line` under NOTES.md ## Working notes (create heading if missing)."""
    lines = notes.split("\n")
    # find ## Working notes
    idx = None
    for i, ln in enumerate(lines):
        if ln.strip().lower() == "## working notes":
            idx = i
            break
    if idx is None:
        if lines and lines[-1].strip() != "":
            lines.append("")
        lines.append("## Working notes")
        lines.append("")
        lines.append(line)
        return "\n".join(lines)
    # insert after heading + following blank line
    j = idx + 1
    if j < len(lines) and lines[j].strip() == "":
        j += 1
    lines.insert(j, line)
    return "\n".join(lines)


# --- entry ------------------------------------------------------------------
def main(argv: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(
        prog="teach.py", description="teach course runtime"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("state", help="print the workspace state report")
    sp.add_argument("--workspace", default=os.getcwd())
    sp.set_defaults(func=cmd_state)

    sc = sub.add_parser(
        "score", help="apply the scoring table to an open cold open"
    )
    sc.add_argument("result", help='result line verbatim, or "abandon"')
    sc.add_argument("--workspace", default=os.getcwd())
    sc.set_defaults(func=cmd_score)

    ld = sub.add_parser(
        "ledger", help="open a cold-open ledger line from a lesson"
    )
    ld.add_argument("lesson", help="lessons/NNNN-slug.html")
    ld.add_argument("--workspace", default=os.getcwd())
    ld.set_defaults(func=cmd_ledger)

    ak = sub.add_parser(
        "asked",
        help="record one unanswered request for the cold-open result line",
    )
    ak.add_argument("--workspace", default=os.getcwd())
    ak.set_defaults(func=cmd_asked)

    ix = sub.add_parser(
        "index", help="write the learner-facing course home page"
    )
    ix.add_argument("--workspace", default=os.getcwd())
    ix.set_defaults(func=cmd_index)

    args = p.parse_args(argv[1:])
    try:
        return args.func(args)
    except TeachError as e:
        print(f"teach: {e.msg}", file=sys.stderr)
        return e.code
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main(sys.argv))
