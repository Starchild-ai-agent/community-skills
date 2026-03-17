---
name: "@554/work-migration"
version: 1.0.0
description: "Package current work for handoff to another agent. Use when the user asks to migrate, transfer, hand off, or export work to another agent or environment. Produces a self-contained .zip with all files, configs, memory, and a comprehensive readme so the receiving agent needs zero additional context."
author: starchild
tags: [migration, handoff, packaging, agent, workflow]

metadata:
  starchild:
    emoji: "📦"
    skillKey: work-migration

user-invocable: true
---

# Work Migration

Package work into a self-contained .zip that another agent can pick up cold — no chat history, no implicit knowledge, no "you should already know this."

## Core Principle

**The receiving agent is a blank slate.** It has never seen your conversation history, your memory topics, your `.env`, your scheduled tasks, or your running services. Everything it needs must be inside the zip. If you're thinking "that's obvious, I don't need to write it down" — write it down.

## Workflow

### Phase 1: Scope

Ask the user: **what work are we migrating?** Could be a project, a custom skill, an ongoing task, or a full workspace. Pin down boundaries before collecting files.

### Phase 2: Dependency Discovery

Work has tentacles. Trace ALL categories:

| Category | Where to look | What to capture |
|----------|---------------|-----------------|
| **Source code** | Project dirs | All files preserving structure |
| **Env vars** | `.env` | ⚠️ SENSITIVE — see Security section below |
| **System deps** | `setup.sh` | pip/apt/npm packages installed for this work |
| **Custom skills** | `skills/` | Any skills created or modified for this work |
| **Scheduled tasks** | `list_scheduled_tasks` | Job ID, schedule, description, model, full command |
| **Running services** | `/data/previews.json` | Dir, command, port — note must be restarted |
| **Memory** | `memory_topics` + `memory_get` | Export relevant topic summaries as .md files |
| **User preferences** | `prompt/SOUL.md`, `prompt/USER.md` | Sections relevant to this work's behavior |
| **Decision history** | Conversation context + memory | Why things are the way they are |
| **External APIs** | Code + .env | Endpoint, auth method, rate limits, quirks |
| **Blockchain/wallet** | Code + wallet tools | Addresses, chains, contracts — NEVER private keys |

### Phase 3: Write work_migration_readme.md

**The most important file in the package.** Follow the template in `references/readme-template.md`.

The template has 10 mandatory sections. Key rules:
- **File Manifest**: every file in zip listed with purpose. No orphans.
- **Decision Log**: top 3-5 non-obvious decisions. Prevents re-litigating settled choices.
- **How to Resume**: exact step-by-step for the receiving agent to pick up work.
- **No implicit knowledge**: ban phrases like "as discussed", "as before", "the usual".

### Phase 3.5: Security Checkpoints

**Two mandatory prompts before packaging:**

#### 🔐 Env Vars — Ask User

```
Found these env vars relevant to this work:
- OPENAI_API_KEY (used in src/llm.py)
- POSTGRES_URL (used in src/db.py)
- TELEGRAM_BOT_TOKEN (used in scripts/notify.py)

Include actual values in the package?
  [A] Yes, include values (convenient but sensitive)
  [B] No, redact values — only include names + purpose (safer)
  [C] Let me pick which ones to include

⚠️ Anyone who gets this zip will see the values.
```

**Rules:**
- **Default recommendation is B** (redact). Explicitly tell user this is safer.
- If user chooses A or C, warn once: "These values will be in plaintext inside the zip."
- If user chooses B, write a clear table in readme: var name → purpose → how to obtain.
- **NEVER include private keys, wallet seeds, or signing keys regardless of user choice.**

#### 🔒 ZIP Password — Ask User

```
Protect the zip with a password?
  [A] Yes — I'll set a password (recommended if transferring over internet)
  [B] No — plain zip is fine

Password adds encryption so the file is safe in transit.
```

**Rules:**
- If yes, ask user to provide the password (do NOT generate one).
- Use `zip -e` (standard encryption) or `7z a -p` (AES-256, stronger).
- Remind user: "Send the password through a separate channel from the zip file."
- If `7z` not installed, fall back to `zip -e` and note it uses ZipCrypto (weaker).

### Phase 4: Package

```bash
mkdir -p /tmp/work-migration-[name]
# Copy files preserving structure
cp -r [identified-files] /tmp/work-migration-[name]/
# Export memory topics
mkdir -p /tmp/work-migration-[name]/memory/
# Copy readme to root
cp work_migration_readme.md /tmp/work-migration-[name]/

# Zip — with or without password based on user choice
cd /tmp
# No password:
zip -r /data/workspace/output/work-migration-[name].zip work-migration-[name]/
# With password (if user chose yes):
# zip -e -r /data/workspace/output/work-migration-[name].zip work-migration-[name]/
# Or stronger encryption:
# 7z a -p"USER_PASSWORD" -mhe=on /data/workspace/output/work-migration-[name].7z work-migration-[name]/

rm -rf /tmp/work-migration-[name]
```

### Phase 5: Quality Gate

Before delivering, self-review:

1. **Blank slate test**: Could a new agent with ONLY this zip fully resume? If no → missing something.
2. **No dangling refs**: Every file in readme exists in zip, every file in zip is in readme.
3. **Env vars handled per user choice**: If redacted → table complete. If included → no private keys/seeds leaked.
4. **Password applied if requested**: Verify zip is encrypted before delivering.
5. **Decision log populated**: At least 3-5 entries.

## Edge Cases

- **Full workspace migration**: Include SOUL.md, USER.md, all memory, all tasks, all custom skills.
- **Skill-only**: Skill dir + dependent scripts + env vars.
- **Running services**: Document but note must be restarted. Don't migrate running state.
- **Wallet work**: Include addresses/chains/contracts, NEVER private keys. Document required policies.
