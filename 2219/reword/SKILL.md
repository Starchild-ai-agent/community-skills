---
name: "@2219/reword"
version: 1.3.0
description: >
  Rewrites a user's raw prompt into a clearer, higher-performing prompt they can
  reuse directly. Trigger when the user starts their message with /reword,
  asks to improve a prompt, asks to rewrite a prompt, or wants prompt
  engineering help. When triggered by /reword, do not execute the task itself.
  Return only the improved prompt in a copy-ready format.
author: starchild
tags:
  - prompt-engineering
  - rewriter
  - optimizer
  - efficiency
user-invocable: true
---

## Reword

This skill is a prompt-rewriting layer for Starchild.

Its purpose is to take a rough user prompt, improve it using strong prompt
engineering, and show the improved version back to the user so they can reuse it.

When the user starts a message with `/reword`, treat everything after `/reword`
as the source prompt to improve.

Example:
`/reword write me a landing page for an AI finance app`

In that case, you rewrite the prompt and return the improved version only.
You do not complete the landing page task itself unless the user separately asks
for execution.

## Empty input handling

If the user sends `/reword` with no text following it — or only whitespace — ask
exactly one question:

> "What prompt would you like me to improve?"

Do not attempt to rewrite, guess, or invent a prompt.

## Primary behavior

When invoked, follow this sequence:

1. Read the text after `/reword` as the raw prompt.
2. Infer the user's likely goal, output format, audience, tone, and any missing
   constraints.
3. Upgrade the prompt so it is clearer, more specific, and more likely to
   produce a strong result in one turn.
4. Keep the rewritten prompt practical and concise. Improve quality without
   turning it into an overlong wall of text.
5. Return the rewritten prompt in a copy-ready block.
6. Do not answer the rewritten prompt.
7. Do not explain your full reasoning unless the user asks.

## Rewriting principles

Apply these improvements where useful:

- Clarify the real task
- Specify desired output format
- Add audience and tone when implied
- Add missing constraints that materially improve output
- Add quality bars such as clarity, accuracy, depth, edge cases, or production readiness
- Remove vagueness, filler, and ambiguity
- Prefer direct language over bloated wording
- Default to reasonable assumptions over asking follow-up questions. Only ask a
  single clarifying question if the prompt is genuinely unsalvageable without
  more info (see "When to ask one question" below). Assumptions always win over
  questions when a sensible default exists.

## Prompt length guidance

Aim for roughly 2–5× the length of the raw input. Cap at around 150 words
unless the task's complexity genuinely demands more. A good rewrite is denser
and more precise, not just longer. If the original prompt is already detailed,
tighten it rather than expanding.

## Compound and multi-step prompts

If the raw prompt contains multiple distinct tasks bundled together (e.g.
"build a page and write the copy and deploy it"), decide:

- If the tasks are tightly coupled and best done in one turn, rewrite as a
  single structured prompt with clearly numbered steps.
- If the tasks are loosely related or would produce better results separately,
  rewrite as the single most important prompt and add a short note suggesting
  the user split the remaining tasks into follow-ups.

Do not silently drop parts of the original request.

## Skill and tool routing

When the rewritten prompt would benefit from a specific skill, tool, or
approach, bake that guidance directly into the prompt text. The goal is to make
the prompt self-routing — so that when pasted into Starchild (or any capable
model), it naturally triggers the right behavior without the user needing to
know what's available.

Tactics:

- **Name the output type explicitly** when it maps to a known skill or tool.
  Instead of "make a presentation," write "Create a .pptx presentation…" so a
  presentation skill triggers. Instead of "make a doc," write "Create a Word
  document (.docx)…"
- **Specify the stack or format** when the task is technical. "Build a React
  component using Tailwind CSS" is more routable than "build a UI."
- **Include action verbs that signal tool use** where appropriate: "Search for…",
  "Fetch the page at…", "Read the uploaded file and…", "Generate an image of…"
- **Reference data sources or integrations** if implied by context: "Pull data
  from the connected Google Sheet," "Check my calendar for…"
- **Do not invent skills or tools that may not exist.** Stick to broadly
  understood formats and capabilities. If unsure whether a specific integration
  is available, phrase it as a conditional: "If calendar access is available,
  check for conflicts; otherwise ask me to paste my schedule."

The rewritten prompt should read naturally — skill hints should feel like
specifications, not metadata.

## Starchild-native capabilities

When the prompt involves crypto, trading, wallets, or financial data, you may
safely reference these capabilities — they exist in Starchild and will route
correctly:

- **Wallet analysis** — balances across EVM chains and Solana
- **Hyperliquid positions** — open positions, orders, fills, funding rates
- **DeFi yields** — Aave, Morpho, DefiLlama protocol data
- **Charting** — TradingView-style candlestick and indicator charts
- **Token data** — prices, market cap, volume via CoinGecko
- **On-chain analytics** — DeBank portfolio, whale tracking, liquidations via CoinGlass
- **Token unlocks** — emission schedules and allocation breakdowns via Tokenomist

Use these in routing hints when the user's implied task involves any of the above.
Do not invent capabilities beyond this list.

## Quality audit

Before returning the rewritten prompt, ask yourself one question:

> "Is this actually better — or just longer?"

If the rewrite is only longer, trim it. A good rewrite is denser and more
precise than the original. If trimming would make it worse, keep it. The test
is quality, not compression.

## Starchild behavior

This skill is for rewriting only.

- If invoked with `/reword`, return the improved prompt only
- Do not silently execute the rewritten prompt
- Do not use tools unless the user explicitly wants a research-backed prompt
- Do not add unnecessary complexity
- Optimize for token efficiency and practical reuse

## Output format

Default output format:

**Improved prompt**
```text
[rewritten prompt]
```

Optional, when useful, add a very short note below the block with one sentence
max, such as:
- Assumed a general audience.
- Optimized for Claude-style models.
- Added production-ready constraints.
- Consider splitting the deployment step into a follow-up.

Do not add long commentary.

## When to ask one question

Ask a single clarifying question only if the raw prompt is genuinely
unsalvageable without more information. This is rare. Examples:

- The user references content you cannot see and no default makes sense
- The target output depends entirely on a missing platform, language, or audience
  with no reasonable default
- The prompt is so short or vague that every possible rewrite would be a
  different task

If a reasonable default exists — even an imperfect one — use it and note the
assumption. Do not ask.

## Examples

### Example 1
User input:
`/reword write something about ai`

Output:

**Improved prompt**
```text
Write a clear 300-word overview of artificial intelligence for a general audience. Explain what AI is, how it is used today, one major benefit, one major risk, and end with a simple real-world example. Use plain English and avoid jargon.
```

### Example 2
User input:
`/reword build me a login page`

Output:

**Improved prompt**
```text
Build a modern responsive login page as a single React component using Tailwind CSS. Include email and password fields, a show-password toggle, a forgot-password link, clear validation states, and a primary sign-in button. Use clean production-ready component structure and accessible form markup.
```

### Example 3
User input:
`/reword make this email better`

Output:

**Improved prompt**
```text
Rewrite the following email to sound professional, concise, and friendly. Keep the meaning the same, improve clarity, remove filler, and end with a clear call to action: [paste email here]
```

### Example 4
User input:
`/reword make a pitch deck about our seed round`

Output:

**Improved prompt**
```text
Create a .pptx pitch deck for a seed-round fundraise. Include slides for: problem, solution, market size, product demo/screenshots, business model, traction, team, and ask. Use a clean minimal design with dark backgrounds. Keep text sparse — one key point per slide with supporting data. Assume a fintech startup unless I specify otherwise.
```
- Specified .pptx to trigger presentation tooling.

### Example 5
User input:
`/reword build me a dashboard and also write a report on the data and send it to my team`

Output:

**Improved prompt**
```text
Build an interactive data dashboard as a single-page React app using Tailwind CSS and Recharts. Include filter controls, key metric cards at the top, and at least one time-series chart and one comparison chart. Use placeholder data that I can swap out. Keep the layout clean and responsive.
```
- This is the highest-leverage task from your request. Follow up separately with: (1) "Write a .docx report summarizing the key findings from this data" and (2) "Draft a Slack message to my team sharing the report and dashboard link."

### Example 6
User input:
`/reword show me my positions`

Output:

**Improved prompt**
```text
Show my current Hyperliquid positions: open trades, entry prices, unrealised PnL, leverage, and current funding rates. Include any open orders. If I have no active positions, show my recent fills instead.
```
- Routed to Hyperliquid positions using the Starchild-native capabilities list.

## Non-goals

- Do not complete the task itself when `/reword` is used
- Do not expose hidden chain-of-thought
- Do not generate multiple prompt options unless the user asks
- Do not turn every prompt into an excessively long specification
- Do not invent or hallucinate tool names or skill identifiers

## Summary

`/reword [prompt]` means:
- if input is empty, ask "What prompt would you like me to improve?"
- read the raw prompt
- improve it (with smart format/tool/skill hints baked in)
- for crypto/trading prompts, use the Starchild-native capabilities list
- keep it 2–5× original length, ~150 word cap
- split compound tasks if they'd work better separately
- audit: "is this better, or just longer?"
- show the better version
- stop there
