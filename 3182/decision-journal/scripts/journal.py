#!/usr/bin/env python3
"""
Decision Journal CLI.
Storage: workspace/data/decision-journal.jsonl (append-only JSONL, one object per line).

Commands:
  add       — log a new decision
  due       — list open entries with review_on <= today
  find      — full-text search across title/decision/reasoning/expected/actual
  list      -- filter by status/tag
  score     -- append a review block to an entry, flip status to closed
  stats     -- aggregate outcome x reasoning_quality cross-tab + tag analysis

Usage:
  python3 journal.py add --title "..." --decision "..." --reasoning "..." \
      --expected "..." --review-on 2026-09-01 [--confidence 3] [--tags investing,a-share] \
      [--alt sell_all="tax event" --alt hold="no conviction"] [--invalidation "..."]
  python3 journal.py due
  python3 journal.py find --query "keyword"
  python3 journal.py list [--status open|closed] [--tag investing]
  python3 journal.py score --id dj-2026-0142 --actual "..." --outcome right|wrong|partial|unresolved \
      --reasoning-quality good|flawed|mixed --notes "..."
  python3 journal.py stats
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

WORKSPACE = os.environ.get("WORKSPACE", "/data/workspace")
JOURNAL_PATH = os.path.join(WORKSPACE, "data", "decision-journal.jsonl")

VALID_OUTCOMES = {"right", "wrong", "partial", "unresolved"}
VALID_RQ = {"good", "flawed", "mixed"}


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _next_id():
    year = datetime.now(timezone.utc).strftime("%Y")
    existing = _read_all()
    n = len([e for e in existing if e.get("id", "").startswith(f"dj-{year}-")]) + 1
    return f"dj-{year}-{n:04d}"


def _read_all():
    if not os.path.exists(JOURNAL_PATH):
        return []
    entries = []
    with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                # skip corrupt line rather than crash
                continue
    return entries


def _write_all(entries):
    os.makedirs(os.path.dirname(JOURNAL_PATH), exist_ok=True)
    with open(JOURNAL_PATH, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def _append(entry):
    os.makedirs(os.path.dirname(JOURNAL_PATH), exist_ok=True)
    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def cmd_add(args):
    if not all([args.title, args.decision, args.reasoning, args.expected, args.review_on]):
        print("ERROR: --title --decision --reasoning --expected --review-on are all required", file=sys.stderr)
        return 2

    # Refuse vague expectations — push back so the entry has learning value.
    vague_markers = ("should do well", "will probably", "likely fine", "good chance", "hopefully")
    if any(m in args.expected.lower() for m in vague_markers) and not args.force:
        print(f'ERROR: --expected looks vague ("{args.expected}"). A decision journal only teaches '
              "if the expectation is falsifiable. State what specifically would confirm or falsify "
              "this, or re-run with --force to log anyway.", file=sys.stderr)
        return 2

    alts = {}
    if args.alt:
        for pair in args.alt:
            if "=" not in pair:
                print(f'ERROR: --alt must be name="reason", got: {pair}', file=sys.stderr)
                return 2
            name, reason = pair.split("=", 1)
            alts[name.strip()] = reason.strip()

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    entry = {
        "id": _next_id(),
        "ts": _now_iso(),
        "title": args.title,
        "decision": args.decision,
        "reasoning": args.reasoning,
        "expected": args.expected,
        "review_on": args.review_on,
        "confidence": args.confidence,
        "tags": tags,
        "alternatives": alts,
        "invalidation": args.invalidation or "",
        "status": "open",
        "review": None,
    }
    _append(entry)
    print(json.dumps({"ok": True, "id": entry["id"], "path": JOURNAL_PATH}, ensure_ascii=False, indent=2))
    return 0


def cmd_due(args):
    today = _today()
    due = []
    for e in _read_all():
        if e.get("status") != "open":
            continue
        ro = e.get("review_on", "")
        # only date-form triggers count as "due"; phrase triggers need manual review
        if re.match(r"^\d{4}-\d{2}-\d{2}$", ro) and ro <= today:
            due.append(e)
    print(json.dumps({"count": len(due), "due": due}, ensure_ascii=False, indent=2))
    return 0


def cmd_find(args):
    q = (args.query or "").lower()
    if not q:
        print("ERROR: --query required", file=sys.stderr)
        return 2
    hits = []
    for e in _read_all():
        haystack = " ".join([
            e.get("title", ""), e.get("decision", ""), e.get("reasoning", ""),
            e.get("expected", ""),
            (e.get("review") or {}).get("actual", ""),
            (e.get("review") or {}).get("notes", ""),
        ]).lower()
        if q in haystack:
            hits.append(e)
    print(json.dumps({"count": len(hits), "results": hits}, ensure_ascii=False, indent=2))
    return 0


def cmd_list(args):
    entries = _read_all()
    if args.status:
        entries = [e for e in entries if e.get("status") == args.status]
    if args.tag:
        entries = [e for e in entries if args.tag in (e.get("tags") or [])]
    print(json.dumps({"count": len(entries), "entries": entries}, ensure_ascii=False, indent=2))
    return 0


def cmd_score(args):
    if not all([args.id, args.actual, args.outcome, args.reasoning_quality]):
        print("ERROR: --id --actual --outcome --reasoning-quality are required", file=sys.stderr)
        return 2
    if args.outcome not in VALID_OUTCOMES:
        print(f"ERROR: --outcome must be one of {VALID_OUTCOMES}", file=sys.stderr)
        return 2
    if args.reasoning_quality not in VALID_RQ:
        print(f"ERROR: --reasoning-quality must be one of {VALID_RQ}", file=sys.stderr)
        return 2

    entries = _read_all()
    target = None
    for e in entries:
        if e.get("id") == args.id:
            target = e
            break
    if target is None:
        print(f'ERROR: no entry with id "{args.id}"', file=sys.stderr)
        return 2
    if target.get("status") == "closed" and not args.force:
        print(f'ERROR: entry {args.id} is already closed. Use --force to re-score.', file=sys.stderr)
        return 2

    target["review"] = {
        "reviewed_ts": _now_iso(),
        "actual": args.actual,
        "outcome": args.outcome,
        "reasoning_quality": args.reasoning_quality,
        "notes": args.notes or "",
    }
    target["status"] = "closed"
    _write_all(entries)
    print(json.dumps({"ok": True, "id": target["id"], "status": target["status"]}, ensure_ascii=False, indent=2))
    return 0


def cmd_stats(args):
    entries = _read_all()
    scored = [e for e in entries if e.get("review")]
    total = len(scored)
    if total == 0:
        print(json.dumps({"total_scored": 0, "note": "No scored entries yet."}, ensure_ascii=False, indent=2))
        return 0

    outcome_counts = Counter(r["outcome"] for r in (e["review"] for e in scored))
    rq_counts = Counter(r["reasoning_quality"] for r in (e["review"] for e in scored))

    # 2x2 cross-tab — the real diagnostic
    cross = defaultdict(int)
    for e in scored:
        r = e["review"]
        cross[(r["outcome"], r["reasoning_quality"])] += 1

    # confidence vs outcome — overconfidence detector
    conf_buckets = defaultdict(lambda: {"total": 0, "right": 0})
    for e in scored:
        c = e.get("confidence")
        if c is None:
            continue
        b = conf_buckets[c]
        b["total"] += 1
        if e["review"]["outcome"] == "right":
            b["right"] += 1

    # tag analysis on flawed reasoning — where blind spots cluster
    flawed_tags = Counter()
    for e in scored:
        if e["review"]["reasoning_quality"] == "flawed":
            for t in (e.get("tags") or []):
                flawed_tags[t] += 1

    print(json.dumps({
        "total_logged": len(entries),
        "total_scored": total,
        "open": len([e for e in entries if e.get("status") == "open"]),
        "by_outcome": dict(outcome_counts),
        "by_reasoning_quality": dict(rq_counts),
        "cross_tab_outcome_x_reasoning": {
            f"{o}|{rq}": cross[(o, rq)] for o in VALID_OUTCOMES for rq in VALID_RQ
        },
        "confidence_vs_right_rate": {str(k): v for k, v in sorted(conf_buckets.items())},
        "flawed_reasoning_top_tags": flawed_tags.most_common(5),
    }, ensure_ascii=False, indent=2))
    return 0


def main():
    p = argparse.ArgumentParser(description="Decision journal CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="log a new decision")
    a.add_argument("--title", required=True)
    a.add_argument("--decision", required=True)
    a.add_argument("--reasoning", required=True)
    a.add_argument("--expected", required=True)
    a.add_argument("--review-on", required=True, dest="review_on")
    a.add_argument("--confidence", type=int, choices=[1, 2, 3, 4, 5])
    a.add_argument("--tags")
    a.add_argument("--alt", action="append", help='name="reason rejected"')
    a.add_argument("--invalidation")
    a.add_argument("--force", action="store_true", help="allow vague expected")
    a.set_defaults(func=cmd_add)

    d = sub.add_parser("due", help="list open entries due for review")
    d.set_defaults(func=cmd_due)

    f = sub.add_parser("find", help="full-text search")
    f.add_argument("--query", required=True)
    f.set_defaults(func=cmd_find)

    l = sub.add_parser("list", help="list entries")
    l.add_argument("--status", choices=["open", "closed"])
    l.add_argument("--tag")
    l.set_defaults(func=cmd_list)

    s = sub.add_parser("score", help="score an entry's outcome")
    s.add_argument("--id", required=True)
    s.add_argument("--actual", required=True)
    s.add_argument("--outcome", required=True, choices=list(VALID_OUTCOMES))
    s.add_argument("--reasoning-quality", required=True, dest="reasoning_quality", choices=list(VALID_RQ))
    s.add_argument("--notes")
    s.add_argument("--force", action="store_true", help="re-score a closed entry")
    s.set_defaults(func=cmd_score)

    st = sub.add_parser("stats", help="aggregate stats")
    st.set_defaults(func=cmd_stats)

    args = p.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
