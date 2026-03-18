#!/usr/bin/env python3
import argparse, json, time
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict
import requests

URL = "https://api.hyperliquid.xyz/info"

def pf(x, d=0.0):
    try: return float(x)
    except: return d

def post(payload):
    r = requests.post(URL, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def get_fills(user, s, e):
    out, cur = [], s
    while cur <= e:
        data = post({"type":"userFillsByTime","user":user,"startTime":cur,"endTime":e,"aggregateByTime":False})
        if not isinstance(data, list) or not data: break
        rows = [x.get("fill", x) for x in data]
        rows.sort(key=lambda x: int(x.get("time", 0)))
        out.extend(rows)
        if len(rows) < 2000: break
        last = int(rows[-1].get("time", 0))
        if last <= cur: break
        cur = last + 1
        time.sleep(0.1)
    return [x for x in out if s <= int(x.get("time",0)) <= e]

def ranges(s,e,step):
    cur = s
    while cur <= e:
        ed = min(e, cur+step-1)
        yield cur, ed
        cur = ed + 1

def get_1m_refs(coin, s, e):
    refs = {}
    step = 3*24*60*60*1000
    for a,b in ranges(s,e,step):
        d = post({"type":"candleSnapshot","req":{"coin":coin,"interval":"1m","startTime":a,"endTime":b}})
        if not isinstance(d,list):
            continue
        for c in d:
            t = int(c.get("t", c.get("time", 0)))
            o,h,l,cl = pf(c.get("o",c.get("open"))), pf(c.get("h",c.get("high"))), pf(c.get("l",c.get("low"))), pf(c.get("c",c.get("close")))
            if t>0 and o>0 and h>0 and l>0 and cl>0:
                refs[(t//60000)*60000] = (o+h+l+cl)/4
        time.sleep(0.08)
    return refs

def money(x): return f"${x:,.2f}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wallet", required=True)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--orderly-taker-bps", type=float, default=3.0)
    ap.add_argument("--orderly-maker-bps", type=float, default=0.0)
    ap.add_argument("--orderly-slippage-improvement-bps", type=float, default=0.0)
    ap.add_argument("--outdir", default="output/vampire_attack")
    args = ap.parse_args()

    end_ms = int(time.time()*1000)
    start_ms = end_ms - args.days*24*60*60*1000
    fills = get_fills(args.wallet, start_ms, end_ms)
    if not fills:
        raise SystemExit("No fills found in selected window")

    coins = sorted({str(f.get("coin","")) for f in fills if f.get("coin")})
    refs = {c:get_1m_refs(c,start_ms,end_ms) for c in coins}

    tot_notional=tot_fee=tot_builder=tot_slip=tot_cf_fee=tot_cf_slip=0.0
    makers=takers=priced=0
    by_coin = defaultdict(lambda:{"fills":0,"notional":0.0,"fees":0.0,"builder_fees":0.0,"slippage_est":0.0,"cf_fee":0.0,"cf_slippage":0.0,"maker":0,"taker":0})

    for f in fills:
        coin = str(f.get("coin","")); px=pf(f.get("px")); sz=pf(f.get("sz"))
        if px<=0 or sz<=0: continue
        n = px*sz
        crossed = bool(f.get("crossed",False))
        fee = pf(f.get("fee")); bfee = pf(f.get("builderFee",0.0))
        side = str(f.get("side",""))
        tms = int(f.get("time",0)); m=(tms//60000)*60000

        tot_notional += n; tot_fee += fee; tot_builder += bfee
        row = by_coin[coin]
        row["fills"] += 1; row["notional"] += n; row["fees"] += fee; row["builder_fees"] += bfee

        if crossed: takers += 1; row["taker"] += 1
        else: makers += 1; row["maker"] += 1

        cf_rate = args.orderly_taker_bps if crossed else args.orderly_maker_bps
        cf_fee = n*cf_rate/10000
        tot_cf_fee += cf_fee; row["cf_fee"] += cf_fee

        slip=cf_slip=0.0
        if crossed:
            ref = refs.get(coin,{}).get(m)
            if ref and ref>0:
                priced += 1
                if side=="B": slip = max(0.0,(px-ref)*sz)
                else: slip = max(0.0,(ref-px)*sz)
                improve = n*args.orderly_slippage_improvement_bps/10000
                cf_slip = max(0.0, slip-improve)
        tot_slip += slip; tot_cf_slip += cf_slip
        row["slippage_est"] += slip; row["cf_slippage"] += cf_slip

    actual = tot_fee + tot_builder + tot_slip
    cf = tot_cf_fee + tot_cf_slip
    savings = actual - cf

    summary = {
        "fills": len(fills), "maker_fills": makers, "taker_fills": takers, "priced_slippage_fills": priced,
        "total_notional_usd": tot_notional, "actual_fees_usd": tot_fee, "actual_builder_fees_usd": tot_builder,
        "actual_slippage_est_usd": tot_slip, "actual_total_cost_usd": actual,
        "orderly_counterfactual_fees_usd": tot_cf_fee, "orderly_counterfactual_slippage_usd": tot_cf_slip,
        "orderly_counterfactual_total_cost_usd": cf, "savings_total_usd": savings,
        "savings_fee_only_usd": (tot_fee+tot_builder)-tot_cf_fee
    }

    payload = {
        "wallet": args.wallet,
        "window": {"start_ms": start_ms, "end_ms": end_ms},
        "assumptions": {
            "orderly_taker_bps": args.orderly_taker_bps,
            "orderly_maker_bps": args.orderly_maker_bps,
            "orderly_slippage_improvement_bps": args.orderly_slippage_improvement_bps,
            "slippage_reference": "1m OHLC4",
            "notes": ["Fees exact from fills", "Slippage estimated for taker fills"]
        },
        "summary": summary,
        "by_coin": dict(by_coin)
    }

    out = Path(args.outdir); out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = args.wallet[:8]
    jp = out/f"hl_vampire_{slug}_{ts}.json"
    mp = out/f"hl_vampire_{slug}_{ts}.md"
    jp.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    si = datetime.fromtimestamp(start_ms/1000, tz=timezone.utc).isoformat()
    ei = datetime.fromtimestamp(end_ms/1000, tz=timezone.utc).isoformat()
    md = f"""# Hyperliquid → Orderly Cost Leakage Report (V1)

**Wallet:** `{args.wallet}`  
**Window:** {si} → {ei} UTC

## Headline
If you routed these exact Hyperliquid trades through Orderly, you would have saved **{money(summary['savings_total_usd'])}** over this period.

Want me to migrate your liquidity?

## Breakdown
- Fills analyzed: **{summary['fills']}** (maker {summary['maker_fills']}, taker {summary['taker_fills']})
- Notional traded: **{money(summary['total_notional_usd'])}**
- Hyperliquid fees (exact): **{money(summary['actual_fees_usd'])}**
- Hyperliquid builder fees (exact): **{money(summary['actual_builder_fees_usd'])}**
- Hyperliquid slippage (estimated): **{money(summary['actual_slippage_est_usd'])}**
- Current total cost: **{money(summary['actual_total_cost_usd'])}**
- Orderly counterfactual total cost: **{money(summary['orderly_counterfactual_total_cost_usd'])}**
- **Projected savings: {money(summary['savings_total_usd'])}**
- Fee-only savings: **{money(summary['savings_fee_only_usd'])}**

## Assumptions
- Orderly taker fee: {args.orderly_taker_bps} bps
- Orderly maker fee: {args.orderly_maker_bps} bps
- Orderly slippage improvement: {args.orderly_slippage_improvement_bps} bps of notional
- Slippage reference: 1m OHLC4
"""
    mp.write_text(md, encoding="utf-8")

    print(json.dumps({"status":"ok","wallet":args.wallet,"fills":len(fills),"json_report":str(jp),"markdown_report":str(mp),"headline_savings_usd":round(savings,2)}, indent=2))

if __name__ == "__main__":
    main()
