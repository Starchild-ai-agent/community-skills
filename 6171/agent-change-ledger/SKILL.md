---
name: "@6171/agent-change-ledger"
version: 1.0.0
description: >-
  Build an auditable evidence ledger for AI-assisted code changes: capture change
  intent, affected files, validation commands, review gates, rollback notes, and
  machine-readable release evidence from a diff or work session.
author: starchild
tags: [agents, software-engineering, audit, change-management, developer-tools]
delivery: prompt
metadata:
  starchild:
    emoji: "🧾"
    skillKey: agent-change-ledger
---

# Agent Change Ledger

Use this skill when an AI agent changes code and the result needs to be explainable,
reviewable, and easy to roll back. The output is an evidence-first change record,
not a generic code review.

## Inputs

Accept any subset of:

- repository path or patch/diff
- change request or issue text
- files changed and their intended impact
- commands already run and their outputs
- test, lint, type-check, build, or deployment results
- reviewer identity and approval status
- rollback or revert procedure

Never request or record secrets, tokens, passwords, private keys, or full contents
of environment files. Redact them as `[REDACTED]`.

## Workflow

1. **State the intent** in one sentence and list explicit acceptance criteria.
2. **Inventory the delta**: files added, modified, deleted, generated artifacts,
   schema/config changes, and public API changes. Distinguish observed facts from
   claims.
3. **Map risk** for each affected area: data loss, security, compatibility,
   performance, operational, and migration risk. Mark unknowns explicitly.
4. **Build the validation matrix** with command, scope, result, timestamp if known,
   and evidence location. Never mark a check passed without output or a trusted
   CI result.
5. **Apply review gates**: required reviewer, unresolved comments, dependency or
   migration approval, and deployment gate. A missing gate is `BLOCKED`, not
   `PASS`.
6. **Record rollback**: exact revert action, stateful-data caveats, and the signal
   that should trigger rollback.
7. **Emit the ledger** in the format below and calculate the final status:
   `READY`, `BLOCKED`, or `NEEDS-EVIDENCE`.

## Output format

```yaml
ledger_version: 1
change:
  intent: "..."
  acceptance_criteria: []
  scope:
    added: []
    modified: []
    deleted: []
    public_interfaces: []
risk_register:
  - area: security|data|compatibility|performance|operations|migration
    level: low|medium|high|unknown
    finding: "..."
    mitigation: "..."
validation:
  - command: "..."
    result: pass|fail|not_run|unknown
    evidence: "..."
review_gates:
  - gate: "..."
    status: pass|blocked|not_applicable|unknown
    owner: "..."
rollback:
  action: "..."
  caveats: []
  trigger: "..."
final_status: READY|BLOCKED|NEEDS-EVIDENCE
open_questions: []
```

## Rules

- Prefer raw evidence and exact commands over prose assurances.
- Treat missing tests, missing review, and missing rollback details as explicit
  gaps. Do not silently infer success.
- Keep the ledger small enough to review in one sitting; link to large logs rather
  than embedding them.
- If the input is only a diff, produce `NEEDS-EVIDENCE` until validation and
  rollback information are supplied.
- Do not modify the repository unless the user separately asks for implementation.
