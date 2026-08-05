---
name: "@6171/json-utils"
version: 1.0.0
description: |
  JSON format, validate, diff, query, and convert (YAML/TOML/JSONL). Use when the user needs to work with JSON files — beautify, minify, validate for errors, deep-compare two files, query by dot-notation path, or convert to/from YAML/TOML/JSONL.
metadata:
  starchild:
    emoji: "🔧"
    skillKey: json-utils
    requires:
      bins: [python3]
user-invocable: true
---

# JSON Utils

## Core Capabilities

| Action | Description | Command |
|--------|-------------|---------|
| **Format** | Beautify or minify JSON | `--action format --input file.json` |
| **Validate** | Check if JSON is valid | `--action validate --input file.json` |
| **Diff** | Deep-compare two JSON files | `--action diff --input a.json --input2 b.json` |
| **Convert** | Convert JSON → YAML/TOML/JSONL | `--action convert --input file.json --to yaml` |
| **Query** | Extract value by dot-notation path | `--action query --input file.json --query config.database.host` |

## Usage

```bash
# Format JSON
python3 skills/json-utils/scripts/json_utils.py --action format --input messy.json

# Minify (compact)
python3 skills/json-utils/scripts/json_utils.py --action format --input data.json --compact

# Validate
python3 skills/json-utils/scripts/json_utils.py --action validate --input data.json

# Diff two files
python3 skills/json-utils/scripts/json_utils.py --action diff --input old.json --input2 new.json

# Convert to YAML
python3 skills/json-utils/scripts/json_utils.py --action convert --input data.json --to yaml

# Query nested path
python3 skills/json-utils/scripts/json_utils.py --action query --input config.json --query app.database.host

# Save output to file
python3 skills/json-utils/scripts/json_utils.py --action format --input messy.json --output clean.json

# JSON output (for piping)
python3 skills/json-utils/scripts/json_utils.py --action validate --input data.json --json
```

## Examples

### Format
```bash
# Before: {"name":"tea","scores":[1,2,3]}
# After:
# {
#   "name": "tea",
#   "scores": [1, 2, 3]
# }
```

### Diff
```bash
$ python3 scripts/json_utils.py --action diff --input v1.json --input2 v2.json
📊 Diff: v1.json ↔ v2.json
   Added: 2
   Removed: 1
   Changed: 3
```

### Query
```bash
$ python3 scripts/json_utils.py --action query --input config.json --query database.host
📌 database.host = localhost  (str)
```

## Gotchas

- **Convert to YAML** requires `pyyaml` (`pip install pyyaml`)
- **Convert to TOML** requires `tomli-w` (`pip install tomli-w`)
- **JSONL convert** requires a top-level JSON array; each item becomes one line
- **Diff** returns first 20 items for each change type (added/removed/changed) — large files get truncated
- **Query** uses simple dot-notation only (no array wildcards like `[*]`). For array access use `items.0.name`