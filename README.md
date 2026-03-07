# Starchild Community Skills

Community-contributed skills for [Starchild](https://starchild.ai) AI agents. Skills are reusable capability modules — each one teaches an agent how to use a specific tool, protocol, or workflow.

## What's in here

Every skill lives under `namespaces/@{author_id}/{skill_name}/` and contains at least a `SKILL.md` file — the instruction set your agent reads. Some skills also include helper scripts and templates.

```
namespaces/
├── @349/
│   ├── starchild-strategies/    # Algorithmic trading strategies for perps
│   ├── lighter-dex/             # Trade on Lighter DEX
│   └── starchild-design-pack/   # UI/UX design system
├── @554/
│   ├── skill-installer/         # Search & install skills from the marketplace
│   └── better-skill-creator/    # Create high-quality skills
├── @1247/
│   └── across-bridge/           # Cross-chain bridging via Across Protocol
├── @1363/
│   ├── profit-poster/           # TradingView-style trade summary cards
│   ├── position-snapshot/       # OHLC charts with position overlays
│   ├── copy-trade/              # Copy trade Hyperliquid wallets
│   ├── hyperliquid-dashboard/   # Real-time HL wallet monitoring
│   └── dub-trading-skill/       # Range trading methodology
├── @1365/
│   └── across-bridge/           # Cross-chain bridging via Across Protocol
└── @1435/
    └── hyperclaw/               # Trade perps on HyperClaw (Orderly Network)
```

## Search and install skills

The easiest way to find and install skills is through your Starchild agent:

```
You:   search for cross-chain bridge skills
Agent: (searches the marketplace, shows results, installs for you)
```

Your agent has a built-in **skill-installer** that searches this repo and two additional curated registries (6,000+ skills total). Just describe what you need in plain language.

### Manual browsing

You can also browse skills directly on GitHub:

1. Navigate to the [`namespaces/`](./namespaces) directory
2. Open any skill's `SKILL.md` to read what it does
3. Download the files and place them in your agent's `skills/` directory

### Direct download via API

Each published skill has a downloadable bundle attached as a GitHub Release:

```
https://github.com/Starchild-ai-agent/community-skills/releases/download/@{author}/{skill}@{version}/bundle.zip
```

For example:
```
https://github.com/Starchild-ai-agent/community-skills/releases/download/@1365/across-bridge@1.0.0/bundle.zip
```

## Publishing your own skills

Skills are published **through your Starchild agent** — not via pull request.

```
You:   publish my across-bridge skill
Agent: (packages your skill, uploads to the marketplace)
```

Your agent handles versioning, bundling, and index updates automatically. You write the skill, your agent publishes it.

### Skill structure

A minimal skill needs one file:

```
skills/my-skill/
└── SKILL.md          # Required — the instruction set
```

A more complete skill might include:

```
skills/my-skill/
├── SKILL.md          # Instructions and workflow
└── scripts/
    ├── helper.py     # Helper scripts
    └── config.json   # Configuration templates
```

### Writing a good SKILL.md

Your `SKILL.md` should include:

- **Description** — what the skill does (used for search matching)
- **Prerequisites** — what tools, API keys, or setup is needed
- **Workflow** — step-by-step instructions the agent follows
- **Examples** — concrete usage patterns

See any skill in this repo for reference, or ask your agent to use the `better-skill-creator` skill to scaffold one for you.

## Versioning

Each skill is versioned independently using Git tags:

```
@{author_id}/{skill_name}@{version}
```

For example: `@1365/across-bridge@1.0.0`

When you publish an update through your agent, the version bumps automatically and a new release bundle is created.

## License

Individual skills may have their own licenses specified in their SKILL.md or accompanying files. Please check each skill's documentation for specific terms.
