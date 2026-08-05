---
name: "@6171/csv-tools"
version: 1.0.0
description: |
  View, filter, merge, convert, and analyze CSV files. Use when the user needs to work with CSV data — inspect structure, filter rows, merge files, compute stats, or convert to JSON/JSONL.
metadata:
  starchild:
    emoji: "📊"
    skillKey: csv-tools
    requires:
      bins: [python3]
user-invocable: true
---

# CSV Tools

## Core Capabilities

| Action | Description | Command |
|--------|-------------|---------|
| **Info** | Get row count, columns, headers, file size | `--action info --input file.csv` |
| **View** | Preview rows with pagination | `--action view --input file.csv --limit 10` |
| **Filter** | Filter rows by column value | `--action filter --input file.csv --column City --value "Beijing"` |
| **Merge** | Combine multiple CSV files | `--action merge --inputs a.csv b.csv --output merged.csv` |
| **Stats** | Column statistics (numeric or text) | `--action stats --input file.csv --column Price` |
| **Convert** | CSV → JSON or JSONL | `--action convert --input file.csv --to json` |

## Usage

```bash
# Quick info
python3 skills/csv-tools/scripts/csv_tools.py --action info --input data.csv

# View first 10 rows
python3 skills/csv-tools/scripts/csv_tools.py --action view --input data.csv --limit 10

# Filter rows
python3 skills/csv-tools/scripts/csv_tools.py --action filter --input data.csv --column City --value "Beijing" --output filtered.csv

# Merge two CSVs
python3 skills/csv-tools/scripts/csv_tools.py --action merge --inputs a.csv b.csv --output combined.csv

# Column stats
python3 skills/csv-tools/scripts/csv_tools.py --action stats --input sales.csv --column Revenue

# Convert to JSON
python3 skills/csv-tools/scripts/csv_tools.py --action convert --input data.csv --to json --output data.json

# Handle TSV (tab-separated)
python3 skills/csv-tools/scripts/csv_tools.py --action info --input data.tsv --delimiter $'\t'
```

## Gotchas

- **Encoding**: auto-detects UTF-8 BOM. For other encodings, convert first.
- **Large files**: `view --limit` and `filter` with output are safe for large files (streaming). `stats` loads all rows.
- **Merge** requires same column headers across all files.
- **Stats numeric** auto-detects by trying to parse numbers (strips `$`, `,`, `¥`).
- **TSV files**: use `--delimiter $'\t'`