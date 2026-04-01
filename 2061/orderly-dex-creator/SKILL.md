---
name: "@2061/orderly-dex-creator"
version: 2.2.0
description: End-to-end lifecycle playbook for launching and operating an Orderly perpetual futures DEX — launch, graduate, domain/DNS, growth automation, market making, vaults, and security hardening. Includes prerequisite matrices, risk boundaries, and rollback procedures.
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

## Risk Boundary Table

Actions agents can auto-execute vs actions requiring human approval.

| Action | Auto-pass | Human approval required |
|---|---|---|
| **Growth** | Adjust referral codes, rotate creatives, reallocate budget within caps | Increase total budget, change fee tiers, enable new chains |
| **Market Making** | Refresh quotes, adjust spread within band, pause on circuit-breaker | Widen inventory caps, change quoting pairs, override circuit-breaker |
| **Vaults** | Rebalance within risk budget, pause on drawdown limit | Deploy new vault, raise exposure caps, change strategy config |
| **Security** | Alert on anomaly, block flagged address, rotate compromised key | Whitelist new address, modify policy allowlists, disable monitoring |
| **Domain/DNS** | Verify records, renew SSL | Change DNS provider, modify domain records, transfer domain |
| **Graduation** | Read fee/tier status | Change fee configuration, modify broker settings |

**Rule of thumb:** if it moves money, changes limits, or weakens security → human approval.

---

## Phase 1 — Launch

### Prerequisites

| Need | Details |
|---|---|
| Wallet | EVM wallet with gas on target chain(s) |
| Access | Orderly dashboard account |
| Infra | Node.js 18+ (custom path only) |

### Choose one path

| Path | Best for | Time to first launch |
|---|---|---|
| Orderly One (no-code) | Fast branded launch | Minutes |
| Custom SDK/API | Full product control | Days–weeks |

#### A) Orderly One (no-code)
1. Go to `https://dex.orderly.network`
2. Connect wallet and run the setup wizard
3. Configure branding, social links, wallets, chains, navigation
4. Deploy and verify public access

#### B) Custom SDK/API
Follow `references/sdk-integration.md` for React SDK / hooks / Python connector and auth model.

**Rollback:** Delete deployment / disconnect wallet. No on-chain state created yet.

---

## Phase 2 — Graduate & monetize

### Prerequisites

| Need | Details |
|---|---|
| Phase 1 | DEX live and accessible |
| Volume | Sufficient trading activity for graduation eligibility |
| Dashboard | Access to Orderly builder dashboard |

Graduation enables builder revenue mechanics (broker identity + fee sharing).

### Operator checklist
- Complete graduation flow in official dashboard
- Confirm broker ID assignment
- Configure default and tiered fee settings
- Verify payout/reporting route before scaling traffic

> Note: economics (fees, staking tiers, costs) can change. Always verify current values in official Orderly docs/dashboard before committing production settings.

**Rollback:** Fee settings are dashboard-configurable. Revert to previous tier config if metrics degrade.

---

## Phase 3 — Domain & DNS

### Prerequisites

| Need | Details |
|---|---|
| Domain | Registered domain name |
| DNS provider | Cloudflare, GoDaddy, Namecheap, or Unstoppable Domains |
| Broker ID | From Phase 2 graduation |

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

**Rollback:** Revert DNS records to previous values. Domain Builder stores previous config in `.orderly-domain-backup`.

---

## Phase 4 — Growth agent (autonomous)

### Prerequisites

| Need | Details |
|---|---|
| Broker ID | Active and graduated |
| API keys | Orderly API key pair for the growth agent |
| Node.js | 18+ with npm |
| Budget | Defined growth budget cap (agent cannot exceed) |

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

**Rollback:** Disable active playbook → agent reverts to dry-run mode. No manual cleanup needed.

---

## Phase 5 — Agentic market making

### Prerequisites

| Need | Details |
|---|---|
| API keys | Dedicated MM API key pair (separate from growth) |
| Capital | Funded trading account on Orderly |
| Pairs | Target pairs selected and validated for liquidity |
| Node.js | 18+ with npm |

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

**Rollback:** Kill MM process → cancel all open orders via API → verify flat position. One command: `npm run emergency-stop`.

---

## Phase 6 — Vault operations (YieldClaw)

### Prerequisites

| Need | Details |
|---|---|
| Strategy config | YAML strategy file with risk parameters defined |
| Capital | Vault seed capital allocated |
| Risk budget | Max drawdown %, max exposure per vault documented |
| Node.js | 18+ with npm |

```bash
git clone https://github.com/SkewCodes/YieldClaw.git
cd YieldClaw && npm install && npm run build
```

Use strategy-as-config (YAML), then enforce:
- clear risk budget per vault
- max drawdown / exposure gates
- explicit operator pause path

**Rollback:** Trigger pause → vault stops accepting deposits → unwind positions to stable assets. Use `npm run pause -- --vault <id>`.

---

## Phase 7 — Security watchdog (SecClaw)

### Prerequisites

| Need | Details |
|---|---|
| Config | `config.yaml` with monitored endpoints and alert channels |
| Alert channel | Telegram bot token or webhook URL |
| Access | Read access to all systems being monitored |

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

**Rollback:** SecClaw is read-only monitoring. Disable by stopping the process. No state to revert.

---

## OtterClaw installable skills

| Skill | Install link |
|---|---|
| Onboarding | `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-onboarding/SKILL.md` |
| Trader | `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-trader/SKILL.md` |
| Data | `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-data/SKILL.md` |
| Swap | `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-swap/SKILL.md` |
| Vault | `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-vault/SKILL.md` |
| 402 Payments | `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-402/SKILL.md` |
| DEX Builder | `https://github.com/SkewCodes/OtterClaw/blob/main/skills/orderly-dex-builder/SKILL.md` |

---

## Production readiness gate (must pass before "go live")

- [ ] Launch path validated (UI, wallet connect, trading path)
- [ ] Broker/fee configuration verified against current docs
- [ ] Domain + TLS + websocket checks green
- [ ] Growth agent started in dry-run with clear KPIs
- [ ] MM running in conservative mode, no safety trips
- [ ] Vault strategy risk caps and pause controls verified
- [ ] SecClaw alerting + incident runbook tested
- [ ] Risk boundary table reviewed and signed off by operator

---

## Operator notes

- Never market your DEX as an "official Orderly product."
- Avoid guaranteed-return language.
- Builder/operator is responsible for legal and regulatory compliance.
- Re-verify external assumptions periodically (fees, tiers, endpoint behavior, chain support).

## Last verified

- Skill structure and references: 2026-04-01
- External economics/endpoints: **must be re-checked at execution time**
