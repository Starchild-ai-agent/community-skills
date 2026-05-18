"""
ERC-8004 Identity Registry operations.

Spec: https://eips.ethereum.org/EIPS/eip-8004

The Identity Registry is an ERC-721 where each tokenId == agentId.
tokenURI points to an off-chain JSON "agent registration file".
"""

from __future__ import annotations

import json
from typing import Any

from web3 import Web3

from _utils import (
    chain_config,
    explorer_token,
    get_contract,
    get_w3,
    send_contract_tx,
    wallet_address,
)


# ── Registration file helpers ────────────────────────────────────────────────

def build_registration_file(
    name: str,
    description: str,
    services: list[dict] | None = None,
    *,
    image: str = "",
    x402_support: bool = False,
    supported_trust: list[str] | None = None,
    chain: str | None = None,
    agent_id: int | None = None,
) -> dict[str, Any]:
    """
    Build a spec-compliant registration file.

    `services` is a list of dicts like:
        {"name": "A2A", "endpoint": "https://...", "version": "0.3.0"}
        {"name": "MCP", "endpoint": "https://..."}
        {"name": "web", "endpoint": "https://..."}
    """
    cfg = chain_config(chain)
    registrations = []
    if agent_id is not None:
        registrations.append({
            "agentId": agent_id,
            "agentRegistry": f"eip155:{cfg['chain_id']}:{cfg['identity_registry']}",
        })
    return {
        "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
        "name": name,
        "description": description,
        "image": image,
        "services": services or [],
        "x402Support": x402_support,
        "active": True,
        "registrations": registrations,
        "supportedTrust": supported_trust or ["reputation"],
    }


def to_data_uri(reg_file: dict) -> str:
    """Encode the registration file as a `data:application/json;base64,...` URI.
    Useful for fully on-chain registration when no IPFS / HTTPS host is handy.
    """
    import base64
    raw = json.dumps(reg_file, separators=(",", ":")).encode()
    b64 = base64.b64encode(raw).decode()
    return f"data:application/json;base64,{b64}"


def decode_data_uri(uri: str) -> dict | None:
    if not uri.startswith("data:application/json;base64,"):
        return None
    import base64
    b64 = uri.split(",", 1)[1]
    return json.loads(base64.b64decode(b64).decode())


# ── On-chain operations ──────────────────────────────────────────────────────

def register_agent(
    agent_uri: str,
    *,
    chain: str | None = None,
    metadata: list[dict] | None = None,
    wait: bool = True,
) -> dict[str, Any]:
    """
    Register a new agent. Returns {agent_id, tx_hash, explorer_url, ...}.

    `metadata` is an OPTIONAL list of {"key": str, "value": bytes}.
    Note: the reserved `agentWallet` key is set automatically to the owner.
    """
    contract = get_contract("IdentityRegistry", chain)

    if metadata:
        meta_struct = [(m["key"], m["value"]) for m in metadata]
        result = send_contract_tx(
            contract, "register", [agent_uri, meta_struct],
            chain=chain, wait=wait,
        )
    else:
        result = send_contract_tx(
            contract, "register", [agent_uri],
            chain=chain, wait=wait,
        )

    # Parse Registered event for agentId
    agent_id = None
    if result.get("receipt"):
        registered_topic = Web3.keccak(text="Registered(uint256,string,address)").hex()
        for log in result.get("logs", []):
            if (
                log["address"].lower() == contract.address.lower()
                and len(log["topics"]) >= 3
                and log["topics"][0] == registered_topic
            ):
                agent_id = int(log["topics"][1], 16)
                break

    result["agent_id"] = agent_id
    if agent_id is not None:
        result["nft_url"] = explorer_token(chain, contract.address, agent_id)
    return result


def set_agent_uri(agent_id: int, new_uri: str, *, chain: str | None = None, wait: bool = True) -> dict:
    contract = get_contract("IdentityRegistry", chain)
    return send_contract_tx(
        contract, "setAgentURI", [agent_id, new_uri],
        chain=chain, wait=wait,
    )


def get_agent(agent_id: int, *, chain: str | None = None) -> dict[str, Any]:
    """Fetch agent on-chain metadata + parsed registration file if reachable."""
    contract = get_contract("IdentityRegistry", chain)
    try:
        token_uri = contract.functions.tokenURI(agent_id).call()
    except Exception as e:
        raise ValueError(f"Agent {agent_id} not found on {chain or 'default'}: {e}")
    owner = contract.functions.ownerOf(agent_id).call()
    agent_wallet = contract.functions.getAgentWallet(agent_id).call()

    out: dict[str, Any] = {
        "agent_id": agent_id,
        "token_uri": token_uri,
        "owner": owner,
        "agent_wallet": agent_wallet,
        "registration_file": None,
        "fetch_error": None,
    }
    # Try to resolve the registration file
    reg = None
    try:
        if token_uri.startswith("data:application/json;base64,"):
            reg = decode_data_uri(token_uri)
        elif token_uri.startswith("ipfs://"):
            cid = token_uri[len("ipfs://"):]
            from urllib.request import urlopen
            with urlopen(f"https://ipfs.io/ipfs/{cid}", timeout=10) as r:
                reg = json.loads(r.read())
        elif token_uri.startswith(("http://", "https://")):
            from urllib.request import urlopen
            with urlopen(token_uri, timeout=10) as r:
                reg = json.loads(r.read())
    except Exception as e:
        out["fetch_error"] = str(e)
    out["registration_file"] = reg
    return out


def get_metadata(agent_id: int, key: str, *, chain: str | None = None) -> bytes:
    return get_contract("IdentityRegistry", chain).functions.getMetadata(agent_id, key).call()


def total_supply_estimate(*, chain: str | None = None) -> int:
    """
    ERC-8004 IdentityRegistry doesn't expose totalSupply by default — we estimate
    by binary-searching for the highest valid tokenId. Cached upstream is recommended.
    """
    contract = get_contract("IdentityRegistry", chain)
    lo, hi = 0, 1
    # find a hi that's not minted
    while True:
        try:
            contract.functions.ownerOf(hi).call()
            lo = hi
            hi *= 2
            if hi > 2**24:
                break
        except Exception:
            break
    # binary search
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        try:
            contract.functions.ownerOf(mid).call()
            lo = mid
        except Exception:
            hi = mid
    return lo


def discover_agents(
    *,
    chain: str | None = None,
    limit: int = 25,
    from_id: int = 0,
    include_registration: bool = True,
    max_scan: int | None = None,
    max_consecutive_gaps: int = 200,
) -> list[dict[str, Any]]:
    """
    Enumerate agents starting at `from_id`, scanning tokenIds until either
    `limit` agents are found, we hit `max_consecutive_gaps` unminted tokenIds
    in a row (presumed end of registry), or we scan `max_scan` ids total.

    NOTE: ERC-8004 IdentityRegistry has no totalSupply. For production-scale
    discovery use Transfer event indexing or a subgraph; this is a simple
    bounded scan suitable for demos and small registries.
    """
    out: list[dict[str, Any]] = []
    contract = get_contract("IdentityRegistry", chain)
    consecutive_gaps = 0
    scanned = 0
    aid = from_id
    while len(out) < limit:
        if max_scan is not None and scanned >= max_scan:
            break
        try:
            owner = contract.functions.ownerOf(aid).call()
            consecutive_gaps = 0
            if include_registration:
                try:
                    agent = get_agent(aid, chain=chain)
                except Exception:
                    agent = {"agent_id": aid, "owner": owner}
            else:
                agent = {"agent_id": aid, "owner": owner}
            out.append(agent)
        except Exception:
            consecutive_gaps += 1
            if consecutive_gaps >= max_consecutive_gaps:
                break
        aid += 1
        scanned += 1
    return out
