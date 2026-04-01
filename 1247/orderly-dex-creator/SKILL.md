---
name: "@1247/orderly-dex-creator"
version: 2.1.0
description: End-to-end lifecycle playbook for launching and operating an Orderly perpetual futures DEX — launch, graduate, domain/DNS, growth automation, market making, vaults, and security hardening.
author: starchild
tags: [orderly, dex, perp, growth, market-making, vaults, security, domain]
---

# orderly-dex-creator

Build and operate a perpetual futures DEX on Orderly with a phased, production-oriented workflow.

## When to use this skill

Use this when the user wants to:
- Launch a new perp DEX on Orderly
- Graduate and configure fee economics
- Attach a custom domain and automate DNS
- Run autonomous growth, market making, and vault strategies
- Add continuous security monitoring across the stack

Do **not** use this for low-level endpoint implementation details alone — see `references/sdk-integration.md` and existing Orderly API/auth skills.

---

## Architecture (Skew stack + Orderly infra)

```text
DEX Frontend (Orderly ONE or custom SDK)
  ├─ OtterClaw (agent skills)
  ├─ Domain Builder (DNS automation)
  ├─ Growth Agent (daily optimization loop)
  ├─ Agentic MM (autonomous market making)
  ├─ YieldClaw (vault ops)
  └─ SecClaw (cross-system watchdog)
        ↓
Orderly infra (omnichain settlement + shared orderbook)
```

### Component map

| Component | Repo | Purpose |
|---|---|---|
| OtterClaw | https://github.com/SkewCodes/OtterClaw | Installable agent skills for onboarding/trading/data/swap/vault/payments/dex-builder |
| Domain Builder | https://github.com/SkewCodes/orderly-domain-builder | DNS/domain automation and provider-specific fixes |
| Growth Agent | https://github.com/SkewCodes/orderly-growth-agent | Autonomous growth and fee/referral optimization loop |
| Agentic MM | https://github.com/SkewCodes/orderly-agentic-mm | Fair-value quoting, adaptive spreads, and safety controls |
| YieldClaw | https://github.com/SkewCodes/YieldClaw | Vault lifecycle + strategy execution |
| SecClaw | https://github.com/SkewCodes/SecClaw | Monitoring, policy checks, and cross-system risk detection |

---

## Phase 1 — Launch

Choose one path:

| Path | Best for | Time to first launch |
|---|---|---|
| Orderly One (no-code) | Fast branded launch | Minutes |
| Custom SDK/API | Full product control | Days–weeks |

### A) Orderly One (no-code)
1. Go to `https://dex.orderly.network`
2. Connect wallet and run the setup wizard
3. Configure branding, social links, wallets, chains, navigation
4. Deploy and verify public access

### B) Custom SDK/API
Follow `references/sdk-integration.md` for React SDK / hooks / Python connector and auth model.

---

## Phase 2 — Graduate & monetize

Graduation enables builder revenue mechanics (broker identity + fee sharing capabilities).

### Operator checklist
- Complete graduation flow in official dashboard
- Confirm broker ID assignment
- Configure default and tiered fee settings
- Verify payout/reporting route before scaling traffic

> Note: economics (fees, staking tiers, costs) can change. Always verify current values in official Orderly docs/dashboard before committing production settings.

---

## Phase 3 — Domain & DNS

Use Domain Builder automation for provider-specific correctness.

```bash
git clone https://github.com/SkewCodes/orderly-domain-builder.git
cd orderly-domain-builder
./orderly-domain-setup.sh setup --domain yourdex.com --broker-id your-broker-id --yes
./orderly-domain-setup.sh verify --domain yourdex.com --broker-id your-broker-id
```

### Recommended validations
- DNS records resolve as expected (`@`, `www`)
- SSL mode and redirects are coherent (no loops)
- Cloudflare performance/security toggles do not break app rendering or websocket flows

---

## Phase 4 — Growth agent (autonomous)

```bash
git clone https://github.com/SkewCodes/orderly-growth-agent.git
cd orderly-growth-agent && npm install && npm run build
```

### Progressive trust rollout
1. **Week 1–2:** dry-run only (observe recommendations)
2. **Week 3:** enable one playbook per cycle
3. **Week 4+:** widen scope after KPI + abuse-monitor validation

### Operating model
`MEASURE → WATCHDOG → COLLECT → DIAGNOSE → DECIDE → ACT → REPORT`

---

## Phase 5 — Agentic market making

```bash
git clone https://github.com/SkewCodes/orderly-agentic-mm.git
cd orderly-agentic-mm && npm install && npm run build
```

Start conservative:
- wider spreads
- low inventory caps
- slower refresh interval
- strict circuit-breakers

Scale aggressiveness only after consistent quality grades and stable realized risk.

---

## Phase 6 — Vault operations (YieldClaw)

```bash
git clone https://github.com/SkewCodes/YieldClaw.git
cd YieldClaw && npm install && npm run build
```

Use strategy-as-config (YAML), then enforce:
- clear risk budget per vault
- max drawdown / exposure gates
- explicit operator pause path

---

## Phase 7 — Security watchdog (SecClaw)

```bash
git clone https://github.com/SkewCodes/SecClaw.git
cd SecClaw && npm install
npm run check -- --config config.yaml
```

Minimum security baseline:
- secret isolation and key rotation plan
- policy allowlists (playbooks/actions)
- cross-system exposure checks
- alert fan-out (Telegram/webhook/log) + runbook

---

## OtterClaw installable skills

- Onboarding: `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-onboarding/SKILL.md`
- Trader: `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-trader/SKILL.md`
- Data: `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-data/SKILL.md`
- Swap: `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-swap/SKILL.md`
- Vault: `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-vault/SKILL.md`
- 402 Payments: `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-402/SKILL.md`
- DEX Builder: `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-dex-builder/SKILL.md`

---

## Production readiness gate (must pass before "go live")

- [ ] Launch path validated (UI, wallet connect, trading path)
- [ ] Broker/fee configuration verified against current docs
- [ ] Domain + TLS + websocket checks green
- [ ] Growth agent started in dry-run with clear KPIs
- [ ] MM running in conservative mode, no safety trips
- [ ] Vault strategy risk caps and pause controls verified
- [ ] SecClaw alerting + incident runbook tested

---

## Operator notes

- Never market your DEX as an “official Orderly product.”
- Avoid guaranteed-return language.
- Builder/operator is responsible for legal and regulatory compliance.
- Re-verify external assumptions periodically (fees, tiers, endpoint behavior, chain support).

## Last verified

- Skill structure and references: 2026-04-01
- External economics/endpoints: **must be re-checked at execution time**
