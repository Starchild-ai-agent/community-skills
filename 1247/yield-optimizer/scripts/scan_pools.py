#!/usr/bin/env python3
"""
Starchild Yield Optimizer — Pool Scanner
Fetches real-time stablecoin yields from DeFi Llama.
Ranks by risk-adjusted return across 8+ protocols, 6 chains.

Usage:
  python3 scan_pools.py                     # Full formatted report
  python3 scan_pools.py --json              # JSON output for automation
  python3 scan_pools.py --chain Base        # Filter by chain
  python3 scan_pools.py --protocol aave-v3  # Filter by protocol
  python3 scan_pools.py --top 5             # Top N only
  python3 scan_pools.py --token USDC        # Filter by token
  python3 scan_pools.py --amount 10000 --risk balanced  # Allocation recommendation
"""
import requests, json, sys, argparse
from datetime import datetime, timezone

DEFILLAMA_YIELDS = "https://yields.llama.fi/pools"
PROTOCOLS = [
    "aave-v3","compound-v3","morpho-v1","morpho-blue","pendle",
    "fluid-lending","sky-lending","sparklend","euler","seamless-protocol","moonwell-v2",
]
CHAINS = ["Ethereum","Arbitrum","Base","Optimism","Polygon","Avalanche"]
STABLES = ["USDC","USDT","DAI","USDS","sDAI","sUSDe","GHO","SUSDAI"]
RISK_TIERS = {
    "aave-v3":1,"compound-v3":1,"sparklend":1,"sky-lending":1,
    "morpho-v1":2,"morpho-blue":2,"euler":2,"fluid-lending":2,
    "seamless-protocol":2,"moonwell-v2":2,"pendle":3,
}
CHAIN_MAP = {
    "Ethereum":{"tool":"ethereum","id":1},"Arbitrum":{"tool":"arbitrum","id":42161},
    "Base":{"tool":"base","id":8453},"Optimism":{"tool":"optimism","id":10},
    "Polygon":{"tool":"polygon","id":137},"Avalanche":{"tool":"avalanche","id":43114},
}
GAS_EST = {"Ethereum":8.0,"Arbitrum":0.15,"Base":0.08,"Optimism":0.15,"Polygon":0.03,"Avalanche":0.15}

def fetch_pools():
    resp = requests.get(DEFILLAMA_YIELDS, timeout=30)
    resp.raise_for_status()
    return resp.json()["data"]

def filter_pools(raw, chain=None, protocol=None, token=None, min_tvl=100_000):
    pools = []
    for p in raw:
        proj, sym, ch = p.get("project",""), (p.get("symbol") or "").upper(), p.get("chain","")
        tvl, apy = p.get("tvlUsd",0) or 0, p.get("apy",0) or 0
        if proj not in PROTOCOLS or ch not in CHAINS: continue
        if not any(s in sym for s in STABLES): continue
        if tvl < min_tvl: continue
        if chain and ch.lower() != chain.lower(): continue
        if protocol and proj != protocol: continue
        if token and token.upper() not in sym: continue
        pools.append({
            "pool_id":p.get("pool",""), "protocol":proj, "chain":ch,
            "chain_tool":CHAIN_MAP.get(ch,{}).get("tool",ch.lower()),
            "chain_id":CHAIN_MAP.get(ch,{}).get("id",0), "symbol":sym,
            "apy":round(apy,4), "apy_base":round(p.get("apyBase",0) or 0,4),
            "apy_reward":round(p.get("apyReward",0) or 0,4),
            "tvl":round(tvl), "risk_tier":RISK_TIERS.get(proj,3),
            "gas_estimate":GAS_EST.get(ch,1.0),
        })
    pools.sort(key=lambda x: x["apy"], reverse=True)
    return pools

def compute_stats(pools):
    if not pools: return {}
    total_tvl = sum(p["tvl"] for p in pools)
    avg_apy = sum(p["apy"] for p in pools) / len(pools)
    best_chain, best_proto = {}, {}
    for p in pools:
        if p["chain"] not in best_chain or p["apy"] > best_chain[p["chain"]]["apy"]:
            best_chain[p["chain"]] = p
        if p["protocol"] not in best_proto or p["apy"] > best_proto[p["protocol"]]["apy"]:
            best_proto[p["protocol"]] = p
    tiers = {1:0,2:0,3:0}
    for p in pools: tiers[p["risk_tier"]] = tiers.get(p["risk_tier"],0)+1
    high_yield = [p for p in pools if p["apy"] > avg_apy * 1.5][:5]
    return {
        "total_pools":len(pools), "total_tvl":total_tvl, "avg_apy":round(avg_apy,2),
        "best_pool":pools[0],
        "best_by_chain":{k:{"chain":v["chain"],"protocol":v["protocol"],"symbol":v["symbol"],"apy":v["apy"]}
            for k,v in sorted(best_chain.items(), key=lambda x:x[1]["apy"], reverse=True)},
        "best_by_protocol":{k:{"chain":v["chain"],"symbol":v["symbol"],"apy":v["apy"]}
            for k,v in sorted(best_proto.items(), key=lambda x:x[1]["apy"], reverse=True)},
        "tier_counts":tiers,
        "high_yield_alerts":[{"protocol":p["protocol"],"chain":p["chain"],"symbol":p["symbol"],"apy":p["apy"]} for p in high_yield],
        "chains_monitored":len(best_chain), "protocols_monitored":len(best_proto),
        "scan_time":datetime.now(timezone.utc).isoformat(),
    }

def recommend_allocation(pools, amount, risk="balanced"):
    if not pools or amount <= 0: return None
    t1 = [p for p in pools if p["risk_tier"]==1]
    t2 = [p for p in pools if p["risk_tier"]==2]
    t3 = [p for p in pools if p["risk_tier"]==3]
    splits = {"conservative":[(t1,1.0)],"balanced":[(t1,0.7),(t2,0.3)],"aggressive":[(t1,0.5),(t2,0.3),(t3,0.2)]}
    alloc, wapy = [], 0
    for tp, w in splits.get(risk, splits["balanced"]):
        if not tp: continue
        b = tp[0]; amt = round(amount*w,2)
        alloc.append({"pool":f"{b['protocol']} {b['chain']} {b['symbol']}","protocol":b["protocol"],
            "chain":b["chain"],"chain_tool":b["chain_tool"],"symbol":b["symbol"],"apy":b["apy"],
            "amount_usd":amt,"weight_pct":round(w*100),"annual_yield_usd":round(amt*b["apy"]/100,2),
            "risk_tier":b["risk_tier"]})
        wapy += b["apy"]*w
    return {"risk_profile":risk,"total_amount":amount,"allocations":alloc,
        "blended_apy":round(wapy,2),"projected_annual_yield":round(amount*wapy/100,2),
        "projected_monthly_yield":round(amount*wapy/100/12,2)}

def print_report(pools, stats):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"🌾 Starchild Yield Optimizer — {now}")
    print(f"📊 {stats['total_pools']} pools | {stats['chains_monitored']} chains | {stats['protocols_monitored']} protocols | ${stats['total_tvl']/1e9:.1f}B TVL")
    print("="*70)
    print(f"\n🏆 TOP YIELDS")
    print(f"{'#':<4} {'Protocol':<16} {'Chain':<12} {'Symbol':<10} {'APY%':<9} {'TVL($M)':<10} {'Tier'}")
    print("-"*70)
    for i,p in enumerate(pools[:15],1):
        t = {1:"🟢",2:"🟡",3:"🔴"}.get(p["risk_tier"],"⚪")
        print(f"{i:<4} {p['protocol']:<16} {p['chain']:<12} {p['symbol']:<10} {p['apy']:<9.2f} {p['tvl']/1e6:<10.1f} {t}")
    print(f"\n⛓️ BEST PER CHAIN")
    for ch,info in stats["best_by_chain"].items():
        print(f"  {ch:<12} → {info['apy']:.2f}% ({info['protocol']} {info['symbol']})")
    if stats.get("high_yield_alerts"):
        print(f"\n🔥 HIGH YIELD (>{stats['avg_apy']*1.5:.1f}%)")
        for a in stats["high_yield_alerts"]:
            print(f"  ⚡ {a['protocol']} {a['chain']} — {a['symbol']} at {a['apy']:.2f}%")
    tc = stats["tier_counts"]
    print(f"\n📊 🟢 Safe:{tc.get(1,0)} | 🟡 Moderate:{tc.get(2,0)} | 🔴 Aggressive:{tc.get(3,0)} | Avg APY: {stats['avg_apy']:.2f}%")

def main():
    pa = argparse.ArgumentParser(description="Starchild Yield Optimizer")
    pa.add_argument("--json", action="store_true")
    pa.add_argument("--chain", type=str)
    pa.add_argument("--protocol", type=str)
    pa.add_argument("--token", type=str)
    pa.add_argument("--top", type=int, default=0)
    pa.add_argument("--amount", type=float, default=0)
    pa.add_argument("--risk", type=str, default="balanced", choices=["conservative","balanced","aggressive"])
    pa.add_argument("--min-tvl", type=float, default=100000)
    args = pa.parse_args()
    raw = fetch_pools()
    pools = filter_pools(raw, chain=args.chain, protocol=args.protocol, token=args.token, min_tvl=args.min_tvl)
    if args.top > 0: pools = pools[:args.top]
    stats = compute_stats(pools)
    if args.json:
        out = {"pools":pools[:30],"stats":stats}
        if args.amount > 0: out["recommendation"] = recommend_allocation(pools, args.amount, args.risk)
        print(json.dumps(out, indent=2))
    else:
        print_report(pools, stats)
        if args.amount > 0:
            rec = recommend_allocation(pools, args.amount, args.risk)
            if rec:
                print(f"\n💰 ALLOCATION ({rec['risk_profile'].upper()}) for ${rec['total_amount']:,.0f}")
                print("-"*50)
                for a in rec["allocations"]:
                    print(f"  {a['weight_pct']}% → {a['pool']} at {a['apy']:.2f}% = ${a['annual_yield_usd']:,.0f}/yr")
                print(f"\n  Blended: {rec['blended_apy']:.2f}% | ${rec['projected_annual_yield']:,.0f}/yr | ${rec['projected_monthly_yield']:,.0f}/mo")

if __name__ == "__main__":
    main()
