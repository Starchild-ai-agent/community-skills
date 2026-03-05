#!/usr/bin/env python3
"""
Copy Trade Orchestrator
Bridges the copy engine's diff output with Hyperliquid order execution.

This script:
1. Runs copy_engine to detect position changes
2. Outputs structured JSON actions for the agent to execute via hl_order
3. Updates state tracking after execution

Usage:
  python3 orchestrator.py --target 0x... --mode fixed --fixed-size 50 --leverage 5
  python3 orchestrator.py --target 0x... --mode proportional --my-account 200
  python3 orchestrator.py --status  # Show current copy state
  python3 orchestrator.py --stop    # Clear all tracked positions
"""

import json
import sys
import os
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from copy_engine import (
    get_target_positions, load_state, save_state,
    compute_position_diff, log, STATE_FILE, LOG_FILE
)

HL_API = "https://api.hyperliquid.xyz/info"


def get_my_hl_state(my_address=None):
    """
    Get our actual HL positions.
    If no address provided, returns empty (agent will use hl_account tool).
    """
    if not my_address:
        return {}, 0

    import requests
    try:
        r = requests.post(HL_API, json={"type": "clearinghouseState", "user": my_address}, timeout=10)
        r.raise_for_status()
        data = r.json()
    except:
        return {}, 0

    positions = {}
    for pos in data.get("assetPositions", []):
        p = pos.get("position", {})
        coin = p.get("coin", "")
        size = float(p.get("szi", 0))
        if size == 0:
            continue
        entry = float(p.get("entryPx", 0))
        lev_info = p.get("leverage", {})
        lev = int(lev_info.get("value", 1)) if isinstance(lev_info, dict) else 1
        positions[coin] = {
            "coin": coin,
            "size": size,
            "side": "long" if size > 0 else "short",
            "entry_px": entry,
            "leverage": lev
        }

    account_value = float(data.get("marginSummary", {}).get("accountValue", 0))
    return positions, account_value


def generate_agent_commands(actions, dry_run=False):
    """
    Convert diff actions to structured commands the agent can execute.
    Returns JSON that maps directly to hl_order / hl_leverage / hl_cancel calls.
    """
    commands = []

    for a in actions:
        if a["action"] in ("open", "increase"):
            # Set leverage first, then place order
            commands.append({
                "tool": "hl_leverage",
                "params": {
                    "coin": a["coin"],
                    "leverage": a["leverage"],
                    "cross": True
                },
                "description": f"Set {a['coin']} leverage to {a['leverage']}x"
            })
            commands.append({
                "tool": "hl_order",
                "params": {
                    "coin": a["coin"],
                    "side": a["side"],
                    "size": a["size"]
                    # No price = market order
                },
                "description": f"Market {a['side']} {a['size']} {a['coin']} — {a['reason']}"
            })

        elif a["action"] in ("close", "decrease"):
            commands.append({
                "tool": "hl_order",
                "params": {
                    "coin": a["coin"],
                    "side": a["side"],
                    "size": a["size"],
                    "reduce_only": True
                },
                "description": f"Close {a['coin']} — {a['reason']}"
            })

    return commands


def update_tracked_state(target_address, target_positions, actions_executed):
    """Update our state file after execution."""
    state = load_state()

    # Update target snapshot
    state["target_snapshots"][target_address] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "positions": {p["coin"]: p for p in target_positions}
    }

    # Update my_positions based on executed actions
    for a in actions_executed:
        coin = a["coin"]
        if a["action"] in ("open", "increase"):
            state["my_positions"][coin] = {
                "coin": coin,
                "size": a["size"] if a["side"] == "buy" else -a["size"],
                "side": "long" if a["side"] == "buy" else "short",
                "leverage": a.get("leverage", 5),
                "opened_at": datetime.now(timezone.utc).isoformat(),
                "source": "copy_trade"
            }
        elif a["action"] in ("close", "decrease"):
            if coin in state["my_positions"]:
                del state["my_positions"][coin]

    # Log execution
    state["executions"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": target_address,
        "actions": len(actions_executed)
    })

    # Keep only last 100 executions
    state["executions"] = state["executions"][-100:]

    save_state(state)
    return state


def show_status():
    """Show current copy trade state."""
    state = load_state()

    print("\n" + "=" * 50)
    print("  Copy Trade Status")
    print("=" * 50)

    positions = state.get("my_positions", {})
    if not positions:
        print("\n  No copied positions active.")
    else:
        print(f"\n  Active copied positions: {len(positions)}")
        for coin, p in positions.items():
            emoji = "🟢" if p["side"] == "long" else "🔴"
            print(f"  {emoji} {coin}: {p['side']} {abs(p.get('size', 0))} @ {p.get('leverage', '?')}x")
            if p.get("opened_at"):
                print(f"     Opened: {p['opened_at']}")

    targets = state.get("target_snapshots", {})
    if targets:
        print(f"\n  Tracked targets: {len(targets)}")
        for addr, snap in targets.items():
            print(f"  📍 {addr[:12]}... — {len(snap.get('positions', {}))} positions")
            print(f"     Last checked: {snap.get('timestamp', 'unknown')}")

    execs = state.get("executions", [])
    if execs:
        print(f"\n  Recent executions: {len(execs)} total")
        for e in execs[-5:]:
            print(f"  ⚡ {e['timestamp']}: {e['actions']} actions for {e['target'][:12]}...")

    print()


def clear_state():
    """Clear all tracked state."""
    save_state({
        "my_positions": {},
        "target_snapshots": {},
        "daily_pnl": 0,
        "last_reset": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "executions": []
    })
    log("State cleared — all tracked positions removed.")


def main():
    parser = argparse.ArgumentParser(description="Copy Trade Orchestrator")
    parser.add_argument("--target", help="Target wallet address")
    parser.add_argument("--my-address", help="Your HL wallet address (for position lookup)")
    parser.add_argument("--mode", choices=["proportional", "fixed", "custom"], default="proportional")
    parser.add_argument("--fixed-size", type=float, default=50, help="USD per position (fixed mode)")
    parser.add_argument("--leverage", type=int, help="Override leverage for all positions")
    parser.add_argument("--max-leverage", type=int, default=10, help="Max leverage cap")
    parser.add_argument("--max-position", type=float, default=500, help="Max position size USD")
    parser.add_argument("--scale", type=float, default=1.0, help="Scale factor (proportional mode)")
    parser.add_argument("--my-account", type=float, default=200, help="Your account value USD")
    parser.add_argument("--blacklist", nargs="*", default=[], help="Coins to skip")
    parser.add_argument("--whitelist", nargs="*", default=[], help="Only copy these coins")
    parser.add_argument("--status", action="store_true", help="Show current state")
    parser.add_argument("--stop", action="store_true", help="Clear all state")
    parser.add_argument("--execute", action="store_true", help="Output commands for agent execution")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.stop:
        clear_state()
        return

    if not args.target:
        parser.print_help()
        sys.exit(1)

    # Get target positions
    target_positions, target_value = get_target_positions(args.target)
    if target_positions is None:
        log("Failed to fetch target positions", "ERROR")
        sys.exit(1)

    log(f"Target: {args.target[:12]}... — {len(target_positions)} positions, ${target_value:,.0f}")

    # Get our positions
    if args.my_address:
        my_positions, my_value = get_my_hl_state(args.my_address)
    else:
        state = load_state()
        my_positions = state.get("my_positions", {})
        my_value = args.my_account

    # Build config
    config = {
        "address": args.target,
        "mode": args.mode,
        "fixed_size_usd": args.fixed_size,
        "custom_sizes": {},
        "leverage": args.leverage,
        "max_leverage": args.max_leverage,
        "max_position_usd": args.max_position,
        "scale_factor": args.scale,
        "blacklist": args.blacklist or [],
        "whitelist": args.whitelist or [],
        "_target_account_value": target_value,
        "_my_account_value": my_value
    }

    # Compute diff
    actions = compute_position_diff(target_positions, my_positions, config)

    if not actions:
        log("No position changes needed — positions in sync.")
        print(json.dumps({"actions": [], "commands": [], "status": "in_sync"}, indent=2))
        return

    # Generate agent commands
    commands = generate_agent_commands(actions)

    # Output
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": args.target,
        "target_value": target_value,
        "target_positions": len(target_positions),
        "actions": actions,
        "commands": commands,
        "status": "actions_ready",
        "mode": args.mode,
        "dry_run": not args.execute
    }

    print(json.dumps(output, indent=2))

    if args.execute:
        log("⚡ Commands ready for agent execution via hl_order tool")
        # The agent reads the commands and executes them
        # After execution, call: update_tracked_state(target, target_positions, actions)


if __name__ == "__main__":
    main()
