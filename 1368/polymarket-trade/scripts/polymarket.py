"""
Polymarket Trading Script — full flow:
- L1 EIP-712 auth → get API creds
- L2 HMAC signing for trading requests
- Place/cancel orders, check positions

Usage:
  python3 polymarket.py auth                          # derive/create API creds
  python3 polymarket.py approve                       # approve USDC for CTF exchange
  python3 polymarket.py order <token_id> <side> <price> <size>  # place order
  python3 polymarket.py orders                        # list open orders
  python3 polymarket.py cancel <order_id>             # cancel order
  python3 polymarket.py balance                       # check USDC allowance/balance
"""
import requests
import json
import time
import hmac
import hashlib
import base64
import os
import sys
import argparse

CLOB_HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
AGENT_ADDRESS = "0x3e880B128146d65368422B0bf4aB3757A010108E"
CREDS_FILE = "/data/workspace/.polymarket_creds.json"

# Polygon contract addresses
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
CTF_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"

def load_creds():
    if not os.path.exists(CREDS_FILE):
        print("❌ No credentials found. Run: python3 polymarket.py auth")
        sys.exit(1)
    with open(CREDS_FILE) as f:
        return json.load(f)

def get_server_timestamp():
    resp = requests.get(f"{CLOB_HOST}/time", timeout=10)
    return int(resp.json()["time"])

def l2_sign(method, request_path, body, timestamp, secret):
    """Generate HMAC-SHA256 L2 signature"""
    body_str = json.dumps(body, separators=(',', ':')) if body else ""
    message = f"{timestamp}{method}{request_path}{body_str}"
    secret_bytes = base64.b64decode(secret)
    sig = hmac.new(secret_bytes, message.encode(), hashlib.sha256).digest()
    return base64.b64encode(sig).decode()

def l2_headers(method, path, body, creds):
    ts = str(get_server_timestamp())
    sig = l2_sign(method, path, body, ts, creds["secret"])
    return {
        "POLY_ADDRESS": AGENT_ADDRESS,
        "POLY_SIGNATURE": sig,
        "POLY_TIMESTAMP": ts,
        "POLY_API_KEY": creds["apiKey"],
        "POLY_PASSPHRASE": creds["passphrase"],
        "Content-Type": "application/json"
    }

def get_open_orders():
    creds = load_creds()
    path = "/orders"
    headers = l2_headers("GET", path, None, creds)
    resp = requests.get(f"{CLOB_HOST}{path}", headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()

def get_balance_allowance():
    creds = load_creds()
    path = "/balance-allowance"
    params = {"asset_type": "COLLATERAL", "signature_type": 0}
    headers = l2_headers("GET", path, None, creds)
    resp = requests.get(f"{CLOB_HOST}{path}", headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()

def cancel_order(order_id):
    creds = load_creds()
    path = "/order"
    body = {"orderID": order_id}
    headers = l2_headers("DELETE", path, body, creds)
    resp = requests.delete(f"{CLOB_HOST}{path}", headers=headers, json=body, timeout=15)
    resp.raise_for_status()
    return resp.json()

def get_market_info(token_id):
    """Get tick size and neg_risk for a token"""
    resp = requests.get(f"{CLOB_HOST}/markets", params={"token_id": token_id}, timeout=10)
    if resp.status_code == 200 and resp.json():
        market = resp.json()[0] if isinstance(resp.json(), list) else resp.json()
        return {
            "tick_size": market.get("minimum_tick_size", "0.01"),
            "neg_risk": market.get("neg_risk", False)
        }
    return {"tick_size": "0.01", "neg_risk": False}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["auth", "approve", "order", "orders", "cancel", "balance", "market"])
    parser.add_argument("args", nargs="*")
    args = parser.parse_args()

    if args.action == "orders":
        orders = get_open_orders()
        if not orders:
            print("No open orders.")
        else:
            for o in orders:
                print(f"ID: {o.get('id')} | {o.get('side')} {o.get('size_matched','?')}/{o.get('original_size','?')} @ {o.get('price')} | Status: {o.get('status')}")

    elif args.action == "balance":
        bal = get_balance_allowance()
        print(json.dumps(bal, indent=2))

    elif args.action == "cancel":
        if not args.args:
            print("Usage: polymarket.py cancel <order_id>")
            sys.exit(1)
        result = cancel_order(args.args[0])
        print(json.dumps(result, indent=2))

    elif args.action == "market":
        if not args.args:
            print("Usage: polymarket.py market <token_id>")
            sys.exit(1)
        info = get_market_info(args.args[0])
        print(json.dumps(info, indent=2))

    elif args.action == "auth":
        print("Auth flow requires EIP-712 signing via tool call.")
        print("Use the agent's auth workflow instead.")

    elif args.action == "approve":
        print("USDC approval requires on-chain transaction via agent wallet tools.")
        print("Use: wallet_transfer with CTF Exchange approval calldata.")

    elif args.action == "order":
        if len(args.args) < 4:
            print("Usage: polymarket.py order <token_id> <BUY|SELL> <price> <size>")
            sys.exit(1)
        token_id, side, price, size = args.args[0], args.args[1].upper(), float(args.args[2]), float(args.args[3])
        print(f"Order params: {side} {size} USDC of token {token_id} @ {price}")
        print("Order placement requires signed order via py_clob_client — use agent workflow.")
