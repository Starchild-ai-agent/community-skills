---
name: "@2004/erc-8004"
version: 0.2.0
description: "ERC-8004 Trustless Agents — register agent identity on-chain, publish reputation, discover other agents. Standardized agent infra for the open agent economy (Ethereum Foundation dAI team)."
author: starchild
tags: [erc-8004, agent, identity, reputation, ethereum, base, web3, agent-economy]
---

# 🪪 ERC-8004 Skill

**Community edition** — updated for Starchild skill marketplace.

Implementation of the **ERC-8004 Trustless Agents** standard — the Ethereum Foundation
dAI team's on-chain Identity + Reputation + Validation layer for AI agents.

- Spec: https://eips.ethereum.org/EIPS/eip-8004
- Contracts: https://github.com/erc-8004/erc-8004-contracts
- This skill gives Starchild agents a portable, censorship-resistant on-chain identity
  and a public reputation track record that any other agent can query.

## What's in this skill

| Layer | Status |
|---|---|
| Identity Registry (ERC-721 agent identity) | ✅ Full read + write |
| Reputation Registry (feedback + summary) | ✅ Full read + write |
| Validation Registry | ⏸ Skipped — official README marks it as under active TEE-community revision |

Tx broadcasting goes through the Starchild **wallet skill** backend
(`tools.wallet._wallet_request → POST /agent/transfer`), so the agent's Privy wallet
signs and gas is platform-sponsored when available.

## Supported chains

Singleton deployments per chain (same address triple across testnets, separate triple across mainnets):

| Chain | chainId | Identity | Reputation |
|---|---|---|---|
| base-sepolia (default) | 84532 | `0x8004A818…BD9e` | `0x8004B663…8713` |
| base | 8453 | `0x8004A169…a432` | `0x8004BAa1…9b63` |
| ethereum | 1 | same as base | same as base |
| ethereum-sepolia | 11155111 | same as base-sepolia | same as base-sepolia |

Pass `chain="base"` etc. to any function. Default is `base-sepolia`.

## Usage from scripts

```python
from core.skill_tools import erc_8004

# 1. Register this agent
r = erc_8004.register_agent(
    name="Crypto Research Agent",
    description="On-chain analyst — funding rates, OI, social sentiment, on demand.",
    services=[
        {"name": "web", "endpoint": "https://my-agent.com/"},
        {"name": "A2A", "endpoint": "https://my-agent.com/.well-known/agent-card.json", "version": "0.3.0"},
    ],
    x402_support=True,
    supported_trust=["reputation"],
)
print(r["agent_id"], r["explorer_url"], r["nft_url"])

# 2. Discover other agents
others = erc_8004.discover_agents(limit=20, filter_tag="reputation")

# 3. Fetch one agent's full registration
agent = erc_8004.get_agent(agent_id=42)
print(agent["registration_file"]["name"])

# 4. Leave feedback (caller MUST NOT be the agent's owner)
erc_8004.give_feedback(
    agent_id=42,
    value=5,                # 5/5 stars
    tag1="rating",
    endpoint="https://my-agent.com/research",
    feedback_uri="ipfs://Qm.../review.json",
)

# 5. Aggregate reputation (auto-fetches all reviewers if not specified)
rep = erc_8004.get_reputation(agent_id=42)
print(rep["count"], rep["avg"])

# 6. Pull individual feedback entries
for f in erc_8004.list_feedback(agent_id=42):
    print(f["client_address"], f["human_value"], f["tag1"])
```

## Key semantics & gotchas

- **agentId** is an ERC-721 tokenId, assigned incrementally per chain. Globally unique
  identifier: `eip155:{chainId}:{identityRegistryAddress}:{agentId}`.
- **Registration file** is the off-chain JSON pointed to by `tokenURI`. By default
  this skill encodes it as a `data:application/json;base64,…` URI — fully on-chain,
  no IPFS / HTTPS hosting required.
- **Sybil mitigation**: `getSummary` requires non-empty `client_addresses`. Pass the
  reviewer set you trust. `get_reputation(...)` defaults to "all reviewers ever" if
  you don't specify, which is convenient but not Sybil-resistant — pick a reviewer
  allowlist for high-stakes decisions.
- **Owner cannot self-rate**: the Reputation Registry reverts if `msg.sender` is the
  agent's owner or operator. Use a separate wallet for testing.
- **Validation Registry skipped**: official README marks it as still under revision
  with the TEE community. Will be added in a follow-up.

## Gas + tx-hash resolution (read this before debugging "no tx_hash")

Calls go through `wallet_transfer` which uses platform gas sponsorship by default
(verified working on Base Sepolia via Alchemy paymaster, ERC-4337 EntryPoint v0.7
at `0x0000000071727De22E5E9d8BAf0edAc6f37da032`). Sponsored txs come back from the
wallet backend as:

```json
{"data": {"hash": "", "user_operation_hash": "0x…", "sponsorship_provider": "alchemy", ...}}
```

The skill resolves `user_operation_hash → real tx_hash` by **scanning EntryPoint
`UserOperationEvent` logs** — not by polling a public bundler. This is critical:
Alchemy / Pimlico / Stackup / Biconomy don't share bundler mempools, so a Pimlico
`eth_getUserOperationReceipt` for an Alchemy-submitted op will return `null` forever.
Log scan is bundler-agnostic. See `_resolve_user_op_hash` in `_utils.py`.

If you ever see `No tx_hash in wallet response`, it means the EntryPoint scan
timed out (default 90s, scanning latest 500 blocks) — increase `timeout=` on
`send_contract_tx` or widen `lookback_blocks`.

If gas sponsorship is unavailable on the chain you target, fund the agent wallet
from the corresponding faucet first (Base Sepolia: coinbase / alchemy / quicknode).

## Demo: end-to-end agent commerce

See `output/eth-hk-demo/` for a full scripted demo combining this skill with:
- ERC-8183 (Agentic Commerce) for escrow + evaluator-attested completion
- x402 for HTTP-native USDC micropayments

## Changelog (v0.2.0)
- Bumped for community marketplace publish
- Added "Community edition" header
- Minor doc cleanup for discoverability
