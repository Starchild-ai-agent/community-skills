"""Chain and token constants for Meta DEX Aggregator."""

CHAINS = {
    "ethereum": 1, "bsc": 56, "polygon": 137, "optimism": 10,
    "arbitrum": 42161, "avax": 43114, "gnosis": 100, "fantom": 250,
    "zksync": 324, "base": 8453, "linea": 59144, "scroll": 534352,
    "sonic": 146, "unichain": 130,
}

ZERO_ADDR = "0x0000000000000000000000000000000000000000"
NATIVE_PLACEHOLDER = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

NATIVE_SYMBOLS = {
    "ethereum": "ETH", "bsc": "BNB", "polygon": "POL", "optimism": "ETH",
    "arbitrum": "ETH", "avax": "AVAX", "gnosis": "xDAI", "fantom": "FTM",
    "zksync": "ETH", "base": "ETH", "linea": "ETH", "scroll": "ETH",
    "sonic": "S", "unichain": "ETH",
}

DEFILLAMA_REFERRER = "0x08a3c2A819E3de7ACa384c798269B3Ce1CD0e437"

# ── CowSwap Configuration ─────────────────────────────────────────────────────
COWSWAP_CHAINS = {"ethereum", "arbitrum", "gnosis", "base"}
COWSWAP_CHAIN_PREFIX = {
    "ethereum": "mainnet", "arbitrum": "arbitrum_one", "gnosis": "xdai", "base": "base",
}
COWSWAP_NATIVE_TOKEN = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
# CowSwap wrapped native addresses per chain (required — CowSwap can't quote raw native)
COWSWAP_WRAPPED_NATIVE = {
    "ethereum": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
    "arbitrum": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",  # WETH
    "gnosis":   "0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d",  # WXDAI
    "base":     "0x4200000000000000000000000000000000000006",  # WETH
}

# ── 1inch Configuration ───────────────────────────────────────────────────────
# 1inch supports all chains in CHAINS dict, uses NATIVE_PLACEHOLDER for native tokens
INCH_API_BASE = "https://api.1inch.dev/swap/v5.2"
