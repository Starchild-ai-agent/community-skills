#!/usr/bin/env python3
"""
Lighter DEX API Tools
Complete trading tools for Lighter DEX mainnet

IMPORTANT: Requires asyncio event loop for all operations.
All functions must be called within an async context or use asyncio.run().
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from lighter import SignerClient

# Configuration
API_BASE = "https://mainnet.zklighter.elliot.ai"

def get_client():
    """
    Get authenticated Lighter client from environment.
    
    Requires these environment variables:
    - LIGHTER_API_KEY_PRIVATE: Your private key (with 0x prefix)
    - LIGHTER_API_KEY_INDEX: Your API key index (2-255)
    - LIGHTER_ACCOUNT_INDEX: Your account index (usually 0)
    """
    api_key_private = os.getenv("LIGHTER_API_KEY_PRIVATE")
    api_key_index = int(os.getenv("LIGHTER_API_KEY_INDEX", "2"))
    account_index = int(os.getenv("LIGHTER_ACCOUNT_INDEX", "0"))
    
    if not api_key_private:
        raise ValueError("LIGHTER_API_KEY_PRIVATE not set in environment")
    
    if not api_key_private.startswith("0x"):
        api_key_private = "0x" + api_key_private
    
    # Create event loop if not exists
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.new_event_loop()
        asyncio.set_event_loop(asyncio.get_event_loop())
    
    return SignerClient(
        url=API_BASE,
        account_index=account_index,
        api_private_keys={api_key_index: api_key_private}
    )


def lighter_account():
    """Get account information"""
    client = get_client()
    account = client.get_account()
    return {
        "address": account.address,
        "available_balance": float(account.available_balance) / 1e6,  # Convert from micro USDC
        "total_balance": float(account.total_balance) / 1e6,
        "total_open_orders": account.total_open_orders,
        "total_positions": account.total_positions
    }


def lighter_holdings():
    """Get account holdings (balances)"""
    client = get_client()
    holdings = client.get_holdings()
    result = []
    for h in holdings:
        result.append({
            "token": h.token,
            "available": float(h.available) / 1e6,
            "total": float(h.total) / 1e6,
            "in_orders": float(h.in_orders) / 1e6
        })
    return result


def lighter_positions():
    """Get open positions"""
    client = get_client()
    positions = client.get_positions()
    result = []
    for p in positions:
        result.append({
            "symbol": p.symbol,
            "size": float(p.size),
            "side": p.side.name,
            "entry_price": float(p.entry_price),
            "mark_price": float(p.mark_price),
            "unrealized_pnl": float(p.unrealized_pnl),
            "leverage": p.leverage
        })
    return result


def lighter_liquidation():
    """Get liquidation prices for all positions"""
    client = get_client()
    positions = client.get_positions()
    result = []
    for p in positions:
        liq_price = float(p.liquidation_price) if p.liquidation_price else None
        result.append({
            "symbol": p.symbol,
            "side": p.side.name,
            "size": float(p.size),
            "leverage": p.leverage,
            "entry_price": float(p.entry_price),
            "mark_price": float(p.mark_price),
            "liquidation_price": liq_price,
            "distance_to_liquidation": f"{((float(p.mark_price) - liq_price) / float(p.mark_price) * 100):.2f}%" if liq_price and p.side == Side.LONG else f"{((liq_price - float(p.mark_price)) / float(p.mark_price) * 100):.2f}%" if liq_price else "N/A"
        })
    return result


def lighter_leverage(symbol: str, leverage: int):
    """
    Set leverage for a symbol
    
    Args:
        symbol: Market symbol (e.g., "BTC", "XAU", "AAPL")
        leverage: Leverage multiplier (1-100)
    """
    client = get_client()
    # Validate leverage
    if leverage < 1 or leverage > 100:
        raise ValueError("Leverage must be between 1 and 100")
    
    result = client.update_leverage(symbol, leverage)
    return {
        "symbol": symbol,
        "leverage": leverage,
        "status": "updated" if result else "failed"
    }


def lighter_market(symbol: str):
    """Get market info for a symbol"""
    client = get_client()
    market = client.get_market(symbol)
    return {
        "symbol": market.symbol,
        "base": market.base,
        "quote": market.quote,
        "min_size": float(market.min_size),
        "tick_size": float(market.tick_size),
        "max_leverage": market.max_leverage,
        "status": market.status.name
    }


def lighter_markets_list(search: str = None, category: str = None):
    """
    List all available markets with optional filtering
    
    Args:
        search: Search term (e.g., "BTC", "gold", "AAPL")
        category: Filter by category ("crypto", "forex", "commodities", "stocks")
    """
    client = get_client()
    markets = client.get_markets()
    
    result = []
    for m in markets:
        # Apply search filter
        if search:
            search_lower = search.lower()
            if search_lower not in m.symbol.lower() and search_lower not in m.base.lower() and search_lower not in m.quote.lower():
                continue
        
        # Apply category filter
        if category:
            category_map = {
                "crypto": ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK", "MATIC", "DOT", "UNI", "ATOM", "LTC", "BCH", "ALGO", "XLM", "VET", "ICP", "FIL", "TRX", "ETC", "NEAR", "APT", "ARB", "OP", "HBAR", "INJ", "TAO", "SUI", "SEI", "TIA", "WIF", "PEPE", "BONK"],
                "forex": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"],
                "commodities": ["XAU", "XAG", "XPT", "XPD", "USOIL", "UKOIL", "NATGAS", "CORN", "WHEAT", "SOYBEAN", "SUGAR", "COFFEE", "COTTON"],
                "stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "V", "JPM", "WMT", "JNJ", "PG", "MA", "HD", "DIS", "PYPL", "BAC", "ADBE", "CRM", "NFLX", "XOM", "KO", "PEP", "MRK", "PFE", "T", "VZ", "INTC", "CSCO"]
            }
            if category.lower() in category_map:
                if m.base not in category_map[category.lower()]:
                    continue
        
        result.append({
            "symbol": m.symbol,
            "base": m.base,
            "quote": m.quote,
            "min_size": float(m.min_size),
            "tick_size": float(m.tick_size),
            "max_leverage": m.max_leverage,
            "status": m.status.name
        })
    
    return {
        "count": len(result),
        "markets": result[:50]  # Limit to 50 for readability
    }


def lighter_orderbook(symbol: str, levels: int = 20):
    """Get orderbook for a symbol"""
    client = get_client()
    ob = client.get_orderbook(symbol, levels)
    return {
        "symbol": symbol,
        "bids": [[float(b[0]), float(b[1])] for b in ob.bids],
        "asks": [[float(a[0]), float(a[1])] for a in ob.asks],
        "spread": float(ob.asks[0][0]) - float(ob.bids[0][0]) if ob.asks and ob.bids else None,
        "mid_price": (float(ob.asks[0][0]) + float(ob.bids[0][0])) / 2 if ob.asks and ob.bids else None
    }


def lighter_candles(symbol: str, interval: str = "1h", limit: int = 100):
    """Get candlestick data"""
    client = get_client()
    candles = client.get_candles(symbol, interval, limit)
    result = []
    for c in candles:
        result.append({
            "timestamp": c.timestamp,
            "open": float(c.open),
            "high": float(c.high),
            "low": float(c.low),
            "close": float(c.close),
            "volume": float(c.volume)
        })
    return result


def lighter_funding(symbol: str):
    """Get funding rate for a symbol"""
    client = get_client()
    funding = client.get_funding(symbol)
    return {
        "symbol": symbol,
        "current_rate": float(funding.current_rate),
        "predicted_rate": float(funding.predicted_rate),
        "next_funding_time": funding.next_funding_time
    }


def lighter_open_orders(symbol: str = None):
    """Get open orders, optionally filtered by symbol"""
    client = get_client()
    orders = client.get_open_orders(symbol)
    result = []
    for o in orders:
        result.append({
            "order_id": o.order_id,
            "symbol": o.symbol,
            "side": o.side.name,
            "type": o.type.name,
            "price": float(o.price) if o.price else None,
            "size": float(o.size),
            "filled": float(o.filled),
            "time_in_force": o.time_in_force.name if o.time_in_force else None,
            "created_at": o.created_at
        })
    return result


def lighter_order(
    symbol: str,
    side: str,
    size: float,
    order_type: str = "LIMIT",
    price: float = None,
    trigger_price: float = None,
    limit_price: float = None,
    time_in_force: str = "GTC",
    expiry_time: str = None,
    reduce_only: bool = False
):
    """
    Place an order on Lighter DEX
    
    Args:
        symbol: Market symbol (e.g., "BTC", "XAU", "AAPL")
        side: "buy" or "sell"
        size: Order size in base asset
        order_type: Order type - "LIMIT", "MARKET", "STOP", "STOP_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT"
        price: Limit price (required for LIMIT, STOP_LIMIT, TAKE_PROFIT_LIMIT)
        trigger_price: Trigger price for stop/take profit orders
        limit_price: Limit price for stop-limit/take-profit-limit orders (alternative to price)
        time_in_force: "GTC" (Good 'Til Cancel), "GTT" (Good 'Til Time), "IOC" (Immediate or Cancel), "POST_ONLY"
        expiry_time: Expiry time for GTT orders (ISO format: "2024-12-31T23:59:59Z")
        reduce_only: If true, only reduces existing position
    
    Returns:
        Order confirmation with order_id, status, filled size
    """
    client = get_client()
    
    # Map order type string to enum
    order_type_map = {
        "LIMIT": OrderType.LIMIT,
        "MARKET": OrderType.MARKET,
        "STOP": OrderType.STOP,
        "STOP_LIMIT": OrderType.STOP_LIMIT,
        "TAKE_PROFIT": OrderType.TAKE_PROFIT,
        "TAKE_PROFIT_LIMIT": OrderType.TAKE_PROFIT_LIMIT
    }
    
    if order_type.upper() not in order_type_map:
        raise ValueError(f"Invalid order type. Must be one of: {list(order_type_map.keys())}")
    
    ot = order_type_map[order_type.upper()]
    
    # Map side string to enum
    side_map = {"buy": Side.BUY, "sell": Side.SELL}
    if side.lower() not in side_map:
        raise ValueError("Side must be 'buy' or 'sell'")
    
    sd = side_map[side.lower()]
    
    # Map time_in_force string to enum
    tif_map = {
        "GTC": TimeInForce.GTC,
        "GTT": TimeInForce.GTT,
        "IOC": TimeInForce.IOC,
        "POST_ONLY": TimeInForce.POST_ONLY
    }
    
    tif = tif_map.get(time_in_force.upper(), TimeInForce.GTC)
    
    # Build order params
    params = OrderParams(
        symbol=symbol,
        side=sd,
        size=size,
        order_type=ot,
        price=price,
        trigger_price=trigger_price,
        time_in_force=tif,
        reduce_only=reduce_only
    )
    
    # Handle expiry time for GTT orders
    if expiry_time and tif == TimeInForce.GTT:
        params.expiry_time = expiry_time
    
    # Place order
    result = client.place_order(params)
    
    return {
        "order_id": result.order_id,
        "symbol": symbol,
        "side": side.upper(),
        "type": order_type.upper(),
        "size": size,
        "price": price,
        "trigger_price": trigger_price,
        "status": "placed",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def lighter_stop_loss(symbol: str, side: str, size: float, trigger_price: float, reduce_only: bool = True):
    """
    Place a stop loss order (market order when triggered)
    
    Args:
        symbol: Market symbol
        side: "buy" or "sell" (direction to close position)
        size: Order size
        trigger_price: Price that triggers the stop loss
        reduce_only: If true, only reduces position (default: True)
    """
    return lighter_order(
        symbol=symbol,
        side=side,
        size=size,
        order_type="STOP",
        trigger_price=trigger_price,
        reduce_only=reduce_only
    )


def lighter_stop_limit(symbol: str, side: str, size: float, trigger_price: float, limit_price: float, reduce_only: bool = True):
    """
    Place a stop limit order (limit order when triggered)
    
    Args:
        symbol: Market symbol
        side: "buy" or "sell"
        size: Order size
        trigger_price: Price that triggers the order
        limit_price: Limit price for the order when triggered
        reduce_only: If true, only reduces position (default: True)
    """
    return lighter_order(
        symbol=symbol,
        side=side,
        size=size,
        order_type="STOP_LIMIT",
        trigger_price=trigger_price,
        price=limit_price,
        reduce_only=reduce_only
    )


def lighter_take_profit(symbol: str, side: str, size: float, trigger_price: float, reduce_only: bool = True):
    """
    Place a take profit order (market order when triggered)
    
    Args:
        symbol: Market symbol
        side: "buy" or "sell" (direction to close position)
        size: Order size
        trigger_price: Price that triggers the take profit
        reduce_only: If true, only reduces position (default: True)
    """
    return lighter_order(
        symbol=symbol,
        side=side,
        size=size,
        order_type="TAKE_PROFIT",
        trigger_price=trigger_price,
        reduce_only=reduce_only
    )


def lighter_take_profit_limit(symbol: str, side: str, size: float, trigger_price: float, limit_price: float, reduce_only: bool = True):
    """
    Place a take profit limit order (limit order when triggered)
    
    Args:
        symbol: Market symbol
        side: "buy" or "sell"
        size: Order size
        trigger_price: Price that triggers the order
        limit_price: Limit price for the order when triggered
        reduce_only: If true, only reduces position (default: True)
    """
    return lighter_order(
        symbol=symbol,
        side=side,
        size=size,
        order_type="TAKE_PROFIT_LIMIT",
        trigger_price=trigger_price,
        price=limit_price,
        reduce_only=reduce_only
    )


def lighter_twap_order(symbol: str, side: str, total_amount: float, duration_seconds: int = 3600, slice_interval: int = 30):
    """
    Create a TWAP (Time-Weighted Average Price) order
    
    Args:
        symbol: Market symbol
        side: "buy" or "sell"
        total_amount: Total amount to execute
        duration_seconds: Total duration for TWAP execution (default: 1 hour)
        slice_interval: Interval between slices in seconds (default: 30s)
    
    Returns:
        TWAP order confirmation with order IDs for each slice
    """
    client = get_client()
    
    # Calculate number of slices
    num_slices = duration_seconds // slice_interval
    if num_slices < 1:
        num_slices = 1
    
    slice_size = total_amount / num_slices
    
    result = client.create_twap_order(
        symbol=symbol,
        side=Side.BUY if side.lower() == "buy" else Side.SELL,
        total_amount=total_amount,
        duration_seconds=duration_seconds,
        slice_interval=slice_interval
    )
    
    return {
        "twap_id": result.twap_id if hasattr(result, 'twap_id') else "twap_" + str(datetime.utcnow().timestamp()),
        "symbol": symbol,
        "side": side.upper(),
        "total_amount": total_amount,
        "num_slices": num_slices,
        "slice_size": slice_size,
        "duration_seconds": duration_seconds,
        "slice_interval": slice_interval,
        "status": "created",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def lighter_cancel(symbol: str, order_id: int):
    """Cancel an order"""
    client = get_client()
    result = client.cancel_order(symbol, order_id)
    return {
        "order_id": order_id,
        "symbol": symbol,
        "status": "cancelled" if result else "failed"
    }


def lighter_cancel_all(symbol: str = None):
    """Cancel all open orders, optionally for a specific symbol"""
    client = get_client()
    result = client.cancel_all_orders(symbol)
    return {
        "symbol": symbol or "all",
        "cancelled_count": len(result) if result else 0,
        "status": "success"
    }


def lighter_modify_order(symbol: str, order_id: int, side: str, new_size: float = None, new_price: float = None):
    """
    Modify an existing order
    
    Args:
        symbol: Market symbol
        order_id: Order ID to modify
        side: "buy" or "sell"
        new_size: New order size (optional)
        new_price: New limit price (optional)
    
    Returns:
        Modified order confirmation
    """
    client = get_client()
    
    # Get current order to preserve other parameters
    orders = client.get_open_orders(symbol)
    current_order = None
    for o in orders:
        if o.order_id == order_id:
            current_order = o
            break
    
    if not current_order:
        raise ValueError(f"Order {order_id} not found")
    
    # Build new params
    size = new_size if new_size else float(current_order.size)
    price = new_price if new_price else (float(current_order.price) if current_order.price else None)
    
    result = client.modify_order(
        symbol=symbol,
        order_id=order_id,
        side=Side.BUY if side.lower() == "buy" else Side.SELL,
        size=size,
        price=price
    )
    
    return {
        "order_id": order_id,
        "symbol": symbol,
        "new_size": size,
        "new_price": price,
        "status": "modified" if result else "failed"
    }


def lighter_trades(symbol: str, limit: int = 50):
    """Get recent trades for a symbol"""
    client = get_client()
    trades = client.get_trades(symbol, limit)
    result = []
    for t in trades:
        result.append({
            "trade_id": t.trade_id,
            "price": float(t.price),
            "size": float(t.size),
            "side": t.side.name,
            "timestamp": t.timestamp
        })
    return result


def lighter_stats():
    """Get platform-wide statistics"""
    client = get_client()
    stats = client.get_stats()
    return {
        "volume_24h": float(stats.volume_24h) / 1e6 if stats.volume_24h else 0,
        "trades_24h": stats.trades_24h,
        "open_interest": float(stats.open_interest) / 1e6 if stats.open_interest else 0
    }


if __name__ == "__main__":
    # Quick test
    print("Testing Lighter DEX connection...")
    try:
        account = lighter_account()
        print(f"✅ Connected: {account['address'][:10]}...")
        print(f"   Balance: ${account['available_balance']:.2f}")
    except Exception as e:
        print(f"❌ Error: {e}")
