#!/usr/bin/env python3
"""Fetch WOOFi volume and staking data across all chains."""
import requests

CHAINS = ["arbitrum", "base", "bsc", "optimism", "solana", "polygon", "avalanche", "ethereum"]
BASE = "https://fi-api.woo.org"

def get_volume(period="monthly"):
    results = []
    for chain in CHAINS:
        try:
            r = requests.get(f"{BASE}/swap_stats", params={"type": period, "network": chain}, timeout=10)
            d = r.json()
            results.append({
                "chain": chain,
                "volume": d.get("volume", 0),
                "traders": d.get("traders", 0),
                "peak_daily_traders": d.get("traders_peak_daily", 0),
            })
        except Exception as e:
            results.append({"chain": chain, "error": str(e)})
    return results

def get_staking():
    r = requests.get(f"{BASE}/staking", timeout=10)
    return r.json()

if __name__ == "__main__":
    print("=== WOOFi 30d Volume by Chain ===")
    data = get_volume("monthly")
    total = 0
    for d in sorted(data, key=lambda x: x.get("volume", 0), reverse=True):
        if "error" not in d:
            total += d["volume"]
            print(f"{d['chain']:12}: ${d['volume']:>14,.0f} | traders: {d['traders']:>6,} | peak daily: {d['peak_daily_traders']:>6,}")
    print(f"{'TOTAL':12}: ${total:>14,.0f}")

    print("\n=== WOO Staking ===")
    s = get_staking()
    print(s)
