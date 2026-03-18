"""
Polymarket Research & Trading Script.
Market lookup, orderbook analysis, R/R calculation, order execution.
All CLOB requests route through VPN to bypass geo-blocking.

Usage:
  python3 poly_research.py lookup <url_or_slug>
  python3 poly_research.py search <query>
  python3 poly_research.py orderbook <token_id>
  python3 poly_research.py rr <token_id> <YES|NO> <size_usd>
  python3 poly_research.py prepare <token_id> <BUY|SELL> <price> <size> [neg_risk] [tick_size]
  python3 poly_research.py post <token_id> <signature> <meta_json>
  python3 poly_research.py balance
  python3 poly_research.py orders
  python3 poly_research.py positions
  python3 poly_research.py trades
  python3 poly_research.py cancel <order_id>
  python3 poly_research.py cancel_all
"""

import json, time, sys, os, re, random, hashlib, hmac, base64
import requests as _requests

# VPN proxy for CLOB (geo-blocked)
VPN_REGION = os.environ.get("POLY_VPN_REGION", "ch")
VPN_PROXY = {
    "https": f"http://{VPN_REGION}:x@sc-vpn.internal:8080",
    "http":  f"http://{VPN_REGION}:x@sc-vpn.internal:8080",
}

BASE  = "https://clob.polymarket.com"
GAMMA = "https://gamma-api.polymarket.com"
CTF_EXCHANGE     = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
CTF_EXCHANGE_NEG = "0xC5d563A36AE78145C45a50134d48A1215220f80a"
CHAIN_ID = 137
EOA = 0           # signature_type 0: raw EOA (direct trading, no proxy wallet needed)
GNOSIS_SAFE = 2   # signature_type 2: proxy/Safe wallet (standard for Polymarket.com web users)
SIG_TYPE = EOA    # We use EOA mode — wallet is both signer and maker

def _load_env():
    env = {}
    try:
        with open("/data/workspace/.env") as f:
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
WALLET       = os.environ.get("POLY_WALLET",       _env.get("POLY_WALLET", ""))       # EOA wallet — is both signer AND maker in EOA mode
PROXY_WALLET = os.environ.get("POLY_PROXY_WALLET", _env.get("POLY_PROXY_WALLET", "")) # Only used in Safe mode (unused in EOA mode)
MAKER_ADDR   = WALLET  # EOA mode: maker = signer = wallet

# HTTP helpers with VPN
def clob_get(url, **kw):
    kw.setdefault("proxies", VPN_PROXY); kw.setdefault("timeout", 30)
    return _requests.get(url, **kw)

def clob_post(url, **kw):
    kw.setdefault("proxies", VPN_PROXY); kw.setdefault("timeout", 30)
    return _requests.post(url, **kw)

def clob_delete(url, **kw):
    kw.setdefault("proxies", VPN_PROXY); kw.setdefault("timeout", 30)
    return _requests.delete(url, **kw)

def gamma_get(url, **kw):
    kw.setdefault("timeout", 30)
    return _requests.get(url, **kw)

# HMAC L2 auth
def _hmac_sig(secret, timestamp, method, path, body=None):
    secret_bytes = base64.urlsafe_b64decode(secret)
    message = str(timestamp) + method.upper() + path
    if body:
        message += body
    sig = hmac.new(secret_bytes, message.encode(), hashlib.sha256)
    return base64.urlsafe_b64encode(sig.digest()).decode()

def l2h(method, path, body=None):
    ts = int(time.time())
    sig = _hmac_sig(SECRET, ts, method.upper(), path, body)
    return {"POLY_ADDRESS": WALLET, "POLY_SIGNATURE": sig,
            "POLY_TIMESTAMP": str(ts), "POLY_API_KEY": API_KEY,
            "POLY_PASSPHRASE": PASSPHRASE, "Content-Type": "application/json"}

# URL parsing
def parse_polymarket_url(url_or_slug):
    url_or_slug = url_or_slug.strip()
    m = re.match(r'https?://(?:www\.)?polymarket\.com/event/([^/?#]+)(?:/([^/?#]+))?', url_or_slug)
    if m:
        return m.group(1), m.group(2)
    parts = url_or_slug.strip("/").split("/")
    return (parts[0], parts[1] if len(parts) > 1 else None)

# Gamma API
def lookup_event(slug):
    r = gamma_get(f"{GAMMA}/events", params={"slug": slug, "limit": 1})
    r.raise_for_status(); data = r.json()
    return data[0] if data else None

def lookup_market_by_slug(slug):
    r = gamma_get(f"{GAMMA}/markets", params={"slug": slug, "limit": 1})
    r.raise_for_status(); data = r.json()
    return data[0] if data else None

def search_markets(query, limit=5):
    r = gamma_get(f"{GAMMA}/markets", params={"q": query, "limit": limit, "active": "true", "closed": "false"})
    r.raise_for_status(); return r.json()

# CLOB API
def get_price(token_id, side="BUY"):
    r = clob_get(f"{BASE}/price", params={"token_id": token_id, "side": side})
    return float(r.json().get("price", 0)) if r.status_code == 200 else None

def get_midpoint(token_id):
    r = clob_get(f"{BASE}/midpoint", params={"token_id": token_id})
    return float(r.json().get("mid", 0)) if r.status_code == 200 else None

def get_orderbook(token_id):
    r = clob_get(f"{BASE}/book", params={"token_id": token_id})
    r.raise_for_status(); return r.json()

def get_balance():
    r = clob_get(f"{BASE}/balance-allowance", headers=l2h("GET", "/balance-allowance"),
                 params={"asset_type": "COLLATERAL", "signature_type": SIG_TYPE})
    r.raise_for_status(); return r.json()

def get_open_orders():
    r = clob_get(f"{BASE}/data/orders", headers=l2h("GET", "/data/orders"))
    r.raise_for_status(); return r.json()

def get_trades(limit=20):
    r = clob_get(f"{BASE}/data/trades", headers=l2h("GET", "/data/trades"), params={"limit": limit})
    r.raise_for_status(); return r.json()

def get_positions():
    r = clob_get(f"{BASE}/data/positions", headers=l2h("GET", "/data/positions"))
    r.raise_for_status(); return r.json()

def cancel_order(order_id):
    body = json.dumps({"orderID": order_id})
    r = clob_delete(f"{BASE}/order", headers=l2h("DELETE", "/order", body), data=body)
    return r.status_code, r.json()

def cancel_all():
    r = clob_delete(f"{BASE}/cancel-all", headers=l2h("DELETE", "/cancel-all"))
    return r.status_code, r.json()

# Orderbook analysis
def analyze_orderbook(token_id):
    book = get_orderbook(token_id)
    mid = get_midpoint(token_id)
    bids = sorted(book.get("bids", []), key=lambda x: float(x["price"]), reverse=True)
    asks = sorted(book.get("asks", []), key=lambda x: float(x["price"]))
    best_bid = float(bids[0]["price"]) if bids else 0
    best_ask = float(asks[0]["price"]) if asks else 1
    spread = best_ask - best_bid
    spread_pct = (spread / mid * 100) if mid else 0
    def depth_within(levels, mp, band, side):
        total = 0
        for lvl in levels:
            p, s = float(lvl["price"]), float(lvl["size"])
            if side == "bid" and p >= mp - band: total += p * s
            elif side == "ask" and p <= mp + band: total += p * s
        return total
    mp = mid or (best_bid + best_ask) / 2
    return {
        "token_id": token_id, "best_bid": best_bid, "best_ask": best_ask,
        "midpoint": mid, "spread": round(spread, 4), "spread_pct": round(spread_pct, 2),
        "bid_levels": len(bids), "ask_levels": len(asks),
        "bid_depth_2c": round(depth_within(bids, mp, 0.02, "bid"), 2),
        "ask_depth_2c": round(depth_within(asks, mp, 0.02, "ask"), 2),
        "bid_depth_5c": round(depth_within(bids, mp, 0.05, "bid"), 2),
        "ask_depth_5c": round(depth_within(asks, mp, 0.05, "ask"), 2),
        "top_bids": [{"price": b["price"], "size": b["size"]} for b in bids[:5]],
        "top_asks": [{"price": a["price"], "size": a["size"]} for a in asks[:5]],
    }

# R/R analysis
def rr_analysis(token_id, side, size_usd):
    ob = analyze_orderbook(token_id)
    if side.upper() == "YES":
        entry_price = ob["best_ask"]
    else:
        entry_price = 1 - ob["best_bid"]
    if entry_price <= 0 or entry_price >= 1:
        return {"error": f"Invalid entry price: {entry_price}"}
    tokens = size_usd / entry_price
    profit_if_win = tokens - size_usd
    rr_ratio = profit_if_win / size_usd if size_usd > 0 else 0
    return {
        "side": side.upper(), "entry_price": round(entry_price, 4),
        "implied_probability": f"{entry_price*100:.1f}%",
        "size_usd": round(size_usd, 2), "tokens": round(tokens, 2),
        "profit_if_win": round(profit_if_win, 2), "loss_if_lose": round(size_usd, 2),
        "risk_reward_ratio": f"1:{round(rr_ratio, 2)}",
        "breakeven_probability": f"{entry_price*100:.1f}%",
        "orderbook": {"spread": ob["spread"], "spread_pct": ob["spread_pct"],
                       "bid_depth_5c": ob["bid_depth_5c"], "ask_depth_5c": ob["ask_depth_5c"]},
    }

# Order building
def build_order_payload(token_id, side, price, size, neg_risk=False, tick_size="0.01"):
    exchange = CTF_EXCHANGE_NEG if neg_risk else CTF_EXCHANGE
    tick = float(tick_size)
    price = round(round(price / tick) * tick, 4)
    size = round(size, 2)
    if side.upper() == "BUY":
        taker_amount = int(round(size, 2) * 1_000_000)
        raw_maker = round(round(size, 2) * round(price, 2), 4)
        maker_amount = round(raw_maker * 1_000_000)
        order_side = 0
    else:
        maker_amount = int(size * 1_000_000)
        taker_amount = int(price * size * 1_000_000)
        order_side = 1
    salt = round(time.time() * random.random())
    domain = {"name": "Polymarket CTF Exchange", "version": "1", "chainId": CHAIN_ID, "verifyingContract": exchange}
    types = {"Order": [
        {"name": "salt", "type": "uint256"}, {"name": "maker", "type": "address"},
        {"name": "signer", "type": "address"}, {"name": "taker", "type": "address"},
        {"name": "tokenId", "type": "uint256"}, {"name": "makerAmount", "type": "uint256"},
        {"name": "takerAmount", "type": "uint256"}, {"name": "expiration", "type": "uint256"},
        {"name": "nonce", "type": "uint256"}, {"name": "feeRateBps", "type": "uint256"},
        {"name": "side", "type": "uint8"}, {"name": "signatureType", "type": "uint8"},
    ]}
    message = {
        "salt": str(salt), "maker": MAKER_ADDR, "signer": WALLET,
        "taker": "0x0000000000000000000000000000000000000000",
        "tokenId": str(token_id), "makerAmount": str(maker_amount),
        "takerAmount": str(taker_amount), "expiration": "0",
        "nonce": "0", "feeRateBps": "0", "side": order_side, "signatureType": SIG_TYPE,
    }
    meta = {"salt": salt, "maker_amount": maker_amount, "taker_amount": taker_amount, "maker": MAKER_ADDR, "signer": WALLET,
            "order_side": order_side, "exchange": exchange, "price": price, "size": size,
            "side_str": side.upper(), "neg_risk": neg_risk}
    return domain, types, message, meta

# Post signed order
def post_signed_order(token_id, signature, meta):
    side_str = "BUY" if meta["order_side"] == 0 else "SELL"
    order_body = {"order": {
        "salt": meta["salt"], "maker": MAKER_ADDR, "signer": WALLET,
        "taker": "0x0000000000000000000000000000000000000000",
        "tokenId": str(token_id), "makerAmount": str(meta["maker_amount"]),
        "takerAmount": str(meta["taker_amount"]), "expiration": "0",
        "nonce": "0", "feeRateBps": "0", "side": side_str,
        "signatureType": SIG_TYPE, "signature": signature,
    }, "owner": API_KEY, "orderType": "GTC"}
    body_str = json.dumps(order_body, separators=(",", ":"))
    headers = l2h("POST", "/order", body_str)
    r = clob_post(f"{BASE}/order", headers=headers, data=body_str)
    return r.status_code, r.json()

# Full market lookup from URL
def full_lookup(url_or_slug):
    event_slug, market_slug = parse_polymarket_url(url_or_slug)
    event = lookup_event(event_slug)
    if not event:
        market = lookup_market_by_slug(event_slug)
        if market:
            return {"type": "single_market", "market": _enrich_market(market)}
        return {"error": f"Not found: {event_slug}"}
    result = {
        "type": "event", "title": event.get("title"), "slug": event.get("slug"),
        "description": event.get("description", "")[:500],
        "end_date": event.get("endDate"), "volume": event.get("volume"),
        "neg_risk": event.get("negRisk", False),
        "neg_risk_market_id": event.get("negRiskMarketID"),
        "markets": [],
    }
    for m in event.get("markets", []):
        enriched = _enrich_market(m)
        result["markets"].append(enriched)
        if market_slug and m.get("slug") == market_slug:
            result["focused_market"] = enriched
    return result

def _enrich_market(m):
    outcomes = json.loads(m.get("outcomes", "[]")) if isinstance(m.get("outcomes"), str) else m.get("outcomes", [])
    prices = json.loads(m.get("outcomePrices", "[]")) if isinstance(m.get("outcomePrices"), str) else m.get("outcomePrices", [])
    token_ids = json.loads(m.get("clobTokenIds", "[]")) if isinstance(m.get("clobTokenIds"), str) else m.get("clobTokenIds", [])
    md = {
        "question": m.get("question"), "slug": m.get("slug"),
        "condition_id": m.get("conditionId"),
        "description": (m.get("description") or "")[:300],
        "end_date": m.get("endDate"),
        "volume": float(m.get("volume", 0) or 0),
        "active": m.get("active"), "closed": m.get("closed"),
        "accepting_orders": m.get("acceptingOrders"),
        "tick_size": m.get("orderPriceMinTickSize", 0.01),
        "min_order_size": m.get("orderMinSize", 5),
        "outcomes": [],
    }
    for i, outcome in enumerate(outcomes):
        entry = {"outcome": outcome,
                 "gamma_price": float(prices[i]) if i < len(prices) else None,
                 "token_id": token_ids[i] if i < len(token_ids) else None}
        if entry["token_id"]:
            try:
                entry["buy_price"] = get_price(entry["token_id"], "BUY")
                entry["sell_price"] = get_price(entry["token_id"], "SELL")
                entry["midpoint"] = get_midpoint(entry["token_id"])
            except Exception:
                pass
        md["outcomes"].append(entry)
    return md

# CLI
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "lookup":
        url = sys.argv[2] if len(sys.argv) > 2 else ""
        if not url: print("Usage: poly_research.py lookup <url_or_slug>"); sys.exit(1)
        print(json.dumps(full_lookup(url), indent=2, default=str))
    elif cmd == "search":
        q = " ".join(sys.argv[2:])
        if not q: print("Usage: poly_research.py search <query>"); sys.exit(1)
        for m in search_markets(q)[:5]:
            print(f"\n{m.get('question', '?')}")
            print(f"  slug: {m.get('slug', '?')}  vol: ${float(m.get('volume',0)):,.0f}")
            prices = json.loads(m.get("outcomePrices", "[]"))
            outcomes = json.loads(m.get("outcomes", "[]"))
            for i, o in enumerate(outcomes):
                print(f"  {o}: {prices[i] if i < len(prices) else '?'}")
    elif cmd == "orderbook":
        tid = sys.argv[2] if len(sys.argv) > 2 else ""
        if not tid: print("Usage: poly_research.py orderbook <token_id>"); sys.exit(1)
        print(json.dumps(analyze_orderbook(tid), indent=2))
    elif cmd == "rr":
        if len(sys.argv) < 5: print("Usage: poly_research.py rr <token_id> <YES|NO> <size_usd>"); sys.exit(1)
        print(json.dumps(rr_analysis(sys.argv[2], sys.argv[3], float(sys.argv[4])), indent=2))
    elif cmd == "prepare":
        if len(sys.argv) < 6: print("Usage: poly_research.py prepare <token_id> <BUY|SELL> <price> <size> [neg_risk] [tick]"); sys.exit(1)
        neg = len(sys.argv) > 6 and sys.argv[6].lower() in ("true", "yes", "1", "neg", "neg_risk")
        tick = sys.argv[7] if len(sys.argv) > 7 else "0.01"
        d, t, m, meta = build_order_payload(sys.argv[2], sys.argv[3].upper(), float(sys.argv[4]), float(sys.argv[5]), neg, tick)
        print(json.dumps({"domain": d, "types": t, "primaryType": "Order", "message": m, "meta": meta}, indent=2))
    elif cmd == "balance":
        d = get_balance()
        print(f"Balance: ${float(d.get('balance',0))/1e6:.4f}  Allowance: ${float(d.get('allowance',0))/1e6:.4f}")
    elif cmd == "orders":
        d = get_open_orders()
        print(f"Open: {d.get('count',0)}")
        for o in d.get("data", []): print(f"  {o['id'][:16]}... {o['side']} @ {o['price']} sz={o['original_size']}")
    elif cmd == "positions":
        print(json.dumps(get_positions(), indent=2))
    elif cmd == "trades":
        d = get_trades(); trades = d.get("data", []) if isinstance(d, dict) else d
        for t in trades[:10]: print(json.dumps(t))
    elif cmd == "cancel":
        if len(sys.argv) < 3: print("Need order_id"); sys.exit(1)
        s, r = cancel_order(sys.argv[2]); print(f"{s}: {json.dumps(r)}")
    elif cmd == "cancel_all":
        s, r = cancel_all(); print(f"{s}: {json.dumps(r)}")
    elif cmd == "post":
        if len(sys.argv) < 5: print("Usage: poly_research.py post <token_id> <signature> <meta_json>"); sys.exit(1)
        meta = json.loads(sys.argv[4])
        s, r = post_signed_order(sys.argv[2], sys.argv[3], meta)
        print(f"{s}: {json.dumps(r, indent=2)}")
    else:
        print(__doc__)
