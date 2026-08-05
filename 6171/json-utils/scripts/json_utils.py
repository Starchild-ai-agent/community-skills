#!/usr/bin/env python3
"""JSON Utils — format, validate, diff, convert, query, and beautify JSON."""

import argparse
import json
import os
import sys
from pathlib import Path


def cmd_format(input_path: str, indent: int = 2, sort_keys: bool = False, compact: bool = False, output: str = None):
    """Format/beautify JSON."""
    with open(input_path) as f:
        data = json.load(f)
    result = json.dumps(data, ensure_ascii=False, indent=None if compact else indent, sort_keys=sort_keys)
    if output:
        with open(output, "w") as f:
            f.write(result)
        return {"action": "format", "input": input_path, "output": output, "size_bytes": len(result)}
    return {"action": "format", "input": input_path, "output": "stdout", "content": result}


def cmd_validate(input_path: str):
    """Validate JSON file."""
    try:
        with open(input_path) as f:
            data = json.load(f)
        return {"valid": True, "type": type(data).__name__, "top_level_keys": len(data) if isinstance(data, dict) else None, "array_length": len(data) if isinstance(data, list) else None}
    except json.JSONDecodeError as e:
        return {"valid": False, "error": str(e), "line": e.lineno, "col": e.colno, "pos": e.pos}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def cmd_diff(path_a: str, path_b: str):
    """Deep compare two JSON files."""
    with open(path_a) as f:
        a = json.load(f)
    with open(path_b) as f:
        b = json.load(f)
    added, removed, changed = [], [], []
    _deep_diff(a, b, "", added, removed, changed)
    return {
        "file_a": os.path.basename(path_a),
        "file_b": os.path.basename(path_b),
        "equal": a == b,
        "added_keys": len(added),
        "removed_keys": len(removed),
        "changed_values": len(changed),
        "added": added[:20],
        "removed": removed[:20],
        "changed": changed[:20],
    }


def _deep_diff(a, b, path, added, removed, changed):
    if a == b:
        return
    if type(a) != type(b):
        changed.append({"path": path, "from": repr(type(a).__name__), "to": repr(type(b).__name__)})
        return
    if isinstance(a, dict):
        all_keys = set(a) | set(b)
        for k in all_keys:
            p = f"{path}.{k}" if path else k
            if k not in a:
                added.append(p)
            elif k not in b:
                removed.append(p)
            else:
                _deep_diff(a[k], b[k], p, added, removed, changed)
    elif isinstance(a, list):
        max_len = max(len(a), len(b))
        for i in range(max_len):
            p = f"{path}[{i}]"
            if i >= len(a):
                added.append(p)
            elif i >= len(b):
                removed.append(p)
            else:
                _deep_diff(a[i], b[i], p, added, removed, changed)
    else:
        if a != b:
            changed.append({"path": path, "from": str(a)[:100], "to": str(b)[:100]})


def cmd_convert(input_path: str, to_format: str, output: str = None):
    """Convert JSON to YAML or TOML (simplified)."""
    with open(input_path) as f:
        data = json.load(f)
    if to_format == "yaml":
        try:
            import yaml
            result = yaml.dump(data, default_flow_style=False, allow_unicode=True)
        except ImportError:
            return {"error": "PyYAML not installed. Run: pip install pyyaml"}
    elif to_format == "toml":
        try:
            import tomli_w
            result = tomli_w.dumps(data)
        except ImportError:
            return {"error": "tomli-w not installed. Run: pip install tomli-w"}
    elif to_format == "jsonl":
        if isinstance(data, list):
            result = "\n".join(json.dumps(item, ensure_ascii=False) for item in data)
        else:
            return {"error": "JSONL conversion requires a JSON array at top level"}
    else:
        return {"error": f"Unsupported format: {to_format}. Use: yaml, toml, jsonl"}
    if output:
        with open(output, "w") as f:
            f.write(result)
        return {"action": "convert", "from": "json", "to": to_format, "output": output}
    return {"action": "convert", "from": "json", "to": to_format, "content": result}


def cmd_query(input_path: str, key_path: str):
    """Query a JSON path expression (dot notation)."""
    with open(input_path) as f:
        data = json.load(f)
    keys = key_path.split(".")
    current = data
    for k in keys:
        try:
            if k.isdigit() and isinstance(current, list):
                current = current[int(k)]
            elif isinstance(current, dict):
                current = current[k]
            else:
                return {"error": f"Cannot traverse '{k}' on {type(current).__name__}"}
        except (KeyError, IndexError, TypeError) as e:
            return {"error": f"Path '{key_path}' not found: {e}"}
    return {"query": key_path, "result": current, "type": type(current).__name__}


def main():
    parser = argparse.ArgumentParser(description="JSON Utils")
    parser.add_argument("--action", required=True, choices=["format", "validate", "diff", "convert", "query"])
    parser.add_argument("--input", help="Input JSON file path")
    parser.add_argument("--input2", help="Second input (for diff)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--indent", type=int, default=2, help="Indent spaces (format)")
    parser.add_argument("--sort-keys", action="store_true", help="Sort keys (format)")
    parser.add_argument("--compact", action="store_true", help="Minify (format)")
    parser.add_argument("--to", choices=["yaml", "toml", "jsonl"], help="Target format (convert)")
    parser.add_argument("--query", help="Dot-notation key path (query)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = None
    try:
        if args.action == "format":
            if not args.input:
                raise ValueError("--input required")
            result = cmd_format(args.input, args.indent, args.sort_keys, args.compact, args.output)
        elif args.action == "validate":
            if not args.input:
                raise ValueError("--input required")
            result = cmd_validate(args.input)
        elif args.action == "diff":
            if not args.input or not args.input2:
                raise ValueError("--input and --input2 required")
            result = cmd_diff(args.input, args.input2)
        elif args.action == "convert":
            if not args.input or not args.to:
                raise ValueError("--input and --to required")
            result = cmd_convert(args.input, args.to, args.output)
        elif args.action == "query":
            if not args.input or not args.query:
                raise ValueError("--input and --query required")
            result = cmd_query(args.input, args.query)
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
        if action == "format":
            if "content" in data:
                print(data["content"])
            else:
                print(f"✅ Formatted → {data['output']} ({data['size_bytes']} bytes)")
        elif action == "validate":
            if data["valid"]:
                print(f"✅ Valid JSON! Type: {data['type']}")
                if data.get("top_level_keys") is not None:
                    print(f"   Top-level keys: {data['top_level_keys']}")
                if data.get("array_length") is not None:
                    print(f"   Array length: {data['array_length']}")
            else:
                print(f"❌ Invalid JSON: {data['error']}")
                print(f"   at line {data['line']}, col {data['col']}")
        elif action == "diff":
            if data["equal"]:
                print("✅ Files are identical")
            else:
                print(f"📊 Diff: {data['file_a']} ↔ {data['file_b']}")
                print(f"   Added: {data['added_keys']}")
                print(f"   Removed: {data['removed_keys']}")
                print(f"   Changed: {data['changed_values']}")
                if data["changed"]:
                    print("\n   Changed values (first 20):")
                    for c in data["changed"]:
                        print(f"     {c['path']}: {c['from']} → {c['to']}")
        elif action == "convert":
            if "content" in data:
                print(data["content"])
            else:
                print(f"✅ Converted → {data['output']}")
        elif action == "query":
            if isinstance(data["result"], (dict, list)):
                print(json.dumps(data["result"], ensure_ascii=False, indent=2))
            else:
                print(f"📌 {data['query']} = {data['result']}  ({data['type']})")


if __name__ == "__main__":
    main()