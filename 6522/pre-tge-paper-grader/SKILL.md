---
name: "@6522/pre-tge-paper-grader"
version: 1.0.0
description: "Rate the research QUALITY of a pre-TGE / pre-launch research paper itself — evidence, logic, valuation rigor, risk honesty, and argument structure. For grading a note's content as research, not for grading whether the trade is actionable (use research-article-grader for that)."
author: Tangtrades
tags: [research, grading, crypto, due-diligence, tokenomics]
---

# Pre-TGE Paper Grader

Judge the QUALITY OF THE RESEARCH, not the outcome. A paper can be excellent research and still lose money; it can be terrible research and still make money. Grade the thinking, not the P&L.

## Core stance: brutish honesty
- Reward: verified primary sources, live/on-chain data anchors, explicit assumptions, falsifiable claims, honest uncertainty, quantified scenarios, named risk mechanisms.
- Punish: unverified "protocol claims" treated as fact, conflating commitments with executed deals, cherry-picked comps, implied-precision without source, survivorship framing, missing counter-arguments, borrowing the conclusion you're paid to reach.

## Scoring dimensions (each 0-10)
1. **Evidence & sourcing** — Are claims tied to verifiable sources (DeFiLlama, on-chain, SEC, exchange announcements)? Distinguish on-chain verified vs. protocol-claimed vs. hearsay. Are sources dated? Any number with no source = penalty.
2. **Analytical rigor** — Are the mechanics actually modeled (float, sell pressure, take rate, unlock math)? Does the paper recompute from first principles or copy headline numbers? Internal consistency of the model (do the tables sum, do the ratios match)?
3. **Valuation method** — Are comps justified and apples-to-apples? Is the chosen metric (FDV/TVL, FDV/revenue, take rate) appropriate to the business model? Are scenario ranges anchored to evidence, not vibes? Is the multiple defensible?
4. **Risk honesty & disconfirmation** — Are material risks named with mechanisms and magnitudes, or buried? Does the paper seek out what would break the thesis, or only assemble support? Are tail risks quantified or hand-waved?
5. **Argument & conclusion integrity** — Is the stated conclusion actually supported by the evidence shown? Any gap between "what we show" and "what we claim"? Is the recommendation separable from the facts, or does the author's position (e.g. relationship with founder, SAFT exposure) leak in as bias?

## Explicit bias flags (apply across all dimensions)
- Relationship disclosure (author is investor / founder is contact) — must be disclosed; if not, big penalty.
- Directional mandate (paper written to justify a held position).
- Treating pipeline/term-sheet/committed capital as realized revenue.
- "Verified" label on an unverifiable number.

## Output: grade card
- Verdict: `Excellent / Solid / Adequate / Weak / Fails` + X.X/10 overall (weighted: evidence 25%, rigor 25%, valuation 20%, risk 20%, integrity 10%).
- Per-dimension score + 1-line reason each.
- 3 strongest pieces of evidence actually shown.
- 3 sharpest omissions / disconfirming angles not addressed.
- One question the paper's author should have asked and didn't.
- Cross-paper comparison table if grading 2+ papers.

Tone: direct, zero flattery, cite page/section where possible. Grade the paper, not the outcome.
