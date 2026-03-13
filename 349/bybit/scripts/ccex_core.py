#!/usr/bin/env python3
"""
ccex-core: Shared CCXT engine for all Starchild CEX skills.
Used internally by exchange-specific skills (binance, bybit, okx, etc.)
Not published to the marketplace directly.

Usage:
    python ccex_core.py <action> [--exchange <name>] [options]

Actions:
    balance          - Get account balances
    ticker           - Get ticker for a symbol
    orderbook        - Get orderbook for a symbol
    markets          - List all available markets
    order            - Place an order
    cancel           - Cancel an order
    orders           - List open orders
    history          - Order history
    position         - Get open positions (futures)
    ohlcv            - Get OHLCV candlestick data
    oco              - Place an OCO order (Binance only)
"""

import os
import sys
import json
import argparse
import ccxt

# ──────────────────────────────────────────────
# Exchange factory
# ──────────────────────────────────────────────

EXCHANGE_ENV_KEYS = {
    "binance":  ("BINANCE_API_KEY",  "BINANCE_SECRET"),
    "bybit":    ("BYBIT_API_KEY",    "BYBIT_SECRET"),
    "okx":      ("OKX_API_KEY",      "OKX_SECRET",   "OKX_PASSPHRASE"),
    "coinbase": ("COINBASE_API_KEY", "COINBASE_SECRET"),
    "kraken":   ("KRAKEN_API_KEY",   "KRAKEN_SECRET"),
    "kucoin":   ("KUCOIN_API_KEY",   "KUCOIN_SECRET", "KUCOIN_PASSPHRASE"),
    "gateio":   ("GATEIO_API_KEY",   "GATEIO_SECRET"),
    "mexc":     ("MEXC_API_KEY",     "MEXC_SECRET"),
    "htx":      ("HTX_API_KEY",      "HTX_SECRET"),
    "bitget":   ("BITGET_API_KEY",   "BITGET_SECRET", "BITGET_PASSPHRASE"),
}

def get_exchange(exchange_id: str, futures: bool = False) -> ccxt.Exchange:
    """Create and authenticate a CCXT exchange instance."""
    exchange_id = exchange_id.lower()

    if exchange_id not in dir(ccxt):
        raise ValueError(f"Exchange '{exchange_id}' not supported by CCXT")

    env_keys = EXCHANGE_ENV_KEYS.get(exchange_id, ())

    config = {"enableRateLimit": True}

    if len(env_keys) >= 2:
        api_key = os.environ.get(env_keys[0])
        secret  = os.environ.get(env_keys[1])
        if api_key and secret:
            config["apiKey"] = api_key
            config["secret"] = secret

    if len(env_keys) == 3:
        passphrase = os.environ.get(env_keys[2])
        if passphrase:
            config["password"] = passphrase

    # Futures mode
    if futures:
        if exchange_id == "binance":
            config["options"] = {"defaultType": "future"}
        elif exchange_id == "bybit":
            config["options"] = {"defaultType": "linear"}
        elif exchange_id == "okx":
            config["options"] = {"defaultType": "swap"}

    exchange_class = getattr(ccxt, exchange_id)
    return exchange_class(config)


# ──────────────────────────────────────────────
# Actions
# ──────────────────────────────────────────────

def action_balance(exchange: ccxt.Exchange, args) -> dict:
    balance = exchange.fetch_balance()
    # Filter to non-zero balances for cleaner output
    clean = {
        "total": {k: v for k, v in balance["total"].items() if v and v > 0},
        "free":  {k: v for k, v in balance["free"].items()  if v and v > 0},
        "used":  {k: v for k, v in balance["used"].items()  if v and v > 0},
    }
    return clean


def action_ticker(exchange: ccxt.Exchange, args) -> dict:
    if not args.symbol:
        raise ValueError("--symbol required for ticker")
    return exchange.fetch_ticker(args.symbol)


def action_orderbook(exchange: ccxt.Exchange, args) -> dict:
    if not args.symbol:
        raise ValueError("--symbol required for orderbook")
    limit = args.limit or 20
    ob = exchange.fetch_order_book(args.symbol, limit)
    return {
        "symbol": args.symbol,
        "bids": ob["bids"][:10],
        "asks": ob["asks"][:10],
        "timestamp": ob.get("timestamp"),
    }


def action_markets(exchange: ccxt.Exchange, args) -> list:
    markets = exchange.load_markets()
    result = []
    for symbol, m in list(markets.items())[:100]:  # cap at 100 for readability
        result.append({
            "symbol": symbol,
            "base": m.get("base"),
            "quote": m.get("quote"),
            "type": m.get("type"),
            "active": m.get("active"),
        })
    return result


def action_ohlcv(exchange: ccxt.Exchange, args) -> list:
    if not args.symbol:
        raise ValueError("--symbol required for ohlcv")
    timeframe = args.timeframe or "1h"
    limit = args.limit or 100
    ohlcv = exchange.fetch_ohlcv(args.symbol, timeframe, limit=limit)
    return [
        {"timestamp": c[0], "open": c[1], "high": c[2], "low": c[3], "close": c[4], "volume": c[5]}
        for c in ohlcv
    ]


def action_order(exchange: ccxt.Exchange, args) -> dict:
    """Place a standard order using CCXT unified API."""
    if not args.symbol:
        raise ValueError("--symbol required")
    if not args.side:
        raise ValueError("--side required (buy/sell)")
    if not args.type:
        raise ValueError("--type required (market/limit/stop/etc.)")
    if not args.amount:
        raise ValueError("--amount required")

    params = {}

    # Stop/trigger price
    if args.stop_price:
        params["stopPrice"] = float(args.stop_price)

    # Trailing
    if args.trailing_delta:
        params["trailingDelta"] = int(args.trailing_delta)

    # Reduce only (futures)
    if args.reduce_only:
        params["reduceOnly"] = True

    # Post only
    if args.post_only:
        params["postOnly"] = True

    price = float(args.price) if args.price else None
    amount = float(args.amount)

    order = exchange.create_order(
        symbol=args.symbol,
        type=args.type,
        side=args.side,
        amount=amount,
        price=price,
        params=params,
    )
    return order


def action_oco(exchange: ccxt.Exchange, args) -> dict:
    """
    Place an OCO order.
    Currently supported: Binance (raw API), simulated on others.

    OCO = One-Cancels-the-Other
    Requires: symbol, side, amount, price (limit), stop_price, stop_limit_price
    """
    if not all([args.symbol, args.side, args.amount, args.price, args.stop_price]):
        raise ValueError("OCO requires --symbol, --side, --amount, --price, --stop_price")

    exchange_id = exchange.id.lower()

    if exchange_id == "binance":
        # Binance native OCO via raw API
        stop_limit_price = args.stop_limit_price or str(float(args.stop_price) * 0.999)
        result = exchange.private_post_order_oco({
            "symbol": exchange.market_id(args.symbol),
            "side": args.side.upper(),
            "quantity": args.amount,
            "price": args.price,
            "stopPrice": args.stop_price,
            "stopLimitPrice": stop_limit_price,
            "stopLimitTimeInForce": "GTC",
        })
        return {"type": "native_oco", "exchange": "binance", "result": result}

    else:
        # Simulate OCO with two separate orders + warning
        limit_order = exchange.create_order(
            symbol=args.symbol,
            type="limit",
            side=args.side,
            amount=float(args.amount),
            price=float(args.price),
        )
        stop_order = exchange.create_order(
            symbol=args.symbol,
            type="stop",
            side=args.side,
            amount=float(args.amount),
            price=float(args.stop_price),
            params={"stopPrice": float(args.stop_price)},
        )
        return {
            "type": "simulated_oco",
            "exchange": exchange_id,
            "warning": f"{exchange_id} does not support native OCO. Placed as two separate orders. You must cancel one manually when the other fills.",
            "limit_order": limit_order,
            "stop_order": stop_order,
        }


def action_cancel(exchange: ccxt.Exchange, args) -> dict:
    if not args.order_id:
        raise ValueError("--order_id required")
    if not args.symbol:
        raise ValueError("--symbol required")
    return exchange.cancel_order(args.order_id, args.symbol)


def action_orders(exchange: ccxt.Exchange, args) -> list:
    symbol = args.symbol or None
    return exchange.fetch_open_orders(symbol)


def action_history(exchange: ccxt.Exchange, args) -> list:
    symbol = args.symbol or None
    limit = args.limit or 50
    return exchange.fetch_closed_orders(symbol, limit=limit)


def action_position(exchange: ccxt.Exchange, args) -> list:
    symbol = args.symbol or None
    if hasattr(exchange, 'fetch_positions'):
        positions = exchange.fetch_positions([symbol] if symbol else None)
        return [p for p in positions if p.get("contracts") and p["contracts"] > 0]
    return []


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

ACTION_MAP = {
    "balance":   action_balance,
    "ticker":    action_ticker,
    "orderbook": action_orderbook,
    "markets":   action_markets,
    "ohlcv":     action_ohlcv,
    "order":     action_order,
    "oco":       action_oco,
    "cancel":    action_cancel,
    "orders":    action_orders,
    "history":   action_history,
    "position":  action_position,
}


def main():
    parser = argparse.ArgumentParser(description="ccex-core CCXT engine")
    parser.add_argument("action", choices=list(ACTION_MAP.keys()))
    parser.add_argument("--exchange",         required=True,  help="Exchange ID (binance, bybit, okx, ...)")
    parser.add_argument("--symbol",           help="Trading pair, e.g. BTC/USDT")
    parser.add_argument("--side",             help="buy or sell")
    parser.add_argument("--type",             help="order type: market, limit, stop, stop_limit")
    parser.add_argument("--amount",           help="Order amount in base currency")
    parser.add_argument("--price",            help="Limit price")
    parser.add_argument("--stop_price",       help="Stop/trigger price")
    parser.add_argument("--stop_limit_price", help="Stop limit price (OCO)")
    parser.add_argument("--trailing_delta",   help="Trailing delta in BIPS (Binance)")
    parser.add_argument("--order_id",         help="Order ID for cancel")
    parser.add_argument("--timeframe",        help="OHLCV timeframe, e.g. 1h, 4h, 1d")
    parser.add_argument("--limit",            type=int, help="Result limit")
    parser.add_argument("--futures",          action="store_true", help="Use futures/perp market")
    parser.add_argument("--reduce_only",      action="store_true", help="Reduce-only order")
    parser.add_argument("--post_only",        action="store_true", help="Post-only (maker) order")

    args = parser.parse_args()

    try:
        exchange = get_exchange(args.exchange, futures=args.futures)
        result = ACTION_MAP[args.action](exchange, args)
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
