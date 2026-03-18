"""
Polymarket L1 Auth — derive API credentials from agent wallet via EIP-712.
Stores creds in workspace/.polymarket_creds.json
"""
import requests
import json
import time
import hmac
import hashlib
import base64
import os
import sys

CLOB_HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
AGENT_ADDRESS = "0x3e880B128146d65368422B0bf4aB3757A010108E"
CREDS_FILE = "/data/workspace/.polymarket_creds.json"

def get_server_timestamp():
    resp = requests.get(f"{CLOB_HOST}/time", timeout=10)
    return int(resp.json()["time"])

def build_eip712_message(address, timestamp, nonce=0):
    return {
        "domain": {
            "name": "ClobAuthDomain",
            "version": "1",
            "chainId": CHAIN_ID
        },
        "types": {
            "ClobAuth": [
                {"name": "address", "type": "address"},
                {"name": "timestamp", "type": "string"},
                {"name": "nonce", "type": "uint256"},
                {"name": "message", "type": "string"}
            ]
        },
        "primaryType": "ClobAuth",
        "message": {
            "address": address,
            "timestamp": str(timestamp),
            "nonce": nonce,
            "message": "This message attests that I control the given wallet"
        }
    }

def derive_creds(signature, address, timestamp, nonce=0):
    headers = {
        "POLY_ADDRESS": address,
        "POLY_SIGNATURE": signature,
        "POLY_TIMESTAMP": str(timestamp),
        "POLY_NONCE": str(nonce),
        "Content-Type": "application/json"
    }
    resp = requests.get(f"{CLOB_HOST}/auth/derive-api-key", headers=headers, timeout=15)
    if resp.status_code == 200:
        return resp.json()
    # Try create instead
    resp2 = requests.post(f"{CLOB_HOST}/auth/api-key", headers=headers, timeout=15)
    resp2.raise_for_status()
    return resp2.json()

if __name__ == "__main__":
    # Step 1: Get server timestamp
    ts = get_server_timestamp()
    print(f"Server timestamp: {ts}")

    # Step 2: Build EIP-712 payload
    nonce = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    eip712 = build_eip712_message(AGENT_ADDRESS, ts, nonce)

    print("\nEIP-712 payload to sign:")
    print(json.dumps(eip712, indent=2))
    print("\nPaste the signature from wallet_sign_typed_data below:")
    sig = input("Signature: ").strip()

    # Step 3: Derive credentials
    print("\nDeriving API credentials...")
    creds = derive_creds(sig, AGENT_ADDRESS, ts, nonce)
    print(f"\nCredentials received:")
    print(json.dumps(creds, indent=2))

    # Step 4: Save to file
    creds["address"] = AGENT_ADDRESS
    creds["nonce"] = nonce
    with open(CREDS_FILE, "w") as f:
        json.dump(creds, f, indent=2)
    print(f"\nSaved to {CREDS_FILE}")
