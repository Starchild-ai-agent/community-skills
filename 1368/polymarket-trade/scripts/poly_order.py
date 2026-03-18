"""
Polymarket order helpers. Build/post orders via EIP-712 + CLOB API.
"""
import json, time, requests, os, random
from py_clob_client.signing.hmac import build_hmac_signature

BASE  = "https://clob.polymarket.com"
GAMMA = "https://gamma-api.polymarket.com"
CTF_EXCHANGE         = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
CTF_EXCHANGE_NEG     = "0xC5d563A36AE78145C45a50134d48A1215220f80a"
CHAIN_ID = 137
EOA = 0

def _load_env():
    env = {}
    try:
        with open(os.path.expanduser("/data/workspace/.env")) as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except Exception:
        pass
    return env

_env = _load_env()
API_KEY    = os.environ.get("POLY_API_KEY",    _env.get("POLY_API_KEY", ""))
SECRET     = os.environ.get("POLY_SECRET",     _env.get("POLY_SECRET", ""))
PASSPHRASE = os.environ.get("POLY_PASSPHRASE", _env.get("POLY_PASSPHRASE", ""))
WALLET     = os.environ.get("POLY_WALLET",     _env.get("POLY_WALLET", ""))

def l2h(method, path, body=None):
    ts = int(time.time())
    sig = build_hmac_signature(SECRET, ts, method.upper(), path, body)
    return {"POLY_ADDRESS": WALLET, "POLY_SIGNATURE": sig,
            "POLY_TIMESTAMP": str(ts), "POLY_API_KEY": API_KEY,
            "POLY_PASSPHRASE": PASSPHRASE, "Content-Type": "application/json"}

def search_markets(query, limit=5):
    r = requests.get(f"{GAMMA}/markets", params={"q": query, "limit": limit, "active": "true", "closed": "false"})
    r.raise_for_status(); return r.json()

def get_price(token_id, side="BUY"):
    r = requests.get(f"{BASE}/price", params={"token_id": token_id, "side": side})
    return float(r.json().get("price", 0)) if r.status_code == 200 else None

def get_orderbook(token_id):
    r = requests.get(f"{BASE}/book", params={"token_id": token_id})
    r.raise_for_status(); return r.json()

def get_market(condition_id):
    r = requests.get(f"{BASE}/markets/{condition_id}")
    r.raise_for_status(); return r.json()

def get_balance():
    r = requests.get(f"{BASE}/balance-allowance", headers=l2h("GET", "/balance-allowance"), params={"asset_type": "COLLATERAL"})
    r.raise_for_status(); return r.json()

def get_open_orders():
    r = requests.get(f"{BASE}/data/orders", headers=l2h("GET", "/data/orders"))
    r.raise_for_status(); return r.json()

def cancel_order(order_id):
    body = json.dumps({"orderID": order_id})
    r = requests.delete(f"{BASE}/order", headers=l2h("DELETE", "/order", body), data=body)
    return r.status_code, r.json()

def cancel_all():
    r = requests.delete(f"{BASE}/cancel-all", headers=l2h("DELETE", "/cancel-all"))
    return r.status_code, r.json()

def build_order_payload(token_id, side, price, size, neg_risk=False):
    """
    Returns (domain, types, message, meta) for wallet_sign_typed_data.
    meta has salt/amounts needed to post after signing.
    """
    exchange = CTF_EXCHANGE_NEG if neg_risk else CTF_EXCHANGE
    price = round(price, 4); size = round(size, 2)
    if side == "BUY":
        maker_amount = int(price * size * 1_000_000)
        taker_amount = int(size * 1_000_000)
        order_side = 0
    else:
        maker_amount = int(size * 1_000_000)
        taker_amount = int(price * size * 1_000_000)
        order_side = 1
    salt = random.randint(1, 2**64)
    domain = {"name": "Polymarket CTF Exchange", "version": "1", "chainId": CHAIN_ID, "verifyingContract": exchange}
    types = {"Order": [
        {"name": "salt",          "type": "uint256"},
        {"name": "maker",         "type": "address"},
        {"name": "signer",        "type": "address"},
        {"name": "taker",         "type": "address"},
        {"name": "tokenId",       "type": "uint256"},
        {"name": "makerAmount",   "type": "uint256"},
        {"name": "takerAmount",   "type": "uint256"},
        {"name": "expiration",    "type": "uint256"},
        {"name": "nonce",         "type": "uint256"},
        {"name": "feeRateBps",    "type": "uint256"},
        {"name": "side",          "type": "uint8"},
        {"name": "signatureType", "type": "uint8"},
    ]}
    message = {
        "salt": str(salt), "maker": WALLET, "signer": WALLET,
        "taker": "0x0000000000000000000000000000000000000000",
        "tokenId": str(token_id), "makerAmount": str(maker_amount),
        "takerAmount": str(taker_amount), "expiration": "0",
        "nonce": "0", "feeRateBps": "0", "side": order_side, "signatureType": EOA,
    }
    meta = {"salt": salt, "maker_amount": maker_amount, "taker_amount": taker_amount,
            "order_side": order_side, "exchange": exchange}
    return domain, types, message, meta

def post_signed_order(token_id, signature, meta):
    """Post a signed order. meta comes from build_order_payload."""
    order_body = {"order": {
        "salt": meta["salt"], "maker": WALLET, "signer": WALLET,
        "taker": "0x0000000000000000000000000000000000000000",
        "tokenId": str(token_id), "makerAmount": str(meta["maker_amount"]),
        "takerAmount": str(meta["taker_amount"]), "expiration": "0",
        "nonce": "0", "feeRateBps": "0", "side": meta["order_side"],
        "signatureType": EOA, "signature": signature,
    }, "owner": WALLET, "orderType": "GTC"}
    body_str = json.dumps(order_body)
    headers = l2h("POST", "/order", body_str)
    r = requests.post(f"{BASE}/order", headers=headers, data=body_str)
    return r.status_code, r.json()

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "search":
        q = " ".join(sys.argv[2:])
        for m in search_markets(q)[:5]:
            print(f"\n{m.get('question', '?')}")
            print(f"  condition_id: {m.get('conditionId', '?')}")
            print(f"  volume: ${float(m.get('volume', 0)):,.0f}")
            for t in m.get('tokens', []):
                print(f"  {t.get('outcome')}: {t.get('price', '?')}")
    elif cmd == "balance":
        d = get_balance()
        print(f"Balance: ${float(d['balance'])/1e6:.4f} USDC")
    elif cmd == "orders":
        d = get_open_orders()
        print(f"Open orders: {d['count']}")
        for o in d.get('data', []):
            print(f"  {o['id'][:12]}... {o['side']} @ {o['price']} size={o['original_size']}")
    elif cmd == "prepare":
        token_id, side, price, size = sys.argv[2], sys.argv[3].upper(), float(sys.argv[4]), float(sys.argv[5])
        neg_risk = len(sys.argv) > 6 and "neg" in sys.argv[6]
        domain, types, message, meta = build_order_payload(token_id, side, price, size, neg_risk)
        print(json.dumps({"domain": domain, "types": types, "primaryType": "Order", "message": message, "meta": meta}, indent=2))
    else:
        print("Commands: search <query> | balance | orders | prepare <token_id> <BUY|SELL> <price> <size>")
