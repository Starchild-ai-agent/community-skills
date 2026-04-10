---
name: "@1892/technical-writing"
version: 2.0.0
description: "Write technical deep-dive articles that explain how systems work under the hood. Use when the content is about architecture, internals, mechanisms, or engineering decisions — not announcements or launches."

metadata:
  starchild:
    emoji: "⚙️"
    skillKey: technical-writing

user-invocable: true
---

# Technical Writing

Write articles that go deeper than features and into how things actually work. For architecture posts, internals explainers, engineering decision writeups, and anything where the reader wants to understand the system, not just use it.

## When to Use This vs Content Writing

**Content writing** covers announcements, launches, partnerships, and general brand content. Use that for "what's new."

**This skill** is for "how it works." When the reader needs to understand a mechanism, a design decision, or the internals of a system to get real value out of it. The audience is power users, developers, and technically curious people who already use the product and want to go further.

If the article would feel at home on an engineering blog or in a "best practices" series, it belongs here.

## Post Types

Not every technical article is an architecture post. Match the structure to the content:

### 1. Architecture / System Design
Explains how a system is built and why decisions were made. Our default type.

```
1. Problem we needed to solve
2. Constraints and requirements
3. Options considered
4. Architecture chosen (with diagram)
5. Trade-offs we accepted
6. Results and lessons
```

### 2. Deep Dive / Explainer
Explains a concept, technology, or mechanism in depth. Not about a whole system — about one thing and how it works.

```
1. What is [concept] and why should you care?
2. How it works (simplified mental model)
3. How it works (detailed mechanics)
4. Real-world example
5. Trade-offs and when NOT to use it
6. Further reading
```

### 3. Tutorial / How-To
Step-by-step instruction. The reader should be able to follow along and build something.

```
1. What we're building (with screenshot/demo)
2. Prerequisites
3. Step 1: Setup
4. Step 2: Core implementation
5. Step 3: ...
6. Complete code (link to repo)
7. Next steps / extensions
```

Tutorial rules: show the end result first, every code block must be runnable, include error handling, explain the "why" not just the "how."

### 4. Postmortem / Incident Report
Describes what went wrong, why, and what was fixed.

```
1. Summary (what happened, impact, duration)
2. Timeline of events
3. Root cause analysis
4. Fix implemented
5. What we're doing to prevent recurrence
6. Lessons learned
```

### 5. Benchmark / Comparison
Data-driven comparison of tools, approaches, or architectures.

```
1. What we compared and why
2. Methodology (so results are reproducible)
3. Results with charts/tables
4. Analysis (what the numbers mean)
5. Recommendation (with caveats)
6. Raw data / reproducibility instructions
```

## The Pattern (Architecture Posts)

Every architecture article follows the same shape, derived from what actually performed well:

1. **Title as series entry.** Format: `The Architecture #N: [Topic]` or a series name that signals recurring depth. This sets expectations and builds a readership that comes back.

2. **Subtitle as thesis.** One line under the title that states the core argument. Not a summary of what the article covers, but the point it makes. Example: "Most people run Starchild on default settings. This is about the two commands that change that."

3. **Open with the gap.** Start by naming what most people do (the default, the obvious path) and why it's suboptimal. This creates stakes without being dramatic. The reader should feel the tension between how they currently operate and how they could.

4. **One mechanism per section.** Each section explains exactly one thing: what it is, why the default is insufficient, how to configure it differently, and what changes when you do. Don't bundle multiple features into a single section even if they're related.

5. **Code blocks as commands, not concepts.** Show the exact thing the reader would type or the file they'd edit. Not pseudocode, not abstract examples. Real commands, real file paths, real config. The article should be usable as a reference while reading it.

6. **Close with "why these first."** A brief section that connects the pieces and explains the priority order. Not a summary, but a justification: why these features matter together, why this sequence, what becomes possible once you have them dialed in.

7. **Series hook.** End with a one-liner about what's next in the series.

## Depth Per Topic

The v1 draft covered six features in one article. The v2 covered two. The v2 performed better because two topics at real depth beats six at surface level.

**Rule of thumb:** 2-3 topics per article, each with enough detail that a reader could actually implement what you're describing. If you can't write 200+ words of substantive content about a feature, it doesn't belong in a technical article. Save it for a changelog or a feature list.

## Word Count by Type

| Type | Word Count | Why |
|------|-----------|-----|
| Quick tip | 500-800 | One concept, one example |
| Tutorial | 1,500-3,000 | Step-by-step needs detail |
| Deep dive | 2,000-4,000 | Thorough exploration |
| Architecture post | 2,000-3,500 | Diagrams carry some load |
| Benchmark | 1,500-2,500 | Data and charts do heavy lifting |

## Audience Level

State your assumed audience level explicitly at the start of the article:

> "This post assumes familiarity with Docker and basic Kubernetes concepts. If you're new to containers, start with [our intro post]."

| Audience Signal | Depth |
|----------------|-------|
| "Getting started with X" | Explain everything, assume no prior knowledge |
| "Advanced X patterns" | Skip basics, go deep on nuances |
| "X vs Y" | Assume familiarity with both, focus on differences |
| "How we built X" | Technical audience, can skip fundamentals |

## Voice and Style

All rules from the content-writing skill apply, plus these additions specific to technical content:

**Be opinionated about defaults.** Technical articles exist because defaults are often wrong for power users. Say so directly. "That is waste" is better than "This may not be optimal."

**Explain the why, not just the what.** Every feature description needs a reason it exists. Don't just say "Smart Routing routes messages to different models." Say why one model for everything is a problem worth solving.

**Use concrete before/after states.** Show the world as it is, then the world as it could be. "Every message hits the same model, whether you're asking what time it is or debugging a 300-line async crawler" is more compelling than "Smart Routing optimizes model selection."

**No hedging.** Don't say "you might want to consider" or "it could be helpful to." Say "do this" or "this is worth setting up." Technical readers want conviction, not options.

**Write from experience.** Only write about what you've done in production. If exploring, say so. The sentence "We haven't tested this at scale yet, but here's our thinking" is better than pretending certainty you don't have.

**Commands and file paths are content.** Format them as code blocks. They're the most valuable part of the article because they're immediately actionable.

### Anti-AI Formatting Rules

**Never use em dashes (—).** They're an AI tell. Use commas, parentheses, or restructure the sentence instead.

Bad: "The vault—which manages liquidity automatically—reduces the need for manual intervention."
Good: "The vault manages liquidity automatically, which reduces the need for manual intervention."

**Never use horizontal dividers (---) between sections.** They make content look AI-generated. Let the headers do the work of separating sections.

**Write flowing sentences, not choppy ones.** Combine related ideas into longer sentences that flow naturally from one point to the next. Short choppy sentences read like AI output.

Bad (AI-sounding): "The system is efficient. It saves gas. Users benefit from lower costs. This improves the experience."
Good (natural flow): "The system is more efficient because it batches transactions together, which means users pay less gas and get a better experience overall."

**Never use the "It's not X. It's Y." construction.** This is the single most recognizable AI tell. Every ChatGPT output leans on it. Restructure the sentence entirely.

Bad: "It's not just a wallet. It's a financial operating system."
Bad: "This isn't automation. It's augmentation."
Bad: "It's not about the tool. It's about the workflow."
Good: "The wallet doubles as a financial operating system, handling everything from transaction signing to portfolio rebalancing."
Good: "The system augments human decisions rather than replacing them."

**Round numbers to meaningful precision.** $1.2M, not $1,234,567. Compare to benchmarks when it helps the reader understand scale.

### Additional Word Swaps

| AI-sounding | Human-sounding |
|-------------|----------------|
| excited, thrilled | confident, ready |
| revolutionary | improved, better |
| game-changing | significant |
| utilize | use |
| leverage (verb) | use |
| importantly | (just say it) |
| "it's worth noting that" | (just say it) |

Hard avoid: exciting, massive, huge, moon, WAGMI, LFG, best-in-class, world-class, ecosystem play.

### Words to Cut

| Kill | Reason |
|------|--------|
| basically, actually, probably | Hedge words that weaken conviction |
| leverage, synergy, paradigm | Corporate speak that developers despise |
| very, really, quite | Unnecessary qualifiers |
| simply, just, easily | Dismissive of reader's experience |
| "it should be noted that" | Just note it |
| "in order to" | "to" |
| obviously | If it's obvious, don't write it |

### Hedging: When It's Appropriate

Hedging is weak in most cases, but correct when:
- Genuinely uncertain outcomes ("We haven't tested this at scale yet")
- Multiple valid approaches ("Either approach works; pick based on your team's familiarity")
- Environment-specific behavior ("This may vary depending on your Kubernetes version")

### Before/After Transformations

| Weak | Strong |
|------|--------|
| "We implemented a comprehensive testing strategy" | "We moved exploratory testing into sprint planning. QE now pairs with devs during story refinement." |
| "The benefits of this approach are numerous" | "Three outcomes: bugs found 2 days earlier, 30% fewer regressions, devs now ask QE for input during design." |
| "Performance improved significantly" | "Response time: 2.3s → 180ms" |
| "You might want to consider using connection pooling" | "Use connection pooling" |
| "This could potentially cause issues" | "This causes issues" |

## Code Examples

| Rule | Why |
|------|-----|
| Every code block must be runnable | Broken examples destroy trust |
| Show complete, working examples | Snippets without context are useless |
| Include language identifier in fenced blocks | Syntax highlighting |
| Show output/result after code | Reader verifies understanding |
| Use realistic variable names | `calculateRetryDelay` not `foo` |
| Include error handling in examples | Real code handles errors |
| Pin dependency versions | "Works with React 18.2" not "React" |

Good code block format:

```python
# Exponential backoff with jitter
def calculate_retry_delay(attempt: int, base_delay: float = 1.0) -> float:
    delay = base_delay * (2 ** attempt)
    jitter = random.uniform(0, delay * 0.1)
    return delay + jitter

# Usage
delay = calculate_retry_delay(attempt=3)  # ~8.0-8.8 seconds
```

## Diagrams and Visuals

| Scenario | Diagram Type |
|----------|-------------|
| Request flow | Sequence diagram |
| System architecture | Box-and-arrow diagram |
| Decision logic | Flowchart |
| Data model | ER diagram |
| Performance comparison | Bar/line chart |
| Before/after | Side-by-side |

One diagram is worth 500 words of description. If you're describing a system with more than three components, draw it instead of narrating it.

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| No TL;DR | Busy devs leave before getting the point | 2-3 sentence summary at the top |
| Broken code examples | Destroys all credibility | Test every code block before publishing |
| No version pinning | Code breaks in 6 months | "Works with Node 20, React 18.2" |
| "Simply do X" | Dismissive, condescending | Remove "simply", "just", "easily" |
| No diagrams for architecture | Walls of text describing systems | One diagram > 500 words of description |
| Marketing tone | Developers instantly disengage | Direct, technical, honest |
| No trade-offs section | Reads as biased marketing | Always discuss downsides |
| Giant introduction before content | Readers bounce | Get to the point in 2-3 paragraphs |
| Unpinned dependencies | Tutorial breaks for future readers | Pin versions, note date written |
| No "Further Reading" | Dead end, no context | 3-5 links to deepen understanding |
| Covering too many topics | Each gets surface treatment | 2-3 topics max, each at real depth |

## Editing Checklist

Before publishing:
- [ ] Title promises something specific
- [ ] Subtitle states the thesis, not the topic
- [ ] Opening hooks in 30 seconds (the gap, the problem)
- [ ] Audience level stated explicitly
- [ ] Claims backed by examples, code, or numbers
- [ ] All unnecessary words cut (see Words to Cut)
- [ ] Code examples tested and runnable
- [ ] Trade-offs section present and honest
- [ ] Takeaway crystal clear
- [ ] Would send to a respected colleague without embarrassment

## What to Ask For

Before writing, confirm:

1. **The product or system** being explained
2. **Which features or mechanisms** to cover (2-3 max per article)
3. **The post type** — Architecture, Deep Dive, Tutorial, Postmortem, or Benchmark
4. **The series name** if this is part of a recurring set
5. **Audience level** — are they users who want to configure, or developers who want to understand the architecture? This changes how deep you go on implementation details.

If the user just says "write a technical article about X," pick the 2-3 most impactful subtopics and propose them before writing.

## Output Format

Deliver both:

1. **Article** — formatted with headers, code blocks, ready for CMS or Paragraph
2. **Tweet thread** — 3 tweets max: hook (the gap), mechanism (the core insight), outcome (what changes + link)

## References

Load on demand:
- Starchild technical article examples: [references/starchild-examples.md](references/starchild-examples.md)
