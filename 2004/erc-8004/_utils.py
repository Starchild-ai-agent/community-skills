"""
ERC-8004 utilities: web3 client, ABI loading, chain config, tx broadcast.

Broadcasting goes through the Starchild wallet skill backend
(`wallet_transfer` POST /agent/transfer) so the platform-managed Privy
wallet signs and pays gas (sponsored when available, user-funded otherwise).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Workaround for skill_tools loader: it deletes web3/eth_hash from sys.modules
# between skill loads, which causes duplicate `BackendAPI` class objects to
# accumulate. When eth_utils.crypto.keccak (bound at its module init) later
# routes through a stale eth_hash.auto.Keccak256 instance, the lazy
# `_initialize()` calls `auto_choose_backend()` which `isinstance`-checks the
# pycryptodome backend against the *latest* `BackendAPI` class — and fails.
#
# Fix: explicitly bind a stable pycryptodome backend to the current
# eth_hash.auto.keccak singleton BEFORE web3 imports run. This makes the
# hasher purely data-driven (no further class checks), surviving sys.modules
# churn between skill loads.
# ---------------------------------------------------------------------------
try:
    import eth_hash.auto as _eh_auto
    from eth_hash.backends.pycryptodome import backend as _eh_pcd_backend
    _eh_auto.keccak.hasher = _eh_pcd_backend.keccak256
    _eh_auto.keccak.preimage = _eh_pcd_backend.preimage
except Exception:
    pass  # if it fails we'll get the original error later — surface, don't hide

from web3 import Web3
from web3.contract import Contract

_HERE = Path(__file__).resolve().parent
_CONTRACTS = _HERE / "contracts"

_ADDRESSES: dict[str, Any] | None = None
_ABI_CACHE: dict[str, list] = {}
_W3_CACHE: dict[str, Web3] = {}


def load_addresses() -> dict[str, Any]:
    global _ADDRESSES
    if _ADDRESSES is None:
        _ADDRESSES = json.loads((_CONTRACTS / "addresses.json").read_text())
    return _ADDRESSES


def chain_config(chain: str | None = None) -> dict[str, Any]:
    addrs = load_addresses()
    if chain is None:
        chain = addrs["default_chain"]
    if chain not in addrs["chains"]:
        raise ValueError(f"Unknown chain '{chain}'. Known: {list(addrs['chains'].keys())}")
    cfg = dict(addrs["chains"][chain])
    cfg["name"] = chain
    return cfg


def _live_web3_cls():
    """Always fetch the *current* Web3 class from sys.modules, not the one
    captured at skill-load time. The skill loader's sys.modules cleanup can
    leave us holding a stale Web3 class whose .eth namespace has a broken
    parent-reference descriptor. Re-import per call to stay in sync."""
    import importlib
    import web3 as _w3pkg
    importlib.reload(_w3pkg) if _w3pkg.Web3 is not Web3 else None  # noqa
    return _w3pkg.Web3


def get_w3(chain: str | None = None):
    """Build a fresh Web3 each call — caching across skill-loader sys.modules
    churn can leave instances pointing at stale class hierarchies."""
    cfg = chain_config(chain)
    name = cfg["name"]
    rpc = os.environ.get(f"RPC_{name.upper().replace('-', '_')}", cfg["rpc"])
    W3 = _live_web3_cls()
    return W3(W3.HTTPProvider(rpc, request_kwargs={"timeout": 30}))


def load_abi(name: str) -> list:
    """name in {IdentityRegistry, ReputationRegistry, ValidationRegistry}"""
    if name not in _ABI_CACHE:
        raw = json.loads((_CONTRACTS / "abis" / f"{name}.json").read_text())
        _ABI_CACHE[name] = raw if isinstance(raw, list) else raw.get("abi", [])
    return _ABI_CACHE[name]


def get_contract(name: str, chain: str | None = None):
    cfg = chain_config(chain)
    addr_key = {
        "IdentityRegistry": "identity_registry",
        "ReputationRegistry": "reputation_registry",
        "ValidationRegistry": "validation_registry",
    }[name]
    addr = cfg.get(addr_key)
    if not addr:
        raise RuntimeError(
            f"{name} not deployed on '{cfg['name']}'. "
            f"Note: ValidationRegistry is under active TEE-community revision."
        )
    W3 = _live_web3_cls()
    w3 = get_w3(chain)
    return w3.eth.contract(address=W3.to_checksum_address(addr), abi=load_abi(name))


def build_calldata(contract: Contract, fn_name: str, args: list) -> str:
    """Encode a function call into hex calldata (0x-prefixed).

    Supports overloaded functions: pass a Solidity-style signature like
    'register(string)' or 'register(string,(string,bytes)[])' as fn_name to
    pick a specific overload. Plain names work when unambiguous.
    """
    if "(" in fn_name:
        fn = contract.get_function_by_signature(fn_name)
    else:
        try:
            fn = contract.get_function_by_name(fn_name)
        except Exception:
            # Fallback: try to disambiguate by arg count
            candidates = [
                f for f in contract.all_functions()
                if f.abi.get("name") == fn_name and len(f.abi.get("inputs", [])) == len(args)
            ]
            if len(candidates) == 1:
                fn = candidates[0]
            else:
                raise
    return fn(*args)._encode_transaction_data()


def explorer_tx(chain: str | None, tx_hash: str) -> str:
    cfg = chain_config(chain)
    return f"{cfg['explorer']}/tx/{tx_hash}"


def explorer_address(chain: str | None, addr: str) -> str:
    cfg = chain_config(chain)
    return f"{cfg['explorer']}/address/{addr}"


def explorer_token(chain: str | None, addr: str, token_id: int) -> str:
    cfg = chain_config(chain)
    return f"{cfg['explorer']}/token/{addr}?a={token_id}"


# ── ERC-4337 user-op hash → real tx hash resolver ───────────────────────────

# EntryPoint addresses (same across all EVM chains — singleton deployments)
_ENTRY_POINT_V07 = "0x0000000071727De22E5E9d8BAf0edAc6f37da032"
_ENTRY_POINT_V06 = "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789"

# UserOperationEvent topic (identical signature in v0.6 + v0.7)
_USER_OP_EVENT_TOPIC = (
    "0x49628fd1471006c1482da88028e9ce4dbb080b815c9b0344d39e5a8e6ec1419f"
)


def _resolve_user_op_hash(
    user_op_hash: str,
    *,
    chain: str | None = None,
    timeout: float = 90.0,
    lookback_blocks: int = 500,
) -> str | None:
    """Resolve a sponsored ERC-4337 user_op_hash to the real on-chain tx_hash
    by scanning EntryPoint UserOperationEvent logs. Bundler-agnostic (works
    with Alchemy / Pimlico / Stackup / Biconomy — none of which share mempools).

    Polls until found or `timeout` seconds elapse.
    """
    import time
    W3 = _live_web3_cls()
    w3 = get_w3(chain)

    # Normalize the topic — must be 0x-prefixed lowercase 32 bytes
    op_hash = user_op_hash.lower()
    if not op_hash.startswith("0x"):
        op_hash = "0x" + op_hash

    deadline = time.time() + timeout
    last_scanned_to = None
    while time.time() < deadline:
        try:
            latest = w3.eth.block_number
            from_block = max(0, latest - lookback_blocks)
            for ep in (_ENTRY_POINT_V07, _ENTRY_POINT_V06):
                logs = w3.eth.get_logs({
                    "fromBlock": from_block,
                    "toBlock": latest,
                    "address": W3.to_checksum_address(ep),
                    "topics": [_USER_OP_EVENT_TOPIC, op_hash],
                })
                if logs:
                    tx = logs[0]["transactionHash"]
                    return tx.hex() if hasattr(tx, "hex") else tx
            last_scanned_to = latest
        except Exception:
            pass
        time.sleep(3.0)
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Broadcasting via Starchild wallet skill
# ─────────────────────────────────────────────────────────────────────────────

def wallet_address() -> str:
    """Return the agent's primary EVM wallet address."""
    try:
        from tools.wallet import _wallet_request
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            info = loop.run_until_complete(_wallet_request("GET", "/agent/wallet"))
        except RuntimeError:
            info = asyncio.run(_wallet_request("GET", "/agent/wallet"))
        # Response shape: {"wallets": [{"chain_type": "ethereum", "wallet_address": "0x..."}, ...]}
        for w in info.get("wallets", []):
            if w.get("chain_type") == "ethereum":
                W3 = _live_web3_cls()
                return W3.to_checksum_address(w.get("wallet_address") or w.get("address"))
        raise RuntimeError(f"No EVM wallet in response: {info}")
    except ImportError:
        # Outside Fly machine — fall back to env override (testing only)
        addr = os.environ.get("AGENT_EVM_ADDRESS")
        if not addr:
            raise RuntimeError("Cannot resolve agent wallet (no tools.wallet, no AGENT_EVM_ADDRESS)")
        return Web3.to_checksum_address(addr)


def send_contract_tx(
    contract: Contract,
    fn_name: str,
    args: list,
    *,
    chain: str | None = None,
    value: int = 0,
    gas_limit: int | None = None,
    sponsor: bool | None = None,
    wait: bool = True,
    poll_interval: float = 2.0,
    timeout: float = 90.0,
) -> dict[str, Any]:
    """
    Encode + broadcast a contract call via the agent's Privy wallet.

    Returns: {tx_hash, explorer_url, status, receipt?}
    """
    from tools.wallet import _wallet_request
    import asyncio
    import time

    cfg = chain_config(chain)
    data = build_calldata(contract, fn_name, args)

    body = {
        "to": contract.address,
        "amount": str(value),
        "chain_id": cfg["chain_id"],
        "data": data,
    }
    if gas_limit is not None:
        body["gas_limit"] = str(gas_limit)
    if sponsor is not None:
        body["sponsor"] = sponsor

    try:
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(_wallet_request("POST", "/agent/transfer", body))
    except RuntimeError:
        resp = asyncio.run(_wallet_request("POST", "/agent/transfer", body))

    # The wallet API returns either:
    #   (a) {"hash": "0x...", ...}  (eth_sendRawTransaction path, no sponsorship)
    #   (b) {"data": {"hash": "", "user_operation_hash": "0x...",
    #                 "sponsorship_provider": "alchemy", ...}}  (ERC-4337 path)
    data = resp.get("data", resp)
    tx_hash = (
        data.get("tx_hash") or data.get("hash")
        or data.get("transaction_hash")
        or resp.get("tx_hash") or resp.get("hash") or resp.get("transaction_hash")
    )
    user_op_hash = data.get("user_operation_hash") or resp.get("user_operation_hash")

    # If we got a sponsored user-op back, resolve it to the real tx_hash via
    # a public ERC-4337 bundler (Pimlico for Base Sepolia).
    if not tx_hash and user_op_hash:
        tx_hash = _resolve_user_op_hash(user_op_hash, chain=chain, timeout=timeout)

    if not tx_hash:
        raise RuntimeError(
            f"No tx_hash in wallet response and EntryPoint log scan timed out "
            f"after {timeout}s. user_op_hash={user_op_hash} raw={resp}"
        )

    # Normalize hex bytes → 0x-prefixed string
    if isinstance(tx_hash, (bytes, bytearray)):
        tx_hash = "0x" + tx_hash.hex()
    elif hasattr(tx_hash, "hex"):
        tx_hash = tx_hash.hex()
    if not tx_hash.startswith("0x"):
        tx_hash = "0x" + tx_hash

    out = {
        "tx_hash": tx_hash,
        "explorer_url": explorer_tx(chain, tx_hash),
        "status": "pending",
        "raw_response": resp,
    }

    if wait:
        w3 = get_w3(chain)
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                out["status"] = "success" if receipt.status == 1 else "failed"
                out["receipt"] = dict(receipt)
                # decode log topics for caller convenience
                out["logs"] = [
                    {
                        "address": log["address"],
                        "topics": [t.hex() for t in log["topics"]],
                        "data": log["data"].hex() if isinstance(log["data"], bytes) else log["data"],
                    }
                    for log in receipt.logs
                ]
                return out
            except Exception:
                time.sleep(poll_interval)
        out["status"] = "timeout"

    return out
