---
name: "@554/better-skill-creator"
version: 1.0.0
description: "Create high-quality skills that reliably trigger, complete workflows cleanly, and work well with other skills. Use when the user asks to build a new capability, integrate a new API, or extend the system with a repeatable workflow. Improvement on the default skill-creator with use-case design, behavioral testing, and success criteria."

author: starchild
tags: [meta, skill, tooling, development]

metadata:
  starchild:
    emoji: "🛠️"
    skillKey: better-skill-creator

user-invocable: true
---

# Better Skill Creator

You build skills that actually work — not just valid YAML, but skills that trigger reliably, complete their workflows without hand-holding, and compose well with other skills.

The fundamental insight from Anthropic's skill design guide: **the description is the skill's interface to the agent**. A skill that doesn't trigger is a skill that doesn't exist. A skill that triggers for the wrong things causes confusion. Get the description right first — everything else follows.

---

## Phase 0: Use-Case Canvas (Do This Before Scaffolding)

Before writing a single line of SKILL.md, fill out this canvas. It forces clarity about what the skill actually does and prevents writing instructions for a skill that was never well-defined.

```
Skill Name: _______________

Use Case 1: _______________
  Trigger phrase: "..."
  Steps: 1. → 2. → 3.
  Expected output: _______________

Use Case 2: _______________
  Trigger phrase: "..."
  Steps: 1. → 2. → 3.
  Expected output: _______________

Dependencies:
  - API keys needed: _______________
  - Python packages: _______________
  - External services: _______________

Success looks like:
  - Agent triggers on ___% of relevant queries
  - User doesn't need to re-prompt to get _______________
  - Works independently when combined with: _______________
```

If you can't fill in at least 2 use cases with concrete trigger phrases, the skill isn't ready to build yet. Ask the user to clarify.

---

## Phase 1: Understand the Request

- **What capability?** API integration, workflow automation, knowledge domain, meta-tool?
- **What triggers it?** Map the exact phrases a user would say. This becomes the description.
- **What freedom level?** Can the agent improvise the steps, or must they be exact?
  - High freedom → natural language guidance in body
  - Medium freedom → pseudocode + key params
  - Low freedom → scripts in `scripts/` executed via bash
- **What does success look like?** Define this now, before you build — see Phase 4.

---

## Phase 2: Scaffold

```bash
python skills/skill-creator/scripts/init_skill.py my-new-skill --path ./skills
```

With resource directories:
```bash
python skills/skill-creator/scripts/init_skill.py api-helper --path ./skills --resources scripts,references
```

---

## Phase 3: Write the SKILL.md

### 3a. Craft the Description (Most Important)

The description is the **only** part of your skill that's always in context. It's what the agent reads to decide whether to activate the skill. Two requirements:

1. **What it does** — one clause
2. **When to trigger** — specific scenarios, not vague categories

Formula: `[What it does] + [Use when <specific trigger conditions>]`

**Examples:**
```
# Too vague — agent won't know when to use this
"Trading utilities and market analysis tools."

# Good — clear what/when
"Fetch live and historical crypto prices, on-chain metrics, and sentiment
scores. Use when the user asks about price, volume, market cap, trend, or
wants data to support a trade thesis."

# Good — multi-scenario trigger
"Generate TradingView-style candlestick charts with indicators. Use when
the user wants a visual chart, price visualization, or technical analysis
plot."
```

**Hard limits:**
- Max 1024 characters
- No XML tags `< >` — they break the skill loader
- Do not name the skill `claude`, `anthropic`, or any Anthropic product name

**Trigger failure modes:**
- Skill never activates → description too vague or missing "Use when"
- Skill activates for unrelated requests → description too broad
- Skill competes with another skill → descriptions overlap; narrow the trigger

### 3b. Frontmatter Template

```yaml
---
name: skill-name            # lowercase, alphanumeric + hyphens, 2-64 chars
version: 1.0.0              # semver — required for market publishing
description: "..."          # trigger text — see formula above
author: your-name           # for market publishing
tags: [tag1, tag2]          # for discoverability

metadata:
  starchild:
    emoji: "🔧"
    skillKey: skill-name
    requires:
      env: [API_KEY_NAME]   # env vars that must be set
      bins: [python3]       # binaries that must ALL exist
      anyBins: [curl, wget] # binaries where ANY ONE is sufficient
    install:
      - kind: pip
        package: pandas
      - kind: apt
        package: curl
        bins: [curl]

user-invocable: true
---
```

| Field | Required | Notes |
|-------|----------|-------|
| `name` | ✅ | lowercase hyphen-case, 2-64 chars |
| `version` | ✅ for publishing | semver, immutable once published |
| `description` | ✅ | trigger text — this is the skill's interface |
| `author` | for publishing | your name |
| `tags` | for publishing | array of strings |
| `emoji` | no | display in skill list |
| `requires.env` | no | fails gracefully if missing |
| `requires.bins` | no | ALL must exist |
| `requires.anyBins` | no | ANY ONE must exist |
| `user-invocable` | no | allow `/command` style invocation (default: true) |

### 3c. Body Structure — Choose a Pattern

Match the body structure to the skill's nature. Don't force workflows onto knowledge skills or vice versa.

| Pattern | Best for | Example |
|---------|----------|---------|
| **Workflow-based** | Sequential processes | charting: fetch → configure → render → serve |
| **Task-based** | User-driven, multiple entry points | trading: "analyze" / "compare" / "check sentiment" |
| **Reference/guidelines** | Rules, frameworks, decision trees | strategy: core principles, when to do X vs Y |
| **Capabilities-based** | Tool groupings | market-data: price tools / derivatives tools / social tools |

**Write for the agent, not the user.** Direct voice.  
Bad: "This skill can be used to generate charts when the user requests them."  
Good: "You generate charts. Fetch OHLCV data, configure the chart layout, render via the charting script, and serve with `preview_serve`."

**What to include:**
- Domain knowledge the agent doesn't have from tool descriptions
- Decision trees: "when X use Y, when Z use W"
- Gotchas and edge cases
- Key thresholds and parameters

**What to leave out:**
- Tool parameter docs (already in system prompt)
- Generic programming advice
- README / changelog content
- Step-by-step for trivially obvious sequences

### 3d. On-Chain Skills — Wallet Policy Prerequisite

If the skill involves any on-chain operations (transactions, approvals, swaps, bridging, signing):

```markdown
## Prerequisites — Wallet Policy

Before executing any [operation], the wallet policy must be active.
Load the **wallet-policy** skill and propose the standard wildcard
policy (deny key export + allow `*`). This covers all [skill-name]
operations across all chains.
```

### 3e. Composability Check

Before finalizing: does this skill assume it's the only capability active? It shouldn't.

- Does it use tool names that might conflict with other skills? Rename.
- Does the description overlap with an existing skill? Narrow the trigger.
- Does it hardcode assumptions about what other skills exist? Remove them.
- Would it break if loaded alongside the skill it's replacing? Test it.

---

## Phase 4: Define Success Criteria

Define these before testing, not after. Write them into the skill's comments or your notes.

**Quantitative (aim for these thresholds):**
- Triggers on ≥90% of queries you listed in the Use-Case Canvas
- Does NOT trigger on >5% of unrelated queries
- Completes its workflow in ≤ the number of tool calls you expect
- Zero API call failures due to wrong parameters

**Qualitative:**
- User doesn't need to re-prompt or correct the agent mid-workflow
- Output is consistent across sessions with the same input
- Works alongside other skills without conflicts

---

## Phase 5: Validate (Syntax + Behavior)

### Syntax validation

```bash
python skills/skill-creator/scripts/validate_skill.py ./skills/my-new-skill
```

This checks: frontmatter structure, required fields, TODO placeholders, body length, field placement.

### Behavioral testing

Run 3+ test cases from your Use-Case Canvas and evaluate against your success criteria:

```
Test: "[exact user phrase from canvas]"
Expected: skill triggers, completes workflow X
Actual: _______________
Pass/Fail: ___
```

**Common failure modes and fixes:**

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Skill never triggers | Description too vague | Add "Use when..." with exact trigger phrases |
| Triggers for wrong requests | Description too broad | Narrow trigger conditions, add "NOT for..." |
| Workflow stops mid-way | Missing decision branch | Add the missing case to the body |
| Works first run, fails second | Session state assumption | Remove stateful assumptions from instructions |
| Conflicts with another skill | Overlapping descriptions | Differentiate with specific trigger conditions |

**Edge cases to test:**
- Empty/ambiguous user input
- Multi-step workflows where earlier steps fail
- Concurrent use with another active skill
- First use (no prior context) vs. mid-conversation use

---

## Phase 6: Refresh and Confirm

```python
skill_refresh()
```

Then run one final test from your Use-Case Canvas to confirm the skill loads, triggers, and completes.

---

## Anatomy of a Well-Structured Skill

```
my-skill/
├── SKILL.md          # Frontmatter + core instructions (< 500 lines)
├── scripts/          # Fragile operations: exact API calls, rendering pipelines
│   └── render.py     #   Executed via bash, never loaded into context
├── references/       # Detailed docs loaded on demand
│   └── api-guide.md  #   Only read when agent explicitly needs it
└── assets/           # Templates, images, config files used in output
    └── template.json #   Never loaded into context
```

**Context budget:**
- SKILL.md body: loaded on every activation — keep it lean, ≤ 500 lines
- `scripts/`: executed, not read — no context cost
- `references/`: read on demand — only when explicitly needed
- `assets/`: never in context — output artifacts only

---

## What NOT to Include

- **README.md** — SKILL.md IS the readme
- **CHANGELOG.md** — skills aren't versioned packages
- **Generic best practices** — "use error handling" is noise, specific gotchas are signal
- **Tool parameter docs** — already in the system prompt
- **Security credentials** — never hardcode API keys; use `requires.env` and env vars

---

## Publishing to the Skill Market

When the skill is ready to share, publish it via the skill-installer workflow.

**Pre-publish checklist:**
- [ ] `name` field: lowercase hyphen-case, 2-64 chars
- [ ] `version` field: semver (e.g. `1.0.0`) — immutable once published
- [ ] `description` passes the formula test (what + when)
- [ ] `author` and `tags` set
- [ ] No `[TODO]` placeholders in body
- [ ] Validate passes with no errors
- [ ] Behavioral tests pass for all Use-Case Canvas scenarios
- [ ] No XML tags `< >` in description

**Publish:**

```bash
# 1. Get OIDC token
TOKEN=$(curl -s --unix-socket /.fly/api \
  -X POST -H "Content-Type: application/json" \
  "http://localhost/v1/tokens/oidc" \
  -d '{"aud": "skills-market-gateway"}')

# 2. Build and publish
SKILL_DIR="./skills/my-skill"
GATEWAY="https://skills-market-gateway.fly.dev"

PAYLOAD=$(python3 -c "
import os, json
files = {}
for root, dirs, fnames in os.walk('$SKILL_DIR'):
    for f in fnames:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, '$SKILL_DIR')
        with open(full) as fh:
            files[rel] = fh.read()
print(json.dumps({'files': files}))
")

curl -s -X POST "$GATEWAY/skills/publish" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | python3 -m json.tool
```

Version is immutable after publishing — bump to `1.0.1` before republishing.
