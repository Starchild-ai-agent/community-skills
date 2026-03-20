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
