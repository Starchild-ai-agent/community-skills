# Disk Manager Cleanup Policy

Use this policy when proposing or executing cleanup actions.

## Safety Tiers

### Tier 1 — Safe to delete (default approve)
- `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`
- Python bytecode files (`*.pyc`, `*.pyo`)
- Build caches clearly marked as cache

### Tier 2 — Recreatable (ask first)
- `node_modules`
- `dist`, `build`, `.next`, `target`
- Package manager caches

### Tier 3 — Review required (never auto-delete)
- User documents in `output/`
- Database files (`*.db`, `*.sqlite`, dumps)
- Anything under `memory/`, `prompt/`, `tasks/`, `skills/`

## Recommended workflow
1. Run scanner and present findings by tier.
2. Default to dry-run cleanup first.
3. Execute only with explicit user confirmation.
4. Re-scan and show before/after bytes freed.
