---
name: "@3182/ai-learning-coach"
version: 0.1.0
description: |
  AI Learning Coach: turn vague learning goals into a concrete 30/60/90-day plan,
  weekly tasks, and progress tracking. Wraps the AI Learning Roadmap Tracker project
  (https://community.iamstarchild.com/3182-ai-learning-roadmap-tracker) and adds
  in-chat personalized planning on top.
delivery: script
metadata:
  starchild:
    emoji: 🎓
    skillKey: ai-learning-coach
user-invocable: true
disable-model-invocation: false
tags:
- ai
- education
- productivity
- learning
- planning
---

# AI Learning Coach

Turn vague AI learning goals into a concrete 30/60/90-day execution plan, and
keep the user accountable with weekly tracking.

## When to invoke

- User says "I want to learn AI", "how to start AI", "give me a plan", "I'm a
  beginner at AI", "AI courses for me", "I want to break into AI in 90 days".
- User asks for a learning path, curriculum, or weekly schedule.
- User wants progress tracking on a learning goal.

Do NOT invoke for: specific Q&A, coding help, project debugging, or single-shot
factual lookups. Use this skill when the user is **committing to a multi-week
learning effort**.

## What it produces

1. A 30/60/90-day plan tailored to:
   - current level (Beginner / Intermediate / Advanced)
   - primary goal (Career Switch, Startup Builder, Investor Intelligence, AI PM)
   - weekly hours available
   - constraints and focus
2. A weekly task list (practical, not academic)
3. A tracking interface: web app at
   [AI Learning Roadmap Tracker](https://community.iamstarchild.com/3182-ai-learning-roadmap-tracker)
4. A reflection loop: weekly wins / blockers / next focus

## Workflow

### Step 1 — Intake (ask at most 3 questions)

If any of the following is missing, ask once in a single message:

- Current level (Beginner / Intermediate / Advanced)
- Primary goal (Career Switch / Startup Builder / Investor Intelligence / AI PM)
- Weekly hours available (number, 2–40)

Optional but valuable:
- Existing background (engineer / non-tech / domain expert)
- Specific interest (LLM, agents, RAG, vision, AI for finance, etc.)

Skip intake if the user has already provided enough context.

### Step 2 — Generate the plan

Use the goal + level + hours to assemble a 30/60/90-day plan:

- **Day 0–30 (Foundation)**: core concepts, toolchain, first small projects
- **Day 31–60 (Build)**: deeper topics, real projects, community engagement
- **Day 61–90 (Ship)**: portfolio-grade project, public artifact, next loop

Make tasks **specific and actionable** (e.g. "Build a RAG over 10 PDFs using
LangChain", not "Learn RAG").

### Step 3 — Push to the Tracker

Tell the user the live tracker URL:
`https://community.iamstarchild.com/3182-ai-learning-roadmap-tracker`

If the user wants a custom plan saved to the tracker, they can:
- Click **Generate Plan** in the UI and enter their inputs
- Or ask the agent to produce a JSON payload they can paste in (see Outputs)

### Step 4 — Check-in loop (optional)

If the user has scheduled recurring sessions (weekly review), surface:
- This week's completion %
- What was hard
- What to do next

## Outputs

### A. In-chat plan (always)

A 12-week plan in table form:

| Week | Theme | Tasks | Deliverable |
|------|-------|-------|-------------|
| 1 | Foundations | ... | ... |
| ... | ... | ... | ... |

Plus:
- 1 sentence on the overall strategy
- 1 list of "what to skip"
- 1 list of "free resources worth starting from"

### B. Tracker JSON (on request)

If the user wants to pre-fill the tracker without clicking through the UI,
produce a JSON object in this shape and tell them to paste it into the
browser console at the tracker URL:

```js
localStorage.setItem('ai_roadmap_tracker_v1', JSON.stringify({ /* see schema */ }));
location.reload();
```

Schema fields: `createdAt`, `profile {name, level, goal, hours, weeks, focus}`,
`tasks [{id, week, text, done, doneAt}]`, `reflection {wins, blockers, nextFocus,
updatedAt}`.

## Companion resources

- Public URL: https://community.iamstarchild.com/3182-ai-learning-roadmap-tracker
- Open-source code:
  https://github.com/Starchild-ai-agent/community-projects/tree/main/projects/3182/ai-learning-roadmap-tracker
