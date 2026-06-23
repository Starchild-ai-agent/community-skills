# Decision Journal — JSONL Schema

## Entry object

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | `dj-YYYY-NNNN`, auto-generated |
| `ts` | ISO datetime | yes | UTC, when decision was logged |
| `title` | string | yes | Short label, ≤80 chars |
| `decision` | string | yes | What was chosen, one sentence |
| `reasoning` | string | yes | WHY, at time of decision. What you believed true. |
| `expected` | string | yes | Falsifiable outcome prediction. Refuse vague. |
| `review_on` | string | yes | ISO date `YYYY-MM-DD` OR trigger phrase ("next earnings") |
| `confidence` | int 1-5 | no | 1=low, 5=high. Used in stats to detect overconfidence. |
| `tags` | string[] | no | Consistent tags enable aggregation. e.g. `["investing","a-share"]` |
| `alternatives` | object | no | `{name: "why rejected"}`. Captures what else was on the table. |
| `invalidation` | string | no | Kill criterion. What would prove this wrong. |
| `status` | `open` \| `closed` | yes | Default `open` on add. Flips to `closed` on score. |
| `review` | object \| null | yes | `null` until scored. See below. |

## Review object (appended on score)

| Field | Type | Notes |
|---|---|---|
| `reviewed_ts` | ISO datetime | when scored |
| `actual` | string | what really happened — factual, not interpretive |
| `outcome` | `right` \| `wrong` \| `partial` \| `unresolved` | did reality match `expected`? |
| `reasoning_quality` | `good` \| `flawed` \| `mixed` | SEPARATE from outcome. See rubric below. |
| `notes` | string | the lesson. what prediction error reveals about mental model. |

## Scoring rubric — reasoning_quality

This is the core discipline. **Outcome and reasoning_quality are independent axes.**

| | Outcome right | Outcome wrong |
|---|---|---|
| **Reasoning good** | Skill (or skill + luck) — keep reasoning, results validate | Variance — reasoning was sound, outcome was unlucky. Don't change the process. |
| **Reasoning flawed** | Luck — good outcome from bad reasoning. Dangerous: reinforces wrong process. Flag explicitly. | Error — both reasoning and outcome were wrong. Clearest learning signal. |

- `good` — reasoning held up: risks identified were the right risks, the causal model matched reality, alternatives rejected for the right reasons.
- `flawed` — reasoning had holes: ignored a known risk, over-weighted single data point, motivated reasoning, confused correlation for causation.
- `mixed` — some right, some wrong. Specify in notes.

**Never** let outcome contaminate this score. A crash after a well-reasoned hold is `reasoning_quality: good, outcome: wrong` (variance). A moonshot after a reckless bet is `reasoning_quality: flawed, outcome: right` (luck). This separation is the entire point of the journal.

## Stats aggregation

`journal.py stats` computes:
- Count by outcome (right/wrong/partial/unresolved)
- Count by reasoning_quality (good/flawed/mixed)
- Cross-tab: outcome × reasoning_quality (the 2×2 above) — this is the real diagnostic
- Average confidence vs actual outcome rate — detects overconfidence (high confidence + low right rate)
- Most frequent tags among flawed-reasoning entries — where the user's blind spots cluster
- Common phrases in `notes` of flawed entries — recurring lessons

After 20+ scored entries, the cross-tab and tag analysis surface systematic patterns.
