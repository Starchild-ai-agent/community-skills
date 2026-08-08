---
name: "@6171/drift-detector"
version: 1.0.0
description: Compare two JSON or CSV snapshots by primary key and report added, removed, and changed records. Use for billing reconciliation, external-system sync checks, data quality audits, and scheduled drift monitoring.
author: starchild
tags: [reconciliation, drift-detection, json, csv, data-quality, monitoring]
delivery: script
metadata:
  starchild:
    emoji: "🔎"
    skillKey: drift-detector
    requires:
      env: []
      bins: [python3]
user-invocable: true
disable-model-invocation: false
---

# Drift Detector

Use `scripts/drift.py` to compare a local snapshot with an external or previous snapshot without requiring third-party packages. It supports JSON arrays/objects and CSV files, aligns rows by a required primary-key column/field, and emits machine-readable JSON.

## Run

```bash
python3 scripts/drift.py old.json new.json --key id
python3 scripts/drift.py old.csv new.csv --key customer_id --fields plan,status
python3 scripts/drift.py old.json new.json --key id --fail-on-drift
```

Use `--fields` to limit comparisons. Nested JSON values are compared as JSON values. Missing records are classified as `added` or `removed`; matching records with field differences appear under `changed` with a field-level `before`/`after` map.

## Output and exit codes

Output is a single JSON document containing `summary`, `added`, `removed`, and `changed`. `summary.has_drift` is true when any difference exists. The default exit code is 0 even when drift is found, which is convenient for reports. With `--fail-on-drift`, exit code 2 indicates drift and exit code 0 indicates no drift; malformed input or invalid arguments exit 1.

For scheduled reconciliation, persist the prior report and alert only when `summary.has_drift` changes or remains actionable. Treat a clean local webhook-derived snapshot as advisory until reconciled against the authoritative source.

## Constraints

- Inputs must be JSON or CSV and use the same format/compatible fields.
- Keys must be unique and present in every row; duplicates and missing keys are errors.
- The tool reads files only and never calls external services or modifies inputs.
