# Methodology — Hyperliquid V1

## What is exact vs estimated

- **Exact:** Fees paid on Hyperliquid from fill-level `fee` + `builderFee` fields.
- **Estimated:** Slippage, because we do not replay full L2 book state for every fill.

## Slippage model (V1)

For each **taker fill** (`crossed=true`):

1. Map fill timestamp to its minute bucket.
2. Pull 1m candle for the same coin.
3. Build reference price: `OHLC4 = (open + high + low + close) / 4`.
4. Slippage cost:
   - Buy fill: `max(0, (fill_px - ref_px) * size)`
   - Sell fill: `max(0, (ref_px - fill_px) * size)`

This is conservative and easy to explain, but not microstructure-perfect.

## Counterfactual Orderly model (V1)

Given fee assumptions:
- `orderly_taker_bps` (default 3.0)
- `orderly_maker_bps` (default 0.0)
- `orderly_slippage_improvement_bps` (default 0.0)

Counterfactual fee per fill:
- taker: `notional * taker_bps / 10000`
- maker: `notional * maker_bps / 10000`

Counterfactual slippage per taker fill:
- `max(0, hl_slippage - notional * improvement_bps / 10000)`

## Headline formula

- `actual_total_cost = hl_fees + hl_builder_fees + hl_slippage_est`
- `orderly_total_cost = orderly_fees_cf + orderly_slippage_cf`
- `projected_savings = actual_total_cost - orderly_total_cost`

## Caveats

- Hyperliquid only (V1).
- Spot remapped symbols and sparse candles can reduce slippage coverage.
- Use **fee-only savings** as conservative baseline.
