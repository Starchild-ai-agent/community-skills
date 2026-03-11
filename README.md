# Starchild Community Skills

Community-contributed skills for [Starchild](https://iamstarchild.com) AI agents. Each skill teaches an agent a new capability — DeFi bridging, trading strategies, content writing, dashboards, and more.

## Repository Structure

```
/
├── skills.json                  # Global skill index
├── .github/workflows/           # CI/CD automation
└── [namespace]/                 # User namespace (numeric ID)
    └── [skill-slug]/            # Skill directory
        ├── SKILL.md             # Core skill file (required)
        ├── scripts/             # Helper scripts (optional)
        └── README.md            # Extended docs (optional)
```

## Browse Skills

Every skill is listed in [`skills.json`](./skills.json) at the repository root. You can also browse by namespace directory.

| Skill | Author | Description |
|-------|--------|-------------|
| [@1247/across-bridge](./1247/across-bridge/) | 1247 | Bridge tokens between EVM chains via Across Protocol |
| [@1363/copy-trade](./1363/copy-trade/) | 1363 | Copy trade Hyperliquid wallets automatically |
| [@1363/dub-trading-skill](./1363/dub-trading-skill/) | 1363 | Range trading with scaled entries/exits |
| [@1363/hyperliquid-dashboard](./1363/hyperliquid-dashboard/) | 1363 | Real-time Hyperliquid position monitoring |
| [@1363/position-snapshot](./1363/position-snapshot/) | 1363 | OHLC charts with position overlays |
| [@1363/profit-poster](./1363/profit-poster/) | 1363 | TradingView-style trade summary cards |
| [@1365/across-bridge](./1365/across-bridge/) | 1365 | Fast cross-chain bridging via Across |
| [@1435/hyperclaw](./1435/hyperclaw/) | 1435 | Trade perps on HyperClaw.io (Orderly Network) |
| [@1892/content-writing](./1892/content-writing/) | 1892 | Blog posts, articles, and tweet threads |
| [@1892/crypto-content](./1892/crypto-content/) | 1892 | Crypto-focused content writing |
| [@349/lighter-dex](./349/lighter-dex/) | 349 | Trade perps on Lighter DEX |
| [@349/starchild-design-pack](./349/starchild-design-pack/) | 349 | UI/UX design system for vibe coders |
| [@349/starchild-strategies](./349/starchild-strategies/) | 349 | Algorithmic trading strategy library |
| [@554/better-skill-creator](./554/better-skill-creator/) | 554 | High-quality skill creation framework |
| [@554/news-aggregator-skill](./554/news-aggregator-skill/) | 554 | Multi-source news aggregation (28 sources) |
| [@554/skill-installer](./554/skill-installer/) | 554 | Search and install skills from marketplace |
| [@554/youtube-summary](./554/youtube-summary/) | 554 | YouTube video transcript summarizer |

## Install a Skill

The easiest way is through your Starchild agent:

```
"Install the across-bridge skill"
"Find skills for trading on Hyperliquid"
```

To install manually, copy the skill directory into your agent's `skills/` folder:

```bash
# Clone and copy
git clone https://github.com/Starchild-ai-agent/community-skills.git
cp -r community-skills/1365/across-bridge ./skills/across-bridge
```

Or download a specific skill's release bundle from [Releases](https://github.com/Starchild-ai-agent/community-skills/releases).

## Publish a Skill

Skills are published through your Starchild agent — not via pull requests.

```
"Publish my across-bridge skill to the marketplace"
```

The agent handles validation, versioning, and index updates automatically.

## SKILL.md Format

Every skill requires a `SKILL.md` with YAML frontmatter:

```yaml
---
name: "@namespace/skill-slug"
version: "1.0.0"
description: "What this skill does — keep it concise and keyword-rich."
author: "your-name"
tags: [defi, bridge, cross-chain]
---

# Skill Title

Your skill instructions here...
```

**Required fields:**
- `name` — Must match `@namespace/skill-slug` format
- `version` — Semver (e.g. `1.0.0`)
- `description` — Used for search matching

## CI/CD

- **Pull requests** — Validates SKILL.md frontmatter, path consistency, and format
- **Post-merge** — Automatically rebuilds `skills.json` index

## License

Individual skills may have their own licenses. Check each skill's directory for details.
