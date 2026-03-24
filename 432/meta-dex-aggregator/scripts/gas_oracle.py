"""Per-chain gas price oracle for Meta DEX Aggregator.

Fetches live gas prices via public RPC eth_gasPrice calls.
Falls back to sane chain-specific defaults if RPC fails.
Caches results for 15 seconds to avoid hammering RPCs.
"""

import time
import http_client as http

# Public RPCs per chain (free, no key needed) — multiple fallbacks for reliability
# Multiple RPCs per chain for fallback reliability
_RPC_ENDPOINTS = {
    "ethereum": ["https://eth.llamarpc.com", "https://cloudflare-eth.com", "https://rpc.ankr.com/eth"],
    "base": ["https://mainnet.base.org", "https://base.llamarpc.com", "https://rpc.ankr.com/base"],
    "arbitrum": ["https://arb1.arbitrum.io/rpc", "https://arbitrum.llamarpc.com", "https://rpc.ankr.com/arbitrum"],
    "optimism": ["https://mainnet.optimism.io", "https://optimism.llamarpc.com", "https://rpc.ankr.com/optimism"],
    "polygon": ["https://polygon.drpc.org", "https://rpc.ankr.com/polygon", "https://polygon-bor-rpc.publicnode.com"],
    "bsc": ["https://bsc-dataseed1.binance.org", "https://bsc.llamarpc.com", "https://rpc.ankr.com/bsc"],
    "avax": ["https://api.avax.network/ext/bc/C/rpc", "https://rpc.ankr.com/avalanche"],
    "gnosis": ["https://rpc.gnosischain.com", "https://rpc.ankr.com/gnosis"],
    "fantom": ["https://rpc.ftm.tools", "https://rpc.ankr.com/fantom"],
    "linea": ["https://rpc.linea.build", "https://linea.drpc.org"],
    "scroll": ["https://rpc.scroll.io", "https://scroll.drpc.org"],
    "zksync": ["https://mainnet.era.zksync.io", "https://zksync.drpc.org"],
    "sonic": ["https://rpc.soniclabs.com"],
}

# Sane defaults in gwei if RPC fails
_DEFAULT_GAS_GWEI = {
    "ethereum": 20.0,
    "base": 0.01,
    "arbitrum": 0.1,
    "optimism": 0.01,
    "polygon": 30.0,
    "bsc": 3.0,
    "avax": 25.0,
    "gnosis": 2.0,
    "fantom": 50.0,
    "linea": 0.05,
    "scroll": 0.05,
    "zksync": 0.25,
    "sonic": 1.0,
    "unichain": 0.01,
}

# Cache: {chain: (timestamp, gwei_value)}
_cache = {}
_CACHE_TTL = 15  # seconds


def get_gas_price_gwei(chain):
    """Get current gas price in gwei for a chain. Cached for 15s."""
    now = time.monotonic()

    # Check cache
    if chain in _cache:
        ts, val = _cache[chain]
        if now - ts < _CACHE_TTL:
            return val

    # Try live RPC (multiple fallbacks per chain)
    rpc_urls = _RPC_ENDPOINTS.get(chain, [])
    for rpc_url in rpc_urls:
        try:
            resp = http.post(rpc_url, json={
                "jsonrpc": "2.0", "method": "eth_gasPrice", "params": [], "id": 1
            }, timeout=(2, 3))
            if resp.status_code == 200:
                result = resp.json().get("result")
                if result:
                    gwei = int(result, 16) / 1e9
                    _cache[chain] = (now, gwei)
                    return gwei
        except Exception:
            continue

    # Fallback to defaults
    default = _DEFAULT_GAS_GWEI.get(chain, 20.0)
    _cache[chain] = (now, default)
    return default


def estimate_gas_usd(chain, gas_units, gas_token_price):
    """Compute gas cost in USD from gas units, live gas price, and token price.

    Args:
        chain: Chain name (e.g. "base")
        gas_units: Estimated gas units (int/float)
        gas_token_price: USD price of native gas token

    Returns:
        float: Estimated gas cost in USD, or None if inputs missing
    """
    if not gas_units or not gas_token_price:
        return None
    try:
        gwei = get_gas_price_gwei(chain)
        return float(gas_units) * gwei * 1e-9 * float(gas_token_price)
    except Exception:
        return None
