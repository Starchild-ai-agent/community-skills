---
name: "@1892/disk-manager"
description: Intelligent disk space management for workspace environments. Analyze storage by safety tier, run dry-run cleanup, remove safe cache artifacts, and archive old projects with dependency exclusion. Use when the user asks to free disk space, clean workspace clutter, or automate cleanup policies.
version: 1.2.0

metadata:
  starchild:
    emoji: "🧹"
    skillKey: disk-manager

user-invocable: true
---

# Disk Manager

You manage workspace disk space with an opinionated, safety-first workflow that prioritizes reclaiming space without risking user data.

## What this skill is for

Use this skill when the user asks to:
- check disk usage,
- clean up storage,
- remove caches/build artifacts,
- archive inactive projects,
- or automate recurring cleanup policies.

## Safety model (always follow)

Classify findings into three tiers and present results this way:

1. **Safe to delete** — caches and bytecode (`__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `*.pyc`)
2. **Recreatable** — dependencies/build outputs (`node_modules`, `dist`, `build`, `.next`, `target`)
3. **Review needed** — anything user-authored or potentially irreplaceable

Never delete Tier 2 or Tier 3 without explicit confirmation.

## Core workflow

1. **Scan first**
   - Run `scripts/scan_workspace.py` to generate categorized opportunities.
2. **Show dry-run impact**
   - Run `scripts/safe_cleanup.py --dry-run` so the user sees estimated reclaimed bytes.
3. **Execute approved cleanup**
   - For safe cleanup, run `scripts/safe_cleanup.py`.
   - For project archival, run `scripts/archive_project.py --project <name>`.
4. **Verify after action**
   - Re-run scanner and report before/after reclaimed space.

## Commands

### 1) Full workspace scan
```bash
python3 skills/disk-manager/scripts/scan_workspace.py
```
(Use `--json` for machine output)

### 2) Dry-run safe cleanup
```bash
python3 skills/disk-manager/scripts/safe_cleanup.py --dry-run
```
(Use `--json` for machine output)

### 3) Execute safe cleanup
```bash
python3 skills/disk-manager/scripts/safe_cleanup.py
```
(Use `--json` for machine output)

### 4) Archive inactive project
```bash
python3 skills/disk-manager/scripts/archive_project.py --project my-project
```

## Reporting format

When reporting to the user, always include:
- total workspace bytes scanned,
- bytes reclaimable by tier,
- exact paths for top heavy items,
- estimated freed bytes (dry-run) or verified freed bytes (post-cleanup).

Keep outputs concise and actionable, and always separate recommendation from executed actions.

## References

See `references/cleanup-policy.md` for tiering and guardrails.
