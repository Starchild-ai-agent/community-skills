"""
Historical quote logging for Meta DEX Aggregator.

Logs every quote to a JSONL file for later analysis:
- Which aggregator wins most often per chain/pair
- Price trends over time
- Gas cost patterns
- Slippage analysis

Usage:
  from quote_logger import log_quote, get_winner_stats, get_price_trend
"""

import json, os
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def _get_log_file(chain, from_symbol, to_symbol):
    """Get log file path for a specific trading pair."""
    LOG_DIR.mkdir(exist_ok=True)
    slug = f"{chain}_{from_symbol.upper()}_{to_symbol.upper()}.jsonl"
    return LOG_DIR / slug


def log_quote(chain, from_token, to_token, amount_in, quotes, best_aggregator, net_out_usd):
    """
    Log a quote snapshot to the historical log.
    
    Args:
        chain: Chain name (e.g., "arbitrum")
        from_token: Token dict with symbol, address, decimals
        to_token: Token dict with symbol, address, decimals
        amount_in: Input amount (human-readable)
        quotes: List of all aggregator quotes
        best_aggregator: Name of winning aggregator
        net_out_usd: Net output in USD (after gas)
    
    Returns:
        log_entry_id: Unique ID for this log entry
    """
    log_file = _get_log_file(chain, from_token["symbol"], to_token["symbol"])
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "chain": chain,
        "fromToken": {
            "symbol": from_token["symbol"],
            "address": from_token["address"],
        },
        "toToken": {
            "symbol": to_token["symbol"],
            "address": to_token["address"],
        },
        "amountIn": amount_in,
        "quotes": [
            {
                "aggregator": q["aggregator"],
                "amountOut": q.get("amountOutHuman"),
                "amountUsd": q.get("amountUsd"),
                "gasUsd": q.get("gasUsd"),
                "netOut": q.get("netOut"),
                "vsBestPct": q.get("vsbestPct"),
                "isMEVSafe": q.get("isMEVSafe", False),
            }
            for q in quotes
        ],
        "winner": best_aggregator,
        "netOutUsd": net_out_usd,
    }
    
    entry_id = f"{chain}-{from_token['symbol']}-{to_token['symbol']}-{int(datetime.utcnow().timestamp())}"
    entry["id"] = entry_id
    
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    return entry_id


def get_winner_stats(chain, from_symbol, to_symbol, days=7):
    """
    Get statistics on which aggregator wins most often for a pair.
    
    Args:
        chain: Chain name
        from_symbol: From token symbol
        to_symbol: To token symbol
        days: Number of days to analyze
    
    Returns:
        dict with winner counts, win rates, and average net out per aggregator
    """
    import time
    from datetime import timedelta
    
    log_file = _get_log_file(chain, from_symbol, to_symbol)
    if not log_file.exists():
        return {"error": "No historical data for this pair"}
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    winner_counts = {}
    aggregator_net_outs = {}
    total_entries = 0
    
    with open(log_file, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
            if ts < cutoff:
                continue
            
            total_entries += 1
            winner = entry["winner"]
            winner_counts[winner] = winner_counts.get(winner, 0) + 1
            
            # Track net outs per aggregator
            for q in entry["quotes"]:
                agg = q["aggregator"]
                if agg not in aggregator_net_outs:
                    aggregator_net_outs[agg] = []
                if q.get("netOut") is not None:
                    aggregator_net_outs[agg].append(float(q["netOut"]))
    
    if total_entries == 0:
        return {"error": f"No data in last {days} days"}
    
    # Calculate win rates
    win_rates = {agg: count / total_entries for agg, count in winner_counts.items()}
    
    # Calculate average net out per aggregator
    avg_net_outs = {}
    for agg, net_outs in aggregator_net_outs.items():
        if net_outs:
            avg_net_outs[agg] = sum(net_outs) / len(net_outs)
    
    return {
        "chain": chain,
        "pair": f"{from_symbol}/{to_symbol}",
        "periodDays": days,
        "totalQuotes": total_entries,
        "winnerCounts": winner_counts,
        "winRates": win_rates,
        "mostFrequentWinner": max(winner_counts, key=winner_counts.get) if winner_counts else None,
        "averageNetOutByAggregator": avg_net_outs,
        "bestOnAverage": max(avg_net_outs, key=avg_net_outs.get) if avg_net_outs else None,
    }


def get_price_trend(chain, from_symbol, to_symbol, days=7, bucket_hours=1):
    """
    Get price trend (net output over time) for a pair.
    
    Args:
        chain: Chain name
        from_symbol: From token symbol
        to_symbol: To token symbol
        days: Number of days to analyze
        bucket_hours: Group data into N-hour buckets
    
    Returns:
        List of {timestamp, avgNetOut, minNetOut, maxNetOut, quoteCount} buckets
    """
    from datetime import timedelta
    from collections import defaultdict
    
    log_file = _get_log_file(chain, from_symbol, to_symbol)
    if not log_file.exists():
        return {"error": "No historical data for this pair"}
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    buckets = defaultdict(list)
    
    with open(log_file, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
            if ts < cutoff:
                continue
            
            # Round to bucket
            bucket_ts = ts.replace(minute=0, second=0, microsecond=0)
            bucket_ts = bucket_ts.replace(hour=(bucket_ts.hour // bucket_hours) * bucket_hours)
            
            if entry.get("netOutUsd") is not None:
                buckets[bucket_ts].append(float(entry["netOutUsd"]))
    
    # Build trend data
    trend = []
    for bucket_ts in sorted(buckets.keys()):
        values = buckets[bucket_ts]
        trend.append({
            "timestamp": bucket_ts.isoformat() + "Z",
            "avgNetOut": sum(values) / len(values),
            "minNetOut": min(values),
            "maxNetOut": max(values),
            "quoteCount": len(values),
        })
    
    return {
        "chain": chain,
        "pair": f"{from_symbol}/{to_symbol}",
        "periodDays": days,
        "bucketHours": bucket_hours,
        "data": trend,
    }


def get_slippage_analysis(chain, from_symbol, to_symbol, days=7):
    """
    Analyze slippage patterns (difference between expected and typical execution).
    
    Returns:
        Statistics on typical vs quoted spreads
    """
    from datetime import timedelta
    
    log_file = _get_log_file(chain, from_symbol, to_symbol)
    if not log_file.exists():
        return {"error": "No historical data for this pair"}
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    spreads = []  # (best - second_best) / best
    
    with open(log_file, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
            if ts < cutoff:
                continue
            
            # Get top 2 quotes by netOut
            sorted_quotes = sorted(
                [q for q in entry["quotes"] if q.get("netOut") is not None],
                key=lambda q: q["netOut"],
                reverse=True
            )
            
            if len(sorted_quotes) >= 2:
                best = sorted_quotes[0]["netOut"]
                second = sorted_quotes[1]["netOut"]
                if best > 0:
                    spread = (best - second) / best * 100
                    spreads.append(spread)
    
    if not spreads:
        return {"error": "Insufficient data for analysis"}
    
    return {
        "chain": chain,
        "pair": f"{from_symbol}/{to_symbol}",
        "periodDays": days,
        "samples": len(spreads),
        "avgSpreadPct": sum(spreads) / len(spreads),
        "minSpreadPct": min(spreads),
        "maxSpreadPct": max(spreads),
        "medianSpreadPct": sorted(spreads)[len(spreads) // 2],
        "competitiveThreshold": "spread < 0.5% = highly competitive, >2% = one aggregator dominates",
    }


def export_to_csv(chain, from_symbol, to_symbol, days=30, output_file=None):
    """
    Export historical quotes to CSV for external analysis.
    
    Returns:
        CSV content as string, or writes to file if output_file specified
    """
    from datetime import timedelta
    import csv
    from io import StringIO
    
    log_file = _get_log_file(chain, from_symbol, to_symbol)
    if not log_file.exists():
        return "error,No historical data for this pair"
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    rows = []
    
    with open(log_file, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
            if ts < cutoff:
                continue
            
            # One row per aggregator quote
            for q in entry["quotes"]:
                rows.append({
                    "timestamp": entry["timestamp"],
                    "chain": chain,
                    "from_symbol": from_symbol,
                    "to_symbol": to_symbol,
                    "amount_in": entry["amountIn"],
                    "aggregator": q["aggregator"],
                    "amount_out": q.get("amountOut", ""),
                    "amount_usd": q.get("amountUsd", ""),
                    "gas_usd": q.get("gasUsd", ""),
                    "net_out": q.get("netOut", ""),
                    "vs_best_pct": q.get("vsBestPct", ""),
                    "is_mev_safe": q.get("isMEVSafe", False),
                    "winner": entry["winner"],
                    "net_out_usd": entry.get("netOutUsd", ""),
                })
    
    if not rows:
        return "error,No data in specified period"
    
    # Write CSV
    output = StringIO()
    fieldnames = ["timestamp", "chain", "from_symbol", "to_symbol", "amount_in", 
                  "aggregator", "amount_out", "amount_usd", "gas_usd", "net_out", 
                  "vs_best_pct", "is_mev_safe", "winner", "net_out_usd"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    
    csv_content = output.getvalue()
    
    if output_file:
        with open(output_file, "w") as f:
            f.write(csv_content)
        return f"Exported {len(rows)} rows to {output_file}"
    
    return csv_content
