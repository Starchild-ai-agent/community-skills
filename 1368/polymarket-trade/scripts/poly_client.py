"""
Polymarket CLOB client helper.
Handles L2 HMAC auth + common API calls.
"""
import time, hmac, hashlib, base64, json, requests
import os

BASE = "https://clob.polymarket.com"
GAMMA = "https://gamma-api.polymarket.com"

# Credentials from env
API_KEY    = os.environ.get("POLY_API_KEY", "")
SECRET     = os.environ.get("POLY_SECRET", "")
PASSPHRASE = os.environ.get("POLY_PASSPHRASE", "")
WALLET     = os.environ.get("POLY_WALLET", "")

def build_hmac_sig(secret, timestamp, method, path, body=None):
    base64_secret = base64.urlsafe_b64decode(secret)
    message = str(timestamp) + str(method) + str(path)
    if body:
        message += str(body).replace("'", '"')
    h = hmac.new(base64_secret, bytes(message, "utf-8"), hashlib.sha256)
    return base64.urlsafe_b64encode(h.digest()).decode("utf-8")

def l2_headers(method, path, body=None):
    ts = int(time.time())
    sig = build_hmac_sig(SECRET, ts, method.upper(), path, body)
    return {
        "POLY_ADDRESS":    WALLET,
        "POLY_SIGNATURE":  sig,
        "POLY_TIMESTAMP":  str(ts),
        "POLY_API_KEY":    API_KEY,
        "POLY_PASSPHRASE": PASSPHRASE,
        "Content-Type":    "application/json",
    }

def get_balance():
    h = l2_headers("GET", "/balance-allowance")
    r = requests.get(f"{BASE}/balance-allowance", headers=h, params={"asset_type": "COLLATERAL"})
    r.raise_for_status()
    return r.json()

def get_open_orders():
    h = l2_headers("GET", "/data/orders")
    r = requests.get(f"{BASE}/data/orders", headers=h)
    r.raise_for_status()
    return r.json()

def get_trades(limit=20):
    h = l2_headers("GET", "/data/trades")
    r = requests.get(f"{BASE}/data/trades", headers=h, params={"limit": limit})
    r.raise_for_status()
    return r.json()

def cancel_order(order_id):
    body = json.dumps({"orderID": order_id})
    h = l2_headers("DELETE", "/order", body)
    r = requests.delete(f"{BASE}/order", headers=h, data=body)
    r.raise_for_status()
    return r.json()

def cancel_all():
    h = l2_headers("DELETE", "/cancel-all")
    r = requests.delete(f"{BASE}/cancel-all", headers=h)
    r.raise_for_status()
    return r.json()

def get_orderbook(token_id):
    r = requests.get(f"{BASE}/book", params={"token_id": token_id})
    r.raise_for_status()
    return r.json()

def get_market(condition_id):
    r = requests.get(f"{BASE}/markets/{condition_id}")
    r.raise_for_status()
    return r.json()

def search_markets(query, limit=10):
    """Search via Gamma API"""
    r = requests.get(f"{GAMMA}/markets", params={
        "q": query, "limit": limit, "active": True, "closed": False
    })
    r.raise_for_status()
    return r.json()

def get_sampling_markets(limit=20):
    r = requests.get(f"{BASE}/sampling-simplified-markets", params={"limit": limit})
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "balance"
    
    if cmd == "balance":
        data = get_balance()
        print(f"USDC Balance: {float(data['balance'])/1e6:.2f} USDC" if int(data['balance']) > 1e4 else f"USDC Balance on Polymarket: ${float(data['balance'])/1e6:.6f}")
        print(f"Raw: {data}")
    
    elif cmd == "orders":
        data = get_open_orders()
        print(f"Open orders: {data['count']}")
        for o in data.get('data', []):
            print(f"  {o['id']}: {o['side']} {o['size_matched']}/{o['original_size']} @ {o['price']} [{o['asset_id'][:20]}...]")
    
    elif cmd == "trades":
        data = get_trades()
        print(f"Recent trades: {len(data.get('data', []))}")
        for t in data.get('data', [])[:5]:
            print(f"  {t}")
    
    elif cmd == "markets":
        q = sys.argv[2] if len(sys.argv) > 2 else ""
        if q:
            data = search_markets(q)
            for m in data[:5]:
                print(f"  [{m.get('conditionId','?')[:20]}...] {m.get('question','?')}")
                for t in m.get('tokens', [{'outcome':'Yes','price':0},{'outcome':'No','price':0}]):
                    print(f"    {t.get('outcome')}: {t.get('price')}")
        else:
            data = get_sampling_markets()
            for m in data.get('data', [])[:5]:
                print(f"  [{m['condition_id'][:20]}...] tokens: {len(m.get('tokens',[]))}")
