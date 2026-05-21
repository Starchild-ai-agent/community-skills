---
name: "@4544/hr-screen-brief"
version: 1.0.0
description: Objective HR-screen candidate brief. Use when the user provides interview/screen notes and wants reusable, business-ready Chinese feedback for hiring managers (standard + compressed), without subjective hiring conclusions.
metadata:
  starchild:
    emoji: "🧾"
    skillKey: hr-screen-brief
user-invocable: true
disable-model-invocation: false
---

## Purpose
Convert raw candidate communication records (interview notes / phone-screen notes / chat logs) into Chinese feedback that can be sent directly to hiring managers. Focus on **objective facts + role alignment + business value**, without subjective hire/no-hire conclusions.

## Hard Constraints (must always follow)
1. Do not write subjective conclusions (forbidden: “recommend hire”, “strongly recommend”, “do not proceed”, etc.).
2. Start with **role-aligned reasons to proceed**; number of reasons depends on available facts (not fixed).
3. Each reason should include three parts whenever possible:
   - Alignment target (what the role needs)
   - Objective evidence (what the candidate said/did)
   - Business value (what it means for the team/role)
4. Do not include “next-round validation questions”.
5. End with one fixed question:
   - `是否继续推进该候选人进入下一流程？`

## Input Handling
When the user provides candidate records, extract objective facts from the current material only (no assumptions), across these dimensions:
- Basic profile: location, level/seniority, current status
- Experience & outputs: what was done, duration, quantified results (if any)
- Motivation fit: why they are exploring, whether it matches role direction
- Capability signals: stack/tools, methods, problem-solving approach
- Availability: start time, weekly commitment, sustainable duration
- Other objective constraints: compensation, location, visa/compliance, process status (only if explicitly present)

## Writing Workflow
1. Extract facts and remove subjective adjectives.
2. Map facts into role-aligned reasons to proceed.
3. Generate two output versions:
   - Standard version (formal sync)
   - Compressed version (within two short paragraphs for WeChat/Slack)
4. Use the fixed closing question, without recommendation language.

## Output Formats

### A) Standard Version (default)
Structure:
- Opening sentence: objective summary from this round
- `与岗位需求对齐的推进理由` (1..N reasons)
  - Each reason contains: alignment target / objective evidence / business value
- `补充客观信息` (optional)
- Fixed closing question

Closing line example:
`是否继续推进该候选人进入下一流程？`

### B) Compressed Version (WeChat/Slack)
- Keep within two paragraphs:
  - Paragraph 1: key objective facts + 2–4 role-aligned reasons
  - Paragraph 2: fixed closing question
- Keep the tone natural, conversational, and directly forwardable (no AI-like wording).

## Style Guide
- Objective, concise, and easy to relay.
- Prefer evidence-based phrasing such as “可见/体现/显示/已提供” in final Chinese output.
- Avoid exaggerated words (e.g., “非常优秀”, “强烈推荐”).
- If evidence is insufficient, state “当前材料未体现/未提供” instead of guessing.

## Edge Cases
- If no clear job target/JD is provided: still produce output; use generic capability alignment (e.g., execution, learning agility, sustained commitment), and note that JD can enable sharper alignment.
- If source material is sparse: only output existing facts, explicitly note limited information, and keep the fixed closing question.
- If user asks for short message only: provide compressed version directly.

## Language Switch
Default output language is Chinese.

- Default: Chinese output (both Standard + Compressed).
- Optional: English output when the user explicitly requests English (e.g., "英文版", "output in English", "send to global HM in English").
- If language is not specified, keep Chinese.

For English mode:
- Keep the same structure and hard constraints.
- Use the equivalent fixed closing question:
  - `Shall we proceed with this candidate to the next stage?`

## Reuse Rule
For similar requests by default:
- Provide both **Standard + Compressed** versions first, in Chinese.
- If the user explicitly asks for English, switch both versions to English.
- If the user asks for only one version, trim accordingly.