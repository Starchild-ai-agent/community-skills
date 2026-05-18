"""
ERC-8004 Reputation Registry operations.

Spec: https://eips.ethereum.org/EIPS/eip-8004

Feedback is `int128 value` + `uint8 valueDecimals`, plus optional tags / endpoint /
off-chain feedbackURI. Per spec, getSummary REQUIRES non-empty clientAddresses
to mitigate Sybil — caller decides which reviewers to trust.
"""

from __future__ import annotations

from typing import Any

from web3 import Web3

from _utils import get_contract, send_contract_tx


def give_feedback(
    agent_id: int,
    value: int,
    *,
    value_decimals: int = 0,
    tag1: str = "",
    tag2: str = "",
    endpoint: str = "",
    feedback_uri: str = "",
    feedback_hash: bytes | str = b"\x00" * 32,
    chain: str | None = None,
    wait: bool = True,
) -> dict[str, Any]:
    """
    Submit feedback for an agent. `value` is the raw fixed-point integer:
        e.g. 5-star rating: value=5, value_decimals=0
             87/100:        value=87, value_decimals=0
             99.77% uptime: value=9977, value_decimals=2

    Caller cannot be the agent's owner / operator (enforced by contract).
    """
    if isinstance(feedback_hash, str):
        if feedback_hash.startswith("0x"):
            feedback_hash = bytes.fromhex(feedback_hash[2:])
        else:
            feedback_hash = feedback_hash.encode()[:32].ljust(32, b"\x00")
    if len(feedback_hash) != 32:
        raise ValueError("feedback_hash must be exactly 32 bytes")

    contract = get_contract("ReputationRegistry", chain)
    return send_contract_tx(
        contract,
        "giveFeedback",
        [agent_id, int(value), int(value_decimals), tag1, tag2, endpoint, feedback_uri, feedback_hash],
        chain=chain,
        wait=wait,
    )


def revoke_feedback(
    agent_id: int,
    feedback_index: int,
    *,
    chain: str | None = None,
    wait: bool = True,
) -> dict[str, Any]:
    contract = get_contract("ReputationRegistry", chain)
    return send_contract_tx(
        contract, "revokeFeedback", [agent_id, int(feedback_index)],
        chain=chain, wait=wait,
    )


def append_response(
    agent_id: int,
    client_address: str,
    feedback_index: int,
    response_uri: str,
    response_hash: bytes | str = b"\x00" * 32,
    *,
    chain: str | None = None,
    wait: bool = True,
) -> dict[str, Any]:
    if isinstance(response_hash, str):
        if response_hash.startswith("0x"):
            response_hash = bytes.fromhex(response_hash[2:])
        else:
            response_hash = response_hash.encode()[:32].ljust(32, b"\x00")
    contract = get_contract("ReputationRegistry", chain)
    return send_contract_tx(
        contract, "appendResponse",
        [agent_id, Web3.to_checksum_address(client_address), int(feedback_index), response_uri, response_hash],
        chain=chain, wait=wait,
    )


def get_summary(
    agent_id: int,
    client_addresses: list[str],
    *,
    tag1: str = "",
    tag2: str = "",
    chain: str | None = None,
) -> dict[str, Any]:
    """
    Returns {count, summary_value, summary_value_decimals, avg}.

    Per spec, client_addresses MUST be non-empty. Pick reviewers you trust.
    """
    if not client_addresses:
        raise ValueError("client_addresses must be non-empty (Sybil mitigation per ERC-8004)")
    contract = get_contract("ReputationRegistry", chain)
    addrs = [Web3.to_checksum_address(a) for a in client_addresses]
    count, sval, sdec = contract.functions.getSummary(agent_id, addrs, tag1, tag2).call()
    avg = None
    if count > 0:
        avg = (sval / count) / (10 ** sdec)
    return {
        "count": count,
        "summary_value": sval,
        "summary_value_decimals": sdec,
        "avg": avg,
    }


def read_all_feedback(
    agent_id: int,
    *,
    client_addresses: list[str] | None = None,
    tag1: str = "",
    tag2: str = "",
    include_revoked: bool = False,
    chain: str | None = None,
) -> list[dict[str, Any]]:
    contract = get_contract("ReputationRegistry", chain)
    addrs = [Web3.to_checksum_address(a) for a in (client_addresses or [])]
    clients, indexes, values, decimals, tag1s, tag2s, revoked = contract.functions.readAllFeedback(
        agent_id, addrs, tag1, tag2, include_revoked
    ).call()
    out = []
    for i in range(len(clients)):
        dec = decimals[i]
        out.append({
            "client_address": clients[i],
            "feedback_index": indexes[i],
            "value": values[i],
            "value_decimals": dec,
            "human_value": values[i] / (10 ** dec) if dec else values[i],
            "tag1": tag1s[i],
            "tag2": tag2s[i],
            "revoked": revoked[i],
        })
    return out


def get_clients(agent_id: int, *, chain: str | None = None) -> list[str]:
    return get_contract("ReputationRegistry", chain).functions.getClients(agent_id).call()


def get_last_index(agent_id: int, client_address: str, *, chain: str | None = None) -> int:
    return (
        get_contract("ReputationRegistry", chain)
        .functions.getLastIndex(agent_id, Web3.to_checksum_address(client_address))
        .call()
    )


def read_feedback(
    agent_id: int,
    client_address: str,
    feedback_index: int,
    *,
    chain: str | None = None,
) -> dict[str, Any]:
    value, decimals, tag1, tag2, revoked = (
        get_contract("ReputationRegistry", chain)
        .functions.readFeedback(agent_id, Web3.to_checksum_address(client_address), feedback_index)
        .call()
    )
    return {
        "value": value,
        "value_decimals": decimals,
        "human_value": value / (10 ** decimals) if decimals else value,
        "tag1": tag1,
        "tag2": tag2,
        "revoked": revoked,
    }
