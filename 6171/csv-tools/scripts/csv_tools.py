#!/usr/bin/env python3
"""CSV Tools — view, filter, merge, convert, stats, clean CSV files."""

import argparse
import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path


def cmd_info(path: str, delimiter: str = ","):
    """Get CSV metadata: rows, columns, types."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
    if not rows:
        return {"rows": 0, "columns": 0, "headers": [], "file_size": os.path.getsize(path)}
    headers = list(rows[0].keys())
    return {
        "file": os.path.basename(path),
        "rows": len(rows),
        "columns": len(headers),
        "headers": headers,
        "file_size_bytes": os.path.getsize(path),
    }


def cmd_view(path: str, delimiter: str = ",", limit: int = 20, offset: int = 0):
    """View first N rows."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        all_rows = list(reader)
    headers = list(all_rows[0].keys()) if all_rows else []
    page = [dict(row) for row in all_rows[offset:offset + limit]]
    return {
        "total_rows": len(all_rows),
        "columns": len(headers),
        "headers": headers,
        "offset": offset,
        "limit": limit,
        "rows": page,
    }


def cmd_filter(path: str, delimiter: str = ",", column: str = None, value: str = None, output: str = None):
    """Filter rows by column value match."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
    if not column or not value:
        return {"error": "--column and --value required for filter"}
    filtered = [r for r in rows if column in r and value.lower() in r[column].lower()]
    if output:
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(filtered)
        return {"action": "filter", "input": path, "output": output, "total": len(rows), "matched": len(filtered)}
    return {"action": "filter", "total": len(rows), "matched": len(filtered), "rows": filtered[:50]}


def cmd_merge(inputs: list, delimiter: str = ",", output: str = None):
    """Merge multiple CSV files (same headers)."""
    all_rows = []
    headers = None
    for path in inputs:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)
            if headers is None:
                headers = list(rows[0].keys())
            all_rows.extend(rows)
    if not output:
        output = "output/merged.csv"
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_rows)
    return {"merged": len(inputs), "total_rows": len(all_rows), "output": output}


def cmd_stats(path: str, delimiter: str = ",", column: str = None):
    """Basic stats on a column."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
    if not rows:
        return {"error": "Empty CSV"}
    if not column:
        return {"error": "--column required for stats"}
    vals = [r.get(column, "") for r in rows if column in r]
    numeric = []
    for v in vals:
        try:
            numeric.append(float(v.replace(",", "").replace("$", "").replace("¥", "")))
        except (ValueError, AttributeError):
            pass
    result = {"column": column, "total_rows": len(rows), "non_empty": sum(1 for v in vals if v.strip())}
    if numeric:
        result.update({
            "type": "numeric",
            "count": len(numeric),
            "min": min(numeric),
            "max": max(numeric),
            "sum": sum(numeric),
            "avg": round(sum(numeric) / len(numeric), 4),
            "median": sorted(numeric)[len(numeric) // 2],
        })
    else:
        counter = Counter(vals)
        result.update({
            "type": "text",
            "unique_values": len(counter),
            "top_5": counter.most_common(5),
        })
    return result


def cmd_convert(path: str, delimiter: str = ",", to_format: str = "json", output: str = None):
    """Convert CSV to JSON or JSONL."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
    if to_format == "json":
        result = json.dumps(rows, ensure_ascii=False, indent=2)
    elif to_format == "jsonl":
        result = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    else:
        return {"error": f"Unsupported format: {to_format}"}
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        return {"action": "convert", "from": "csv", "to": to_format, "output": output, "rows": len(rows)}
    return {"action": "convert", "from": "csv", "to": to_format, "content": result}


def main():
    parser = argparse.ArgumentParser(description="CSV Tools")
    parser.add_argument("--action", required=True, choices=["info", "view", "filter", "merge", "stats", "convert"])
    parser.add_argument("--input", help="Input CSV file")
    parser.add_argument("--inputs", nargs="+", help="Multiple inputs (for merge)")
    parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: comma)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--limit", type=int, default=20, help="Rows to show (view)")
    parser.add_argument("--offset", type=int, default=0, help="Row offset (view)")
    parser.add_argument("--column", help="Column name (filter/stats)")
    parser.add_argument("--value", help="Filter value (filter)")
    parser.add_argument("--to", choices=["json", "jsonl"], help="Target format (convert)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = None
    try:
        if args.action == "info":
            if not args.input:
                raise ValueError("--input required")
            result = cmd_info(args.input, args.delimiter)
        elif args.action == "view":
            if not args.input:
                raise ValueError("--input required")
            result = cmd_view(args.input, args.delimiter, args.limit, args.offset)
        elif args.action == "filter":
            if not args.input:
                raise ValueError("--input required")
            result = cmd_filter(args.input, args.delimiter, args.column, args.value, args.output)
        elif args.action == "merge":
            if not args.inputs or len(args.inputs) < 2:
                raise ValueError("--inputs requires at least 2 files")
            result = cmd_merge(args.inputs, args.delimiter, args.output)
        elif args.action == "stats":
            if not args.input:
                raise ValueError("--input required")
            result = cmd_stats(args.input, args.delimiter, args.column)
        elif args.action == "convert":
            if not args.input or not args.to:
                raise ValueError("--input and --to required")
            result = cmd_convert(args.input, args.delimiter, args.to, args.output)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_human(result, args.action)


def _print_human(data, action):
    if isinstance(data, dict):
        if "error" in data:
            print(f"❌ {data['error']}")
            return
        if action == "info":
            print(f"📄 {data['file']}")
            print(f"   Rows: {data['rows']} | Columns: {data['columns']}")
            print(f"   Size: {data['file_size_bytes']:,} bytes")
            print(f"   Headers: {', '.join(data['headers'])}")
        elif action == "view":
            print(f"📊 Showing rows {data['offset']+1}-{min(data['offset']+data['limit'], data['total_rows'])} of {data['total_rows']}")
            print(f"   Columns: {', '.join(data['headers'])}")
            print()
            for row in data["rows"]:
                for k, v in row.items():
                    print(f"   {k}: {v[:80] if v else ''}")
                print()
        elif action == "filter":
            print(f"🔍 Filtered: {data['matched']} / {data['total']} rows matched")
            if "output" in data:
                print(f"   Saved to: {data['output']}")
            if "rows" in data:
                for r in data["rows"][:5]:
                    for k, v in r.items():
                        print(f"   {k}: {v[:80] if v else ''}")
                    print()
        elif action == "merge":
            print(f"📦 Merged {data['merged']} files → {data['output']}")
            print(f"   Total rows: {data['total_rows']}")
        elif action == "stats":
            print(f"📊 Stats for column '{data['column']}'")
            if data.get("type") == "numeric":
                print(f"   Type: Numeric ({data['count']} values)")
                print(f"   Min: {data['min']}  |  Max: {data['max']}")
                print(f"   Avg: {data['avg']}  |  Median: {data['median']}")
                print(f"   Sum: {data['sum']}")
            else:
                print(f"   Type: Text ({data['unique_values']} unique)")
                print(f"   Top 5: {data['top_5']}")
        elif action == "convert":
            if "content" in data:
                print(data["content"][:2000])
            else:
                print(f"✅ Converted → {data['output']} ({data['rows']} rows)")


if __name__ == "__main__":
    main()