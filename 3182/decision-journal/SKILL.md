---
name: "@3182/decision-journal"
version: 1.0.0
description: |
  Log non-trivial decisions with reasoning, expected outcome, and a review date — then later score what actually happened vs what you predicted. Use when the user makes a consequential call (buy/sell, strategy pivot, hire, commit-or-kill) and wants to capture it before hindsight bias rewrites memory. Surfaces prediction errors over time so the user actually learns from them.

  Distinct from `memory` (declarative facts) — this is structured decision tracking with review triggers and outcome scoring.
delivery: script
metadata:
  starchild:
    emoji: 🧭
    skillKey: decision-journal
user-invocable: true
disable-model-invocation: false
---

## Why this exists

Hindsight bias rewrites memory. "I knew it was risky" feels true after the loss, but you didn't write it down. A decision journal forces you to commit your reasoning to paper **before** the outcome is known, then scores how well your predictions matched reality — so the user learns from prediction errors, not just outcomes.

Good outcomes from bad reasoning = luck. Bad outcomes from good reasoning = variance. You can only tell the difference if the reasoning was captured beforehand.

## When to use

- User says "I'm deciding whether to..." on something consequential
- User commits to a position / pivot / hire / kill decision
- User reviews a past decision ("what did I think when I bought X?")
- User asks "what was my reasoning on..."
- A scheduled review fires (see Review loop below)

Do NOT use for: trivial preferences ("should I use tabs or spaces"), routine execution, or things the user has already decided and is just executing. Only log decisions where the reasoning itself has learning value.

## The four fields that matter

Every entry captures these, no exceptions:

1. **The decision** — what you chose, in one sentence. Not the options considered, the choice made.
2. **The reasoning** — WHY, at the time. What you believed to be true. What would have to be true for this to be wrong. This is the whole point — capture it before the outcome.
3. **Expected outcome** — concrete and falsifiable. "Up 20% in 6 months" not "should do well." If you can't state a falsifiable expectation, the decision isn't logged — it's too vague to learn from.
4. **Review date / trigger** — when to come back and score. Date-based ("2026-09-01") or event-based ("next earnings call", "if price hits $X").

Optional but valuable: **confidence** (1-5), **alternatives rejected** (one-liner each, with why), **what would invalidate this** (the kill criterion).

## Workflow

### Logging a decision

```python
from core.skill_tools import decision_journal_add
# or via bash:
# python3 skills/decision-journal/scripts/journal.py add ...
```

Fields: `title`, `decision`, `reasoning`, `expected`, `review_on` (ISO date or trigger phrase), `confidence` (1-5), `tags` (list), `alternatives` (dict of name→reason rejected), `invalidation` (string).

Returns the entry ID. Entries are stored in `workspace/data/decision-journal.jsonl` (append-only, one JSON object per line).

### Reviewing — the part that actually teaches

Two modes:

**Date-triggered review** — entries with `review_on` ≤ today and `status=open` are due. Run:
```bash
python3 skills/decision-journal/scripts/journal.py due
```
Returns due entries. For each, the agent prompts the user: "What actually happened?" then scores it.

**Manual review** — user asks "review my decision on X":
```bash
python3 skills/decision-journal/scripts/journal.py find --query "X"
```

### Scoring an outcome

```bash
python3 skills/decision-journal/scripts/journal.py score --id <entry_id> \
  --actual "what happened" --outcome right|wrong|partial|unresolved \
  --notes "what the gap teaches"
```

The score captures:
- `actual` — what really happened (factual, not interpretive)
- `outcome` — right / wrong / partial / unresolved (did reality match expectation?)
- `reasoning_quality` — separate from outcome! Good reasoning + bad outcome = variance, not error. Bad reasoning + good outcome = luck, not skill. The agent should score reasoning_quality honestly, not let the outcome contaminate it.
- `notes` — the lesson. What did the prediction error reveal about the user's mental model?

**Critical scoring discipline:** never let outcome contaminate reasoning_quality. A decision to hold a stock that then crashed isn't automatically bad reasoning — only mark reasoning_quality low if the reasoning itself was flawed (ignored a known risk, over-weighted a single data point, etc.). This separation is the whole point of the journal.

## Review loop (scheduled)

Optionally wire date-triggered reviews into `scheduled_task` so due entries surface automatically:

```python
# Register a daily check that pushes due decisions to the user
scheduled_task(
    action="register",
    title="Decision journal review",
    schedule="0 9 * * *",  # 9 AM UTC daily
    # run.py calls: python3 skills/decision-journal/scripts/journal.py due
    # if any due: push summary to user via /push
)
```

The run.py should: call `due`, if empty exit silently (no push), if non-empty push a summary listing each due decision's title + expected outcome + a prompt to score it.

This is optional — the journal works fine with manual review. But the scheduled loop is what turns it from a diary into a learning system.

## Reading patterns

- `journal.py list --status open` — all unresolved decisions
- `journal.py list --tag investing` — filter by tag
- `journal.py stats` — aggregate: how many right/wrong/partial, average confidence, most common prediction errors (from `notes` field across scored entries)
- `journal.py find --query "keyword"` — full-text search across decisions + reasoning + actual outcomes

The `stats` command is where the meta-learning lives. After 20+ scored entries, patterns emerge: "I'm consistently overconfident on X type of decision" or "my reasoning is good but my timing is off." That's the gold.

## Storage

`workspace/data/decision-journal.jsonl` — append-only JSONL. One object per line. Never edit historical entries in place; scoring adds a `review` block to the same entry (so the original reasoning is preserved exactly as written, even if it was wrong).

Schema (see `references/schema.md` for full):
```json
{
  "id": "dj-2026-0142",
  "ts": "2026-06-23T14:30:00Z",
  "title": "Hold ZG despite PE 168",
  "decision": "Keep position, no add",
  "reasoning": "PE high but growth story intact, sector momentum...",
  "expected": "Flat to +10% over 3 months, no >15% drawdown",
  "review_on": "2026-09-23",
  "confidence": 3,
  "tags": ["investing", "a-share"],
  "alternatives": {"sell_all": "tax event + timing risk"},
  "invalidation": "Q2 miss or sector break MA60",
  "status": "open",
  "review": null
}
```

After scoring, `review` fills in and `status` flips to `closed`.

## Behavioral rules

- **Capture before outcome.** If the user is describing a decision already made and resolved, logging it has limited value — the reasoning is already contaminated by knowing how it went. Still log if asked, but flag it.
- **Falsifiable expectations only.** Refuse vague expectations ("should do well"). Push back: "What specifically would confirm or falsify this?"
- **Separate outcome from reasoning quality.** This is non-negotiable. See scoring discipline above.
- **Don't log routine execution.** "I decided to rebalance today" is not a decision worth journaling. The journal is for non-obvious calls with learning value.
- **Never rewrite history.** Original reasoning is immutable. Scoring appends, never edits.
- **Tags are how patterns surface.** Encourage consistent tags (`investing`, `hiring`, `strategy`, `kill-decision`) so `stats` can aggregate.

## References

- `references/schema.md` — full JSONL schema, field semantics, scoring rubric
- `scripts/journal.py` — CLI: `add`, `due`, `find`, `list`, `score`, `stats`
