# Starchild Technical Article Examples

## Example 1: The Architecture #1 — Smart Routing and the Doctor

This was the published version (v2). It covered two features at depth rather than six at surface level.

**What worked:**
- Series framing ("The Architecture #1") set expectations for recurring content
- Subtitle stated the thesis directly: "Most people run Starchild on default settings. This is about the two commands that change that."
- Each feature section explained the default problem, the command to fix it, and the concrete change
- Code blocks showed exact commands (`/model smart`, `/doctor`)
- "Why These Two First" section justified the priority order
- Series hook at the end: "Next up: Scheduled Tasks and Silent Automation"

**Full text preserved in:** `output/technical-blog-draft-v2.md`

## Example 2: The Architecture (v1 draft) — Six Features

This was the earlier draft covering Smart Routing, /doctor, Push Notifications, Memory, Skills, and Scheduled Tasks.

**What changed between v1 and v2:**
- v1 covered too many topics. Each section was 3-5 paragraphs, enough to describe but not enough to actually teach
- v2 cut to two topics and gave each room to breathe with examples, edge cases, and concrete configuration
- v2 added the "Why These Two First" connector section, which v1 lacked
- v2's subtitle was a thesis; v1's subtitle was a description ("A Starchild Best Practices Guide")

**Lesson:** Depth beats breadth. Two features a reader can actually configure beats six features they'll forget.

**Full text preserved in:** `output/technical-blog-draft.md`

## Structural Pattern (extracted from both)

```
# [Series Name] #[N]: [Specific Topic]

*[Subtitle that states the thesis, not the summary]*

## [Feature 1]: [Short Name]

[Open with the default behavior and why it's suboptimal]
[Show the command or configuration that changes it]
[Explain what changes concretely — before/after]
[Edge case or override worth knowing about]

## [Feature 2]: [Short Name]

[Same structure as Feature 1]

## Why These [N] First

[Connect the features, justify the priority, show what becomes possible]

*[Series hook — what's next]*
```
