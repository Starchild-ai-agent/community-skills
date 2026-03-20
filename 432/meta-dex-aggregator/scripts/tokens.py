"""Token list resolution for Meta DEX Aggregator.

Three-tier resolution:
  1. Trusted majors — hardcoded canonical addresses, auto-resolved (no confirmation)
  2. Single match — only one token matches the symbol, auto-resolved
  3. Ambiguous — multiple matches, returns candidates for user confirmation
"""

import requests
from decimal import Decimal
from chains import CHAINS, ZERO_ADDR, NATIVE_SYMBOLS

# ── Tier 1: Trusted canonical addresses per chain ──────────────────────
# These are THE canonical tokens — never need confirmation.
# Format: { chain_id: { "SYMBOL": ("address", decimals) } }
TRUSTED_TOKENS = {
    # Ethereum (1)
    1: {
        "WETH":  ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 18),
        "USDC":  ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
        "USDT":  ("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
        "DAI":   ("0x6B175474E89094C44Da98b954EedeAC495271d0F", 18),
        "WBTC":  ("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", 8),
        "LINK":  ("0x514910771AF9Ca656af840dff83E8264EcF986CA", 18),
        "UNI":   ("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", 18),
        "AAVE":  ("0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", 18),
        "MKR":   ("0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2", 18),
        "STETH": ("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84", 18),
        "WSTETH":("0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0", 18),
        "CBETH": ("0xBe9895146f7AF43049ca1c1AE358B0541Ea49704", 18),
        "RETH":  ("0xae78736Cd615f374D3085123A210448E74Fc6393", 18),
        "RPL":   ("0xD33526068D116cE69F19A9ee46F0bd304F21A51f", 18),
        "LDO":   ("0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32", 18),
        "CRV":   ("0xD533a949740bb3306d119CC777fa900bA034cd52", 18),
        "COMP":  ("0xc00e94Cb662C3520282E6f5717214004A7f26888", 18),
        "SNX":   ("0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F", 18),
        "PEPE":  ("0x6982508145454Ce325dDbE47a25d4ec3d2311933", 18),
        "SHIB":  ("0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE", 18),
    },
    # Arbitrum (42161)
    42161: {
        "WETH":  ("0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", 18),
        "USDC":  ("0xaf88d065e77c8cC2239327C5EDb3A432268e5831", 6),   # native USDC
        "USDC.e":("0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8", 6),   # bridged
        "USDT":  ("0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", 6),
        "DAI":   ("0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1", 18),
        "WBTC":  ("0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f", 8),
        "ARB":   ("0x912CE59144191C1204E64559FE8253a0e49E6548", 18),
        "LINK":  ("0xf97f4df75117a78c1A5a0DBb814Af92458539FB4", 18),
        "UNI":   ("0xFa7F8980b0f1E64A2062791cc3b0871572f1F7f0", 18),
        "GMX":   ("0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a", 18),
        "PENDLE":("0x0c880f6761F1af8d9Aa9C466984b80DAb9a8c9e8", 18),
        "GRT":   ("0x9623063377AD1B27544C965cCd7342f7EA7e88C7", 18),
        "RDNT":  ("0x3082CC23568eA640225c2467653dB90e9250AaA0", 18),
        "WSTETH":("0x5979D7b546E38E9Ab8049e39eAcB0B30261edE29", 18),
        "RETH":  ("0xEC70Dcb4A1EFa46b8F2D97C310C9c4790ba5ffA8", 18),
    },
    # Base (8453)
    8453: {
        "WETH":  ("0x4200000000000000000000000000000000000006", 18),
        "USDC":  ("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", 6),
        "USDBC": ("0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA", 6),   # bridged
        "DAI":   ("0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb", 18),
        "CBETH": ("0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22", 18),
        "WSTETH":("0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452", 18),
        "AERO":  ("0x940181a94A35A4569E4529A3CDfB74e38FD98631", 18),
        "DEGEN": ("0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed", 18),
        "BRETT": ("0x532f27101965dd16442E59d40670FaF5eBB142E4", 18),
        "TOSHI": ("0xAC1Bd2486aAf3B5C0fc3Fd868558b082a531B2B4", 18),
    },
    # Optimism (10)
    10: {
        "WETH":  ("0x4200000000000000000000000000000000000006", 18),
        "USDC":  ("0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85", 6),   # native
        "USDC.e":("0x7F5c764cBc14f9669B88837ca1490cCa17c31607", 6),   # bridged
        "USDT":  ("0x94b008aA00579c1307B0EF2c499aD98a8ce58e58", 6),
        "DAI":   ("0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1", 18),
        "WBTC":  ("0x68f180fcCe6836688e9084f035309E29Bf0A2095", 8),
        "OP":    ("0x4200000000000000000000000000000000000042", 18),
        "LINK":  ("0x350a791Bfc2C21F9Ed5d10980Dad2e2638ffa7f6", 18),
        "SNX":   ("0x8700dAec35aF8Ff88c16BdF0418774CB3D7599B4", 18),
        "WSTETH":("0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb", 18),
        "RETH":  ("0x9Bcef72bE871e61ED4fBbc7630889beE758eb81D", 18),
        "VELO":  ("0x9560e827aF36c94D2Ac33a39bCE1Fe78631088Db", 18),
    },
    # Polygon (137)
    137: {
        "WETH":  ("0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", 18),
        "WMATIC":("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270", 18),
        "WPOL":  ("0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270", 18),
        "USDC":  ("0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359", 6),   # native
        "USDC.e":("0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", 6),   # bridged
        "USDT":  ("0xc2132D05D31c914a87C6611C10748AEb04B58e8F", 6),
        "DAI":   ("0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063", 18),
        "WBTC":  ("0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6", 8),
        "LINK":  ("0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39", 18),
        "AAVE":  ("0xD6DF932A45C0f255f85145f286eA0b292B21C90B", 18),
        "UNI":   ("0xb33EaAd8d922B1083446DC23f610c2567fB5180f", 18),
    },
    # BSC (56)
    56: {
        "WBNB":  ("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c", 18),
        "USDC":  ("0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", 18),
        "USDT":  ("0x55d398326f99059fF775485246999027B3197955", 18),
        "DAI":   ("0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3", 18),
        "WETH":  ("0x2170Ed0880ac9A755fd29B2688956BD959F933F8", 18),
        "BTCB":  ("0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c", 18),
        "CAKE":  ("0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82", 18),
        "XRP":   ("0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE", 18),
    },
    # Avalanche (43114)
    43114: {
        "WAVAX": ("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7", 18),
        "USDC":  ("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E", 6),
        "USDT":  ("0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7", 6),
        "DAI.e": ("0xd586E7F844cEa2F87f50152665BCbc2C279D8d70", 18),
        "WETH.e":("0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB", 18),
        "WBTC.e":("0x50b7545627a5162F82A992c33b87aDc75187B218", 8),
        "JOE":   ("0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd", 18),
    },
    # Gnosis (100)
    100: {
        "WXDAI": ("0xe91D153E0b41518A2Ce8Dd3D7944Fa863463a97d", 18),
        "USDC":  ("0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83", 6),
        "USDT":  ("0x4ECaBa5870353805a9F068101A40E0f32ed605C6", 6),
        "WETH":  ("0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1", 18),
        "GNO":   ("0x9C58BAcC331c9aa871AFD802DB6379a98e80CEdb", 18),
    },
}

# ── Token cache ────────────────────────────────────────────────────────
_token_cache = {}

def get_token_list(chain_id: int) -> dict:
    if chain_id in _token_cache:
        return _token_cache[chain_id]
    url = f"https://d3g10bzo9rdluh.cloudfront.net/tokenlists-{chain_id}.json"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    _token_cache[chain_id] = data
    return data

def search_tokens(chain: str, query: str, limit: int = 20):
    chain_id = CHAINS[chain]
    tokens = get_token_list(chain_id)
    query_lower = query.lower()
    results = []
    for addr, tok in tokens.items():
        if query_lower in tok.get("symbol", "").lower() or query_lower in tok.get("name", "").lower():
            results.append(tok)
    results.sort(key=lambda t: t.get("volume24h", 0) or 0, reverse=True)
    return results[:limit]


def resolve_token(chain: str, symbol_or_address: str) -> dict:
    """Resolve symbol or address to { address, decimals, symbol, confidence }.

    confidence levels:
      "trusted"   — hardcoded canonical address, no confirmation needed
      "exact"     — user provided a 0x address directly
      "single"    — only one symbol match found, safe to auto-use
      "high"      — multiple matches but top result has >>10x volume of #2
      "ambiguous" — multiple plausible matches, needs user confirmation

    When confidence is "ambiguous", the returned dict includes a "candidates"
    list with the top matches so the agent can present them to the user.
    """
    chain_id = CHAINS[chain]
    native_sym = NATIVE_SYMBOLS.get(chain, "ETH")
    sym_upper = symbol_or_address.strip().upper()

    # ── Native gas token ──
    if sym_upper in (native_sym, "ETH") and native_sym == "ETH":
        return {"address": ZERO_ADDR, "decimals": 18, "symbol": native_sym, "confidence": "trusted"}
    if sym_upper == native_sym:
        return {"address": ZERO_ADDR, "decimals": 18, "symbol": native_sym, "confidence": "trusted"}

    # ── User gave a 0x address directly ──
    if symbol_or_address.startswith("0x") and len(symbol_or_address) == 42:
        tokens = get_token_list(chain_id)
        tok = tokens.get(symbol_or_address.lower())
        if tok:
            return {"address": tok["address"], "decimals": tok["decimals"],
                    "symbol": tok["symbol"], "confidence": "exact"}
        return {"address": symbol_or_address.lower(), "decimals": 18,
                "symbol": "UNKNOWN", "confidence": "exact"}

    # ── Tier 1: Trusted canonical tokens ──
    trusted = TRUSTED_TOKENS.get(chain_id, {})
    if sym_upper in trusted:
        addr, dec = trusted[sym_upper]
        return {"address": addr, "decimals": dec, "symbol": sym_upper, "confidence": "trusted"}

    # ── Tier 2+3: Search token list by symbol ──
    tokens = get_token_list(chain_id)
    matches = [tok for addr, tok in tokens.items()
               if tok.get("symbol", "").upper() == sym_upper]

    if not matches:
        raise ValueError(f"Token '{symbol_or_address}' not found on {chain}. Use 'search' command.")

    matches.sort(key=lambda t: t.get("volume24h", 0) or 0, reverse=True)

    # Single match — no ambiguity
    if len(matches) == 1:
        best = matches[0]
        return {"address": best["address"], "decimals": best["decimals"],
                "symbol": best["symbol"], "confidence": "single"}

    # Multiple matches — check if top is dominant (10x volume of runner-up)
    top_vol = matches[0].get("volume24h", 0) or 0
    second_vol = matches[1].get("volume24h", 0) or 0

    if top_vol > 0 and (second_vol == 0 or top_vol / max(second_vol, 1) > 10):
        best = matches[0]
        return {"address": best["address"], "decimals": best["decimals"],
                "symbol": best["symbol"], "confidence": "high"}

    # Ambiguous — return candidates for confirmation
    candidates = []
    for m in matches[:5]:
        candidates.append({
            "symbol": m["symbol"],
            "name": m.get("name", ""),
            "address": m["address"],
            "decimals": m["decimals"],
            "volume24h": m.get("volume24h"),
        })
    best = matches[0]
    return {"address": best["address"], "decimals": best["decimals"],
            "symbol": best["symbol"], "confidence": "ambiguous",
            "candidates": candidates}


def to_wei(amount: str, decimals: int) -> str:
    return str(int(Decimal(amount) * Decimal(10 ** decimals)))

def from_wei(amount_wei: str, decimals: int) -> str:
    return str(Decimal(str(amount_wei)) / Decimal(10 ** decimals))
