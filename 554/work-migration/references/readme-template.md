# Work Migration: [Project Name]

> One-sentence summary of what this work is.

**Migration Date**: YYYY-MM-DD
**Source Agent**: [agent ID or environment]

---

## 1. Overview

What this project does, why it exists, current state (active / maintenance / paused / blocked). Two to three paragraphs. Include the user's original goal.

## 2. Current Status

### ✅ Completed
- [item with enough context to understand standalone]

### 🔄 In Progress
- [item + what's done + what remains]

### 📋 TODO
- [item + priority + suggested approach]

### 🚫 Blocked (if any)
- [item + blocker + suggested resolution]

## 3. Architecture

How pieces connect. Include: component relationships, data flow, entry points, communication between parts. Text diagrams are fine.

## 4. File Manifest

| Path | Purpose | Notes |
|------|---------|-------|
| `src/main.py` | Entry point | Runs on port 3000 |
| `config/settings.json` | Runtime config | See env vars section |

**Every file in zip must appear here. No orphan files.**

## 5. Environment & Configuration

### Environment Variables

<!-- Use table A if values were redacted, table B if included -->

**[If redacted]:**
| Variable | Purpose | How to obtain |
|----------|---------|---------------|
| `API_KEY_X` | Auth for service X | Sign up at https://... |

⚠️ **Values NOT included. Receiving agent must obtain from user.**

**[If included]:**
| Variable | Purpose | Included |
|----------|---------|----------|
| `API_KEY_X` | Auth for service X | ✅ See `.env` in package |

⚠️ **Values included in `.env` — treat as sensitive, do not log or expose.**

🚫 **Private keys, wallet seeds, and signing keys are NEVER included regardless of user choice.**

### System Dependencies
```bash
pip install package1 package2
apt-get install binary1
```

### Required Starchild Skills
| Skill | Purpose | Install |
|-------|---------|---------|
| `skill-name` | What for | `search_skills("skill-name")` |

## 6. Scheduled Tasks

| Description | Schedule | Mode | Config |
|-------------|----------|------|--------|
| Check X every 4h | `0 */4 * * *` | command | `python3 scripts/check.py` |

To recreate, provide exact `schedule_task` call parameters.

## 7. Memory & Context

### Exported Topics (in `memory/` dir)
- `topic-a.md` — what it tracks and why
- `topic-b.md` — ...

### User Preferences
- [e.g. "Prefers concise output, no emoji"]
- [e.g. "Timezone UTC+8"]

## 8. Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Used X over Y | Because Z | YYYY-MM-DD |
| Architecture A | Perf vs simplicity tradeoff | YYYY-MM-DD |

**Prevents receiving agent from re-litigating settled decisions.**

## 9. Known Issues & Gotchas

- [Non-obvious behavior that will trip up the new agent]
- ["If you see error X, it's because Y — do Z"]
- [Workarounds in place]

## 10. How to Resume

1. Extract zip to workspace
2. Copy env var names to `.env`, obtain values from user
3. Add system deps to `setup.sh`, run them
4. Install required skills
5. Recreate scheduled tasks (see Section 6)
6. Import memory topics: `memory_store` each exported topic
7. **Next task**: [specific actionable item to work on first]
