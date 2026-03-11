#!/usr/bin/env python3
"""
Hyperliquid Copy Trade Engine
Monitors a target wallet and mirrors positions on your account.

Usage:
  python3 copy_engine.py --config config.json
  python3 copy_engine.py --target 0x... --mode proportional --poll 60
  python3 copy_engine.py --target 0x... --mode fixed --fixed-size 50 --leverage 5 --poll 60

Config JSON format:
{
  "targets": [
    {
      "address": "0x...",
      "label": "whale1",
      "mode": "proportional",     # proportional | fixed | custom
      "fixed_size_usd": null,     # USD per position (fixed mode)
      "custom_sizes": {},         # {"BTC": 0.001, "ETH": 0.01} (custom mode)
      "leverage": null,           # Override leverage (null = match target)
      "max_leverage": 10,         # Hard cap on leverage
      "scale_factor": 1.0,        # Multiplier for proportional mode
      "blacklist": [],            # Coins to skip
      "whitelist": [],            # Only copy these (empty = all)
      "max_position_usd": 500,   # Max single position size USD
      "enabled": true
    }
  ],
  "global": {
    "poll_interval": 60,          # Seconds between checks
    "daily_loss_limit_usd": 100,  # Stop if daily loss exceeds this
    "max_total_positions": 10,    # Max simultaneous positions
    "dry_run": false,             # Log only, don't execute
    "log_file": "copy_trade.log"
  }
}
"""

import json
import sys
import os
import time
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Add workspace to path for imports
sys.path.insert(0, "/data/workspace")

try:
    import requests
except ImportError:
    os.system("pip install --break-system-packages requests")
    import requests

HL_API = "https://api.hyperliquid.xyz/info"
HL_EXCHANGE = "https://api.hyperliquid.xyz/exchange"

# State file to track what we've mirrored
STATE_FILE = "/data/workspace/output/copy_trade_state.json"
LOG_FILE = "/data/workspace/output/copy_trade.log"


def log(msg, level="INFO"):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass


def post_info(req_type, payload=None):
    """Query Hyperliquid public info API."""
    body = {"type": req_type}
    if payload:
        body.update(payload)
    try:
        r = requests.post(HL_API, json=body, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log(f"API error ({req_type}): {e}", "ERROR")
        return None


def get_target_positions(address):
    """Get target wallet's current positions."""
    state = post_info("clearinghouseState", {"user": address})
    if not state:
        return None, None

    positions = []
    for pos in state.get("assetPositions", []):
        p = pos.get("position", {})
        coin = p.get("coin", "")
        size = float(p.get("szi", 0))
        entry = float(p.get("entryPx", 0))
        leverage_info = p.get("leverage", {})
        lev = int(leverage_info.get("value", 1)) if isinstance(leverage_info, dict) else 1

        if size == 0:
            continue

        positions.append({
            "coin": coin,
            "size": size,  # positive=long, negative=short
            "side": "long" if size > 0 else "short",
            "entry_px": entry,
            "leverage": lev,
            "notional_usd": abs(size * entry)
        })

    # Get account value for proportional scaling
    margin_summary = state.get("marginSummary", {})
    account_value = float(margin_summary.get("accountValue", 0))

    return positions, account_value


def get_my_positions():
    """Get our account's current positions via agent tools."""
    # This reads from the state file that the orchestrator updates
    state = load_state()
    return state.get("my_positions", {})


def load_state():
    """Load persistent state."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {
        "my_positions": {},
        "target_snapshots": {},
        "daily_pnl": 0,
        "last_reset": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "executions": []
    }


def save_state(state):
    """Save persistent state."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def compute_position_diff(target_positions, my_positions, config):
    """
    Compare target vs our positions, return actions needed.
    
    Returns list of:
      {"action": "open"|"close"|"increase"|"decrease",
       "coin": str, "side": "buy"|"sell", "size": float, "leverage": int}
    """
    mode = config.get("mode", "proportional")
    scale_factor = config.get("scale_factor", 1.0)
    fixed_size_usd = config.get("fixed_size_usd", 50)
    custom_sizes = config.get("custom_sizes", {})
    max_position_usd = config.get("max_position_usd", 500)
    max_leverage = config.get("max_leverage", 10)
    leverage_override = config.get("leverage")
    blacklist = set(config.get("blacklist", []))
    whitelist = set(config.get("whitelist", []))
    target_account_value = config.get("_target_account_value", 1)
    my_account_value = config.get("_my_account_value", 1)

    actions = []
    target_by_coin = {p["coin"]: p for p in target_positions}

    # --- Detect NEW positions and SIZE CHANGES ---
    for coin, tp in target_by_coin.items():
        if coin in blacklist:
            continue
        if whitelist and coin not in whitelist:
            continue

        # Calculate our desired size
        if mode == "proportional":
            ratio = my_account_value / target_account_value if target_account_value > 0 else 0
            desired_size = abs(tp["size"]) * ratio * scale_factor
        elif mode == "fixed":
            desired_size = fixed_size_usd / tp["entry_px"] if tp["entry_px"] > 0 else 0
        elif mode == "custom":
            if coin in custom_sizes:
                desired_size = custom_sizes[coin]
            else:
                continue  # Skip coins not in custom map
        else:
            continue

        # Apply max position cap
        desired_notional = desired_size * tp["entry_px"]
        if desired_notional > max_position_usd:
            desired_size = max_position_usd / tp["entry_px"]

        # Determine leverage
        lev = leverage_override if leverage_override else min(tp["leverage"], max_leverage)

        # Check what we currently have
        my_pos = my_positions.get(coin)

        if my_pos is None:
            # NEW position — open it
            side = "sell" if tp["side"] == "short" else "buy"
            actions.append({
                "action": "open",
                "coin": coin,
                "side": side,
                "size": round(desired_size, 6),
                "leverage": lev,
                "reason": f"Target opened {tp['side']} {coin}"
            })
        else:
            # Position exists — check if direction matches
            my_side = my_pos.get("side", "")
            if my_side != tp["side"]:
                # Direction flipped — close ours and open opposite
                close_side = "buy" if my_side == "short" else "sell"
                actions.append({
                    "action": "close",
                    "coin": coin,
                    "side": close_side,
                    "size": abs(my_pos.get("size", 0)),
                    "leverage": lev,
                    "reason": f"Target flipped {coin} from {my_side} to {tp['side']}"
                })
                open_side = "sell" if tp["side"] == "short" else "buy"
                actions.append({
                    "action": "open",
                    "coin": coin,
                    "side": open_side,
                    "size": round(desired_size, 6),
                    "leverage": lev,
                    "reason": f"Target flipped to {tp['side']} {coin}"
                })

    # --- Detect CLOSED positions ---
    for coin, my_pos in my_positions.items():
        if coin not in target_by_coin:
            close_side = "buy" if my_pos["side"] == "short" else "sell"
            actions.append({
                "action": "close",
                "coin": coin,
                "side": close_side,
                "size": abs(my_pos.get("size", 0)),
                "leverage": my_pos.get("leverage", 5),
                "reason": f"Target closed {coin}"
            })

    return actions


def format_actions_report(actions, dry_run=False):
    """Format actions into readable report."""
    if not actions:
        return "No position changes detected."

    prefix = "🔵 [DRY RUN] " if dry_run else "🟢 "
    lines = [f"\n{'='*50}", f"  Copy Trade Actions — {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}", f"{'='*50}"]

    for a in actions:
        emoji = "🟢" if a["action"] == "open" else "🔴" if a["action"] == "close" else "🟡"
        lines.append(f"{prefix}{emoji} {a['action'].upper()} {a['coin']}: {a['side']} {a['size']} @ {a['leverage']}x — {a['reason']}")

    return "\n".join(lines)


def generate_snapshot(target_address, target_positions, target_value, my_positions, actions, config):
    """Generate a JSON snapshot of current state."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": target_address,
        "target_account_value": target_value,
        "target_positions": len(target_positions),
        "my_positions": len(my_positions),
        "actions_needed": len(actions),
        "actions": actions,
        "config": {
            "mode": config.get("mode"),
            "dry_run": config.get("dry_run", False)
        }
    }


def run_single_check(config):
    """Run one iteration of the copy trade check."""
    target = config["address"]
    label = config.get("label", target[:10])

    log(f"Checking target: {label} ({target[:10]}...)")

    # Get target positions
    target_positions, target_value = get_target_positions(target)
    if target_positions is None:
        log(f"Failed to fetch target positions for {label}", "ERROR")
        return None

    log(f"Target has {len(target_positions)} positions, account value: ${target_value:,.0f}")

    # Inject target account value into config for proportional calc
    config["_target_account_value"] = target_value
    config["_my_account_value"] = config.get("my_account_value", 200)

    # Load our tracked state
    state = load_state()
    my_positions = state.get("my_positions", {})

    # Compute diff
    actions = compute_position_diff(target_positions, my_positions, config)

    # Report
    report = format_actions_report(actions, config.get("dry_run", True))
    log(report)

    # Generate snapshot
    snapshot = generate_snapshot(target, target_positions, target_value, my_positions, actions, config)

    return snapshot


def main():
    parser = argparse.ArgumentParser(description="Hyperliquid Copy Trade Engine")
    parser.add_argument("--config", help="Path to config JSON file")
    parser.add_argument("--target", help="Target wallet address")
    parser.add_argument("--mode", choices=["proportional", "fixed", "custom"], default="proportional")
    parser.add_argument("--fixed-size", type=float, default=50, help="USD per position (fixed mode)")
    parser.add_argument("--leverage", type=int, help="Override leverage")
    parser.add_argument("--max-leverage", type=int, default=10, help="Max leverage cap")
    parser.add_argument("--max-position", type=float, default=500, help="Max position size USD")
    parser.add_argument("--scale", type=float, default=1.0, help="Scale factor (proportional mode)")
    parser.add_argument("--my-account", type=float, default=200, help="Your account value USD")
    parser.add_argument("--poll", type=int, default=0, help="Poll interval seconds (0=one-shot)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Log only, don't execute")
    parser.add_argument("--live", action="store_true", help="Actually execute trades")
    parser.add_argument("--blacklist", nargs="*", default=[], help="Coins to skip")
    parser.add_argument("--whitelist", nargs="*", default=[], help="Only copy these coins")

    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            full_config = json.load(f)
        # Process all targets
        for target_config in full_config.get("targets", []):
            if not target_config.get("enabled", True):
                continue
            target_config["dry_run"] = full_config.get("global", {}).get("dry_run", True)
            target_config["my_account_value"] = args.my_account
            snapshot = run_single_check(target_config)
            if snapshot:
                print(json.dumps(snapshot, indent=2))
    elif args.target:
        config = {
            "address": args.target,
            "label": args.target[:10],
            "mode": args.mode,
            "fixed_size_usd": args.fixed_size,
            "custom_sizes": {},
            "leverage": args.leverage,
            "max_leverage": args.max_leverage,
            "max_position_usd": args.max_position,
            "scale_factor": args.scale,
            "blacklist": args.blacklist or [],
            "whitelist": args.whitelist or [],
            "dry_run": not args.live,
            "my_account_value": args.my_account
        }

        if args.poll > 0:
            log(f"Starting copy trade loop — polling every {args.poll}s")
            log(f"Mode: {args.mode} | Leverage: {args.leverage or 'match target'} | Dry run: {config['dry_run']}")
            while True:
                try:
                    snapshot = run_single_check(config)
                    if snapshot and snapshot["actions_needed"] > 0:
                        print(json.dumps(snapshot, indent=2))
                except Exception as e:
                    log(f"Error in poll loop: {e}", "ERROR")
                time.sleep(args.poll)
        else:
            snapshot = run_single_check(config)
            if snapshot:
                print(json.dumps(snapshot, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
