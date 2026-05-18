"""
ERC-8004 Trustless Agents — high-level API for Starchild agents.

Usage from a script:
    from core.skill_tools import erc_8004
    r = erc_8004.register_agent(name="My Agent", description="Does X", services=[...])
    print(r["agent_id"], r["explorer_url"])

Spec: https://eips.ethereum.org/EIPS/eip-8004
Contracts: https://github.com/erc-8004/erc-8004-contracts
"""

from __future__ import annotations

from typing import Any

import _identity
import _reputation
from _utils import (
    chain_config,
    explorer_address,
    explorer_token,
    explorer_tx,
    load_addresses,
    wallet_address,
)


# ─────────────────────────────────────────────────────────────────────────────
# Chain / wallet info
# ─────────────────────────────────────────────────────────────────────────────

def list_chains() -> dict[str, Any]:
    """Return all configured chains and their registry addresses."""
    return load_addresses()


def my_address() -> str:
    """Return the agent's primary EVM wallet address."""
    return wallet_address()


# ─────────────────────────────────────────────────────────────────────────────
# Identity Registry
# ─────────────────────────────────────────────────────────────────────────────

def register_agent(
    name: str,
    description: str,
    *,
    services: list[dict] | None = None,
    image: str = "",
    x402_support: bool = False,
    supported_trust: list[str] | None = None,
    chain: str | None = None,
    inline: bool = True,
    agent_uri: str | None = None,
    wait: bool = True,
) -> dict[str, Any]:
    """
    Register a new agent on ERC-8004 Identity Registry.

    Two modes:
      * inline=True (default): the registration file is encoded as a data: URI
        and stored on-chain via setAgentURI. Zero external dependency.
      * inline=False + agent_uri="https://...": pass an off-chain URI you host.

    Returns: {agent_id, tx_hash, explorer_url, nft_url, ...}
    """
    if not inline and not agent_uri:
        raise ValueError("inline=False requires agent_uri=...")

    if inline:
        reg_file = _identity.build_registration_file(
            name=name,
            description=description,
            services=services,
            image=image,
            x402_support=x402_support,
            supported_trust=supported_trust,
            chain=chain,
        )
        agent_uri = _identity.to_data_uri(reg_file)

    result = _identity.register_agent(agent_uri, chain=chain, wait=wait)
    result["registration_uri"] = agent_uri
    return result


def get_agent(agent_id: int, *, chain: str | None = None) -> dict[str, Any]:
    """Fetch agent on-chain state + registration file (auto-resolves data:/http/ipfs)."""
    return _identity.get_agent(agent_id, chain=chain)


def update_agent_uri(agent_id: int, new_uri: str, *, chain: str | None = None) -> dict:
    return _identity.set_agent_uri(agent_id, new_uri, chain=chain)


def discover_agents(
    *,
    chain: str | None = None,
    limit: int = 25,
    from_id: int = 1,
    include_registration: bool = True,
    filter_tag: str | None = None,
    min_reputation_count: int = 0,
    reviewer_addresses: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Enumerate agents in [from_id, from_id+limit). Optional filters layered off-chain.

    `filter_tag` matches against any service `name` or `supportedTrust` entry in the
    registration file. `min_reputation_count` requires the agent to have at least
    N feedback entries from `reviewer_addresses` (if provided) or any reviewer.
    """
    agents = _identity.discover_agents(
        chain=chain, limit=limit, from_id=from_id, include_registration=include_registration
    )

    if filter_tag:
        kept = []
        for a in agents:
            reg = a.get("registration_file") or {}
            tags = set()
            for s in reg.get("services", []):
                if isinstance(s, dict):
                    tags.add(str(s.get("name", "")).lower())
            for t in reg.get("supportedTrust", []) or []:
                tags.add(str(t).lower())
            if filter_tag.lower() in tags:
                kept.append(a)
        agents = kept

    if min_reputation_count > 0:
        kept = []
        for a in agents:
            try:
                if reviewer_addresses:
                    s = _reputation.get_summary(a["agent_id"], reviewer_addresses, chain=chain)
                    if s["count"] >= min_reputation_count:
                        a["reputation"] = s
                        kept.append(a)
                else:
                    clients = _reputation.get_clients(a["agent_id"], chain=chain)
                    if len(clients) >= min_reputation_count:
                        a["clients"] = clients
                        kept.append(a)
            except Exception:
                continue
        agents = kept

    return agents


# ─────────────────────────────────────────────────────────────────────────────
# Reputation Registry
# ─────────────────────────────────────────────────────────────────────────────

def give_feedback(
    agent_id: int,
    value: int | float,
    *,
    value_decimals: int = 0,
    tag1: str = "",
    tag2: str = "",
    endpoint: str = "",
    feedback_uri: str = "",
    chain: str | None = None,
    wait: bool = True,
) -> dict[str, Any]:
    """
    Submit feedback for an agent.

    Common patterns:
      * 5-star rating:   give_feedback(id, 5, tag1="rating")
      * 87/100 quality:  give_feedback(id, 87, tag1="starred")
      * 99.77% uptime:   give_feedback(id, 9977, value_decimals=2, tag1="uptime")

    NOTE: caller cannot be the agent's owner (contract reverts).
    """
    # accept a float convenience like 4.5 → store as 45 / 10
    if isinstance(value, float):
        if value_decimals == 0:
            value_decimals = 1
        value = int(round(value * (10 ** value_decimals)))
    return _reputation.give_feedback(
        agent_id, int(value),
        value_decimals=value_decimals,
        tag1=tag1, tag2=tag2,
        endpoint=endpoint, feedback_uri=feedback_uri,
        chain=chain, wait=wait,
    )


def get_reputation(
    agent_id: int,
    *,
    reviewer_addresses: list[str] | None = None,
    tag1: str = "",
    tag2: str = "",
    chain: str | None = None,
) -> dict[str, Any]:
    """
    Aggregate reputation summary. If reviewer_addresses is None, defaults to
    every client that has ever rated this agent (no Sybil filter).
    """
    if reviewer_addresses is None:
        reviewer_addresses = _reputation.get_clients(agent_id, chain=chain)
    if not reviewer_addresses:
        return {"count": 0, "summary_value": 0, "summary_value_decimals": 0, "avg": None}
    return _reputation.get_summary(
        agent_id, reviewer_addresses, tag1=tag1, tag2=tag2, chain=chain
    )


def list_feedback(
    agent_id: int,
    *,
    reviewer_addresses: list[str] | None = None,
    tag1: str = "",
    tag2: str = "",
    include_revoked: bool = False,
    chain: str | None = None,
) -> list[dict[str, Any]]:
    return _reputation.read_all_feedback(
        agent_id, client_addresses=reviewer_addresses,
        tag1=tag1, tag2=tag2,
        include_revoked=include_revoked, chain=chain,
    )


def get_reviewers(agent_id: int, *, chain: str | None = None) -> list[str]:
    return _reputation.get_clients(agent_id, chain=chain)


def revoke_feedback(
    agent_id: int, feedback_index: int,
    *, chain: str | None = None,
) -> dict[str, Any]:
    return _reputation.revoke_feedback(agent_id, feedback_index, chain=chain)
