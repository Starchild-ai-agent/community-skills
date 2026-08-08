#!/usr/bin/env python3
"""Compare JSON or CSV snapshots by primary key."""
import argparse
import csv
import json
import sys
from pathlib import Path


def load(path):
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    if suffix == ".json":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("data", "records", "items"):
                if isinstance(data.get(key), list):
                    return data[key]
        raise ValueError("JSON input must be an array or contain a data/records/items array")
    raise ValueError("input extension must be .json or .csv")


def normalize(row):
    if not isinstance(row, dict):
        raise ValueError("each JSON record must be an object")
    return row


def main():
    p = argparse.ArgumentParser(description="Compare two JSON/CSV snapshots by key")
    p.add_argument("old")
    p.add_argument("new")
    p.add_argument("--key", required=True, help="primary-key field")
    p.add_argument("--fields", help="comma-separated fields to compare")
    p.add_argument("--fail-on-drift", action="store_true")
    args = p.parse_args()
    try:
        old_rows = [normalize(r) for r in load(args.old)]
        new_rows = [normalize(r) for r in load(args.new)]
        fields = [x.strip() for x in args.fields.split(",") if x.strip()] if args.fields else None
        def index(rows):
            out = {}
            for row in rows:
                if args.key not in row or row[args.key] in (None, ""):
                    raise ValueError(f"missing primary key: {args.key}")
                k = str(row[args.key])
                if k in out:
                    raise ValueError(f"duplicate primary key: {k}")
                out[k] = row
            return out
        before, after = index(old_rows), index(new_rows)
        added = [{"key": k, "record": after[k]} for k in sorted(set(after) - set(before))]
        removed = [{"key": k, "record": before[k]} for k in sorted(set(before) - set(after))]
        changed = []
        for k in sorted(set(before) & set(after)):
            names = fields or sorted(set(before[k]) | set(after[k]))
            diffs = {}
            for name in names:
                if name == args.key:
                    continue
                if before[k].get(name) != after[k].get(name):
                    diffs[name] = {"before": before[k].get(name), "after": after[k].get(name)}
            if diffs:
                changed.append({"key": k, "fields": diffs})
        result = {"summary": {"old_count": len(before), "new_count": len(after), "added": len(added), "removed": len(removed), "changed": len(changed), "has_drift": bool(added or removed or changed)}, "added": added, "removed": removed, "changed": changed}
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 2 if args.fail_on_drift and result["summary"]["has_drift"] else 0
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
