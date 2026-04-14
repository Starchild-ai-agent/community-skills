---
name: "@2004/skill-repo-publish"
version: 1.0.0
description: "Update and publish skills to the official-skills GitHub repo. Use when the user wants to update a SKILL.md, bump version, and push to Starchild-ai-agent/official-skills."
author: starchild
tags: [github, skills, workflow, git]

metadata:
  starchild:
    emoji: "📦"
    skillKey: skill-repo-publish
    requires:
      bins: [git, python3]

user-invocable: true
---

# Skill Repo Publish

Push local SKILL.md changes to `Starchild-ai-agent/official-skills`.

## Token

Always use `GITHUB_TOKEN` (not `GITHUB_TOKEN_NEW` — no org write access).
Embed token in clone URL: `https://${GITHUB_TOKEN}@github.com/Starchild-ai-agent/official-skills.git`

## Standard Workflow

```bash
# 1. Clone (always fresh /tmp dir)
git clone https://${GITHUB_TOKEN}@github.com/Starchild-ai-agent/official-skills.git /tmp/official-skills
cd /tmp/official-skills
git config user.name "nicholasDxy"
git config user.email "nicholasDxy@users.noreply.github.com"
```

```python
# 2. Edit with Python replace (safer than sed)
with open("/tmp/official-skills/<skill>/SKILL.md", "r") as f:
    content = f.read()
content = content.replace("old text", "new text")
with open("/tmp/official-skills/<skill>/SKILL.md", "w") as f:
    f.write(content)
```

```bash
# 3. Verify diff before commit
git diff <skill>/SKILL.md

# 4. Commit + push
git add <skill>/SKILL.md
git commit -m "feat(<skill>): <summary>

<details>

Co-authored-by: Starchild <noreply@iamstarchild.com>"
git push origin main
```

## Version Bump Rules

| Change type | Bump | Example |
|-------------|------|---------|
| New capability or tool | minor | 3.2.0 → 3.3.0 |
| Doc fix / wording | patch | 3.3.0 → 3.3.1 |
| Breaking interface change | major | 3.x.x → 4.0.0 |

## SKILL.md Writing Principles

**Describe capabilities, don't enumerate dynamic data.**
- ❌ `Supported chains: ethereum, base, ...（list 16 chains）`
- ✅ `Supports all EVM chains via DeBank dynamic lookup (300+ chains)`

DeBank chain lists, token lists, and other API-driven data change over time — never hardcode them. If there's a fallback map in code, describe its purpose ("offline map for common chains, not an exhaustive list"), don't copy it into the skill.

## After Pushing

Always sync the local workspace skill too:
```python
skill_manage(action="patch", name="<skill>", old_string="version: x.x.x", new_string="version: y.y.y")
```
So local skill stays in sync with the repo version.
