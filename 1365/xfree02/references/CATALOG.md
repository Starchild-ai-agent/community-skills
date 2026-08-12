# Nansen x402 Endpoints Catalog

_Source: docs.nansen.ai/llms-full.txt_  
_Generated: 2026-08-12T11:28:43Z_

**Matched: 45/54**  
Body sources: body_source=generated: 44, body_source=none: 10

## Summary

| # | Method | Path | Price ($) | body_source | required fields | matched |
|---|--------|------|-----------|-------------|-----------------|---------|
| 1 | POST | `/api/v1/agent/fast` | 2.00 | generated | 1 | True |
| 2 | POST | `/api/v1/chains/chain-rank` | 0.01 | none | 0 | False |
| 3 | POST | `/api/v1/nansen-score/top-tokens` | 0.01 | none | 0 | False |
| 4 | POST | `/api/v1/perp-leaderboard` | 0.05 | generated | 1 | True |
| 5 | POST | `/api/v1/perp-screener` | 0.01 | generated | 1 | True |
| 6 | POST | `/api/v1/prediction-market/address-summary` | 0.01 | none | 0 | False |
| 7 | POST | `/api/v1/prediction-market/categories` | 0.01 | generated | 0 | True |
| 8 | POST | `/api/v1/prediction-market/event-screener` | 0.01 | generated | 0 | True |
| 9 | POST | `/api/v1/prediction-market/market-screener` | 0.01 | generated | 0 | True |
| 10 | POST | `/api/v1/prediction-market/ohlcv` | 0.01 | none | 0 | False |
| 11 | POST | `/api/v1/prediction-market/orderbook` | 0.01 | generated | 1 | True |
| 12 | POST | `/api/v1/prediction-market/pnl-by-market` | 0.05 | none | 0 | True |
| 13 | POST | `/api/v1/prediction-market/position-detail` | 0.05 | none | 0 | False |
| 14 | POST | `/api/v1/prediction-market/top-holders` | 0.05 | none | 0 | False |
| 15 | POST | `/api/v1/prediction-market/trades-by-market` | 0.01 | none | 0 | False |
| 16 | POST | `/api/v1/profiler/address/counterparties` | 0.05 | generated | 2 | True |
| 17 | POST | `/api/v1/profiler/address/current-balance` | 0.01 | generated | 1 | True |
| 18 | POST | `/api/v1/profiler/address/historical-balances` | 0.01 | generated | 2 | True |
| 19 | POST | `/api/v1/profiler/address/pnl` | 0.01 | generated | 2 | True |
| 20 | POST | `/api/v1/profiler/address/pnl-summary` | 0.01 | generated | 2 | True |
| 21 | POST | `/api/v1/profiler/address/related-wallets` | 0.01 | generated | 2 | True |
| 22 | POST | `/api/v1/profiler/address/transactions` | 0.01 | generated | 3 | True |
| 23 | POST | `/api/v1/profiler/dex-trades` | 0.01 | generated | 3 | True |
| 24 | POST | `/api/v1/profiler/perp-positions` | 0.01 | generated | 1 | True |
| 25 | POST | `/api/v1/profiler/perp-trades` | 0.01 | generated | 2 | True |
| 26 | POST | `/api/v1/smart-money/dcas` | 0.05 | generated | 0 | True |
| 27 | POST | `/api/v1/smart-money/dex-trades` | 0.05 | generated | 1 | True |
| 28 | POST | `/api/v1/smart-money/holdings` | 0.05 | generated | 1 | True |
| 29 | POST | `/api/v1/smart-money/netflow` | 0.05 | generated | 1 | True |
| 30 | POST | `/api/v1/smart-money/perp-trades` | 0.05 | generated | 0 | True |
| 31 | POST | `/api/v1/smart-money/pnl-leaderboard` | 0.05 | none | 0 | False |
| 32 | POST | `/api/v1/tgm/dex-trades` | 0.01 | generated | 3 | True |
| 33 | POST | `/api/v1/tgm/flow-intelligence` | 0.01 | generated | 2 | True |
| 34 | POST | `/api/v1/tgm/flows` | 0.01 | generated | 3 | True |
| 35 | POST | `/api/v1/tgm/holders` | 0.05 | generated | 2 | True |
| 36 | POST | `/api/v1/tgm/jup-dca` | 0.01 | generated | 1 | True |
| 37 | POST | `/api/v1/tgm/pnl-leaderboard` | 0.05 | generated | 3 | True |
| 38 | POST | `/api/v1/tgm/position-intelligence` | 0.01 | generated | 1 | True |
| 39 | POST | `/api/v1/tgm/token-information` | 0.01 | generated | 3 | True |
| 40 | POST | `/api/v1/tgm/token-ohlcv` | 0.01 | generated | 2 | True |
| 41 | POST | `/api/v1/tgm/transfers` | 0.01 | generated | 3 | True |
| 42 | POST | `/api/v1/tgm/who-bought-sold` | 0.01 | generated | 3 | True |
| 43 | POST | `/api/v1/token-screener` | 0.01 | generated | 1 | True |
| 44 | POST | `/api/v1/transaction-with-token-transfer-lookup` | 0.01 | generated | 2 | True |
| 45 | POST | `/api/v1beta1/profiler/address/historical-token-balances` | 0.05 | generated | 3 | True |
| 46 | POST | `/api/v1beta1/profiler/address/historical-transactions` | 0.05 | generated | 3 | True |
| 47 | POST | `/api/v1beta1/profiler/historical-transaction-lookup` | 0.05 | generated | 3 | True |
| 48 | POST | `/api/v1beta1/smart-money/historical-token-balances` | 0.25 | generated | 1 | True |
| 49 | POST | `/api/v1beta1/tgm/historical-pnl-leaderboard` | 0.25 | generated | 3 | True |
| 50 | POST | `/api/v1beta1/tgm/historical-token-flow-summary` | 0.05 | generated | 3 | True |
| 51 | POST | `/api/v1beta1/tgm/historical-token-ohlcv` | 0.05 | none | 0 | False |
| 52 | POST | `/api/v1beta1/tgm/historical-token-quant-scores` | 0.25 | generated | 3 | True |
| 53 | POST | `/api/v1beta1/tgm/historical-top-holders` | 0.25 | generated | 3 | True |
| 54 | POST | `/api/v1beta1/tgm/historical-who-bought-sold` | 0.05 | generated | 3 | True |

## Endpoints

### 1. POST `/api/v1/agent/fast`

- **Label:** Interact with the Nansen Research Agent in "fast" mode
- **Price (USD):** 2.00
- **Matched:** True (path)
- **Doc heading:** Interact with the Nansen Research Agent in "fast" mode
- **body_source:** generated
- **Required fields:** `text`
- **Notes:** no doc example; generated from schema 'AgentResearchRequest'; request_schema=AgentResearchRequest
- **Fields:**
  - `text` (string, required): Research query or question for the Nansen AI agent.
  - `conversation_id` (anyOf, optional): Optional conversation ID for multi-turn interactions. Returned in the finish event of a previous response. Omit to start…
- **Example body:**

```json
{
  "text": ""
}
```

### 2. POST `/api/v1/chains/chain-rank`

- **Label:** Get chain growth rankings
- **Price (USD):** 0.01
- **Matched:** False (none)
- **body_source:** none
- **Required fields:** _(none)_
- **Notes:** no matching doc section in llms-full.txt
- **Example body:**

```json
null
```

### 3. POST `/api/v1/nansen-score/top-tokens`

- **Label:** Get Nansen Score Top Tokens
- **Price (USD):** 0.01
- **Matched:** False (none)
- **body_source:** none
- **Required fields:** _(none)_
- **Notes:** no matching doc section in llms-full.txt
- **Example body:**

```json
null
```

### 4. POST `/api/v1/perp-leaderboard`

- **Label:** Get Perpetual Trading Leaderboard Data
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get Perpetual Trading Leaderboard Data
- **body_source:** generated
- **Required fields:** `date`
- **Notes:** no doc example; generated from schema 'PerpLeaderboardRequest'; request_schema=PerpLeaderboardRequest
- **Fields:**
  - `date` (object, required): Date range object with optional from and to fields in YYYY-MM-DD format
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Additional filters to apply to the query.
  - `premium_labels` (anyOf, optional): Controls label tier in the response. When null/omitted or false (the default), returns free-tier labels at the standard …
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering
- **Example body:**

```json
{
  "date": {}
}
```

### 5. POST `/api/v1/perp-screener`

- **Label:** Get Perpetual Contract Screening Data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Perpetual Contract Screening Data
- **body_source:** generated
- **Required fields:** `date`
- **Notes:** no doc example; generated from schema 'PerpScreenerRequest'; request_schema=PerpScreenerRequest
- **Fields:**
  - `date` (object, required): Date range for the perp screener
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Additional filters to apply
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "date": {}
}
```

### 6. POST `/api/v1/prediction-market/address-summary`

- **Label:** Get Prediction Market Address Summary
- **Price (USD):** 0.01
- **Matched:** False (none)
- **body_source:** none
- **Required fields:** _(none)_
- **Notes:** no matching doc section in llms-full.txt
- **Example body:**

```json
null
```

### 7. POST `/api/v1/prediction-market/categories`

- **Label:** Get Prediction Market Categories
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Prediction Market Categories
- **body_source:** generated
- **Required fields:** _(none)_
- **Notes:** no doc example; generated from schema 'CategoriesRequest'; request_schema=CategoriesRequest
- **Fields:**
  - `pagination` (object, optional): 
- **Example body:**

```json
{}
```

### 8. POST `/api/v1/prediction-market/event-screener`

- **Label:** Get Prediction Market Event Screener
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Prediction Market Event Screener
- **body_source:** generated
- **Required fields:** _(none)_
- **Notes:** no doc example; generated from schema 'EventScreenerRequest'; request_schema=EventScreenerRequest
- **Fields:**
  - `order_by` (anyOf, optional): Sort order
  - `sort_by` (string(enum), optional): Deprecated: use 'order_by' instead.
  - `query` (string, optional): Search query to filter results
  - `status` (string(enum), optional): Filter by status (active, closed, or empty for all)
  - `tags` (array, optional): Filter by tags
  - `min_liquidity` (number, optional): Minimum liquidity filter (-1 = no filter)
  - `max_liquidity` (number, optional): Maximum liquidity filter (-1 = no limit)
  - `max_unique_traders_24h` (integer, optional): Maximum unique traders in 24h (-1 = no limit)
  - `min_volume_24hr` (number, optional): Minimum 24h volume filter (-1 = no filter)
  - `neg_risk` (anyOf, optional): Filter by neg-risk framework (null = no filter)
  - `min_open_interest` (number, optional): Minimum open interest filter (-1 = no filter)
  - `max_open_interest` (number, optional): Maximum open interest filter (-1 = no limit)
  - `end_date_before` (string, optional): Filter markets ending before this datetime (ISO 8601)
  - `end_date_after` (string, optional): Filter markets ending after this datetime (ISO 8601)
  - `pagination` (object, optional): 
- **Example body:**

```json
{}
```

### 9. POST `/api/v1/prediction-market/market-screener`

- **Label:** Get Prediction Market Screener
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Prediction Market Screener
- **body_source:** generated
- **Required fields:** _(none)_
- **Notes:** no doc example; generated from schema 'MarketScreenerRequest'; request_schema=MarketScreenerRequest
- **Fields:**
  - `order_by` (anyOf, optional): Sort order
  - `sort_by` (string(enum), optional): Deprecated: use 'order_by' instead.
  - `query` (string, optional): Search query to filter results
  - `status` (string(enum), optional): Filter by status (active, closed, or empty for all)
  - `tags` (array, optional): Filter by tags
  - `min_liquidity` (number, optional): Minimum liquidity filter (-1 = no filter)
  - `max_liquidity` (number, optional): Maximum liquidity filter (-1 = no limit)
  - `max_unique_traders_24h` (integer, optional): Maximum unique traders in 24h (-1 = no limit)
  - `min_volume_24hr` (number, optional): Minimum 24h volume filter (-1 = no filter)
  - `neg_risk` (anyOf, optional): Filter by neg-risk framework (null = no filter)
  - `min_open_interest` (number, optional): Minimum open interest filter (-1 = no filter)
  - `max_open_interest` (number, optional): Maximum open interest filter (-1 = no limit)
  - `end_date_before` (string, optional): Filter markets ending before this datetime (ISO 8601)
  - `end_date_after` (string, optional): Filter markets ending after this datetime (ISO 8601)
  - `pagination` (object, optional): 
  - `min_price` (number, optional): Minimum price filter (-1 = no filter)
  - `max_price` (number, optional): Maximum price filter (-1 = no limit)
- **Example body:**

```json
{}
```

### 10. POST `/api/v1/prediction-market/ohlcv`

- **Label:** Get Prediction Market OHLCV Candles
- **Price (USD):** 0.01
- **Matched:** False (none)
- **body_source:** none
- **Required fields:** _(none)_
- **Notes:** no matching doc section in llms-full.txt
- **Example body:**

```json
null
```

### 11. POST `/api/v1/prediction-market/orderbook`

- **Label:** Get Prediction Market Orderbook
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Prediction Market Orderbook
- **body_source:** generated
- **Required fields:** `market_id`
- **Notes:** no doc example; generated from schema 'OrderbookRequest'; request_schema=OrderbookRequest
- **Fields:**
  - `market_id` (string, required): Polymarket market ID
  - `pagination` (object, optional): 
- **Example body:**

```json
{
  "market_id": ""
}
```

### 12. POST `/api/v1/prediction-market/pnl-by-market`

- **Label:** Get Prediction Market PnL by Market
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Endpoint Credit Cost
- **body_source:** none
- **Required fields:** _(none)_
- **Notes:** no openapi json block in section
- **Example body:**

```json
null
```

### 13. POST `/api/v1/prediction-market/position-detail`

- **Label:** Get Prediction Market Position Detail
- **Price (USD):** 0.05
- **Matched:** False (none)
- **body_source:** none
- **Required fields:** _(none)_
- **Notes:** no matching doc section in llms-full.txt
- **Example body:**

```json
null
```

### 14. POST `/api/v1/prediction-market/top-holders`

- **Label:** Get Prediction Market Top Holders
- **Price (USD):** 0.05
- **Matched:** False (none)
- **body_source:** none
- **Required fields:** _(none)_
- **Notes:** no matching doc section in llms-full.txt
- **Example body:**

```json
null
```

### 15. POST `/api/v1/prediction-market/trades-by-market`

- **Label:** Get Prediction Market Trades by Market
- **Price (USD):** 0.01
- **Matched:** False (none)
- **body_source:** none
- **Required fields:** _(none)_
- **Notes:** no matching doc section in llms-full.txt
- **Example body:**

```json
null
```

### 16. POST `/api/v1/profiler/address/counterparties`

- **Label:** Get Address Counterparties Data
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get Address Counterparties Data
- **body_source:** generated
- **Required fields:** `chain`, `date`
- **Notes:** no doc example; generated from schema 'ProfilerAddressCounterpartiesRequest'; request_schema=ProfilerAddressCounterpartiesRequest
- **Fields:**
  - `address` (anyOf, optional): Address to get counterparties for
  - `entity_name` (anyOf, optional): Entity name to get counterparties for
  - `chain` (string(enum), required): Blockchain chain for the counterparties data
  - `date` (object, required): Date range for the counterparties data. Note: High-volume addresses (e.g., WETH on Base) are limited to 180 days.
  - `source_input` (string(enum), optional): Type of interactions to include
  - `group_by` (string(enum), optional): Group counterparties by wallet or entity
  - `filters` (anyOf, optional): Additional filters to apply. Only filters for columns that are being selected will be applied.
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "chain": "all",
  "date": {}
}
```

### 17. POST `/api/v1/profiler/address/current-balance`

- **Label:** Get Address Current Balance Data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Address Current Balance Data
- **body_source:** generated
- **Required fields:** `chain`
- **Notes:** no doc example; generated from schema 'ProfilerAddressBalancesRequest'; request_schema=ProfilerAddressBalancesRequest
- **Fields:**
  - `address` (anyOf, optional): Address to get balances for
  - `entity_name` (anyOf, optional): Entity name to get balances for
  - `chain` (string(enum), required): Blockchain chain for the balances
  - `hide_spam_token` (boolean, optional): Removes suspicious tokens from the balance list
  - `filters` (anyOf, optional): Additional filters to apply. Only filters for columns that are being selected will be applied.
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering
- **Example body:**

```json
{
  "chain": "all"
}
```

### 18. POST `/api/v1/profiler/address/historical-balances`

- **Label:** Get Address Historical Balances Data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Address Historical Balances Data
- **body_source:** generated
- **Required fields:** `chain`, `date`
- **Notes:** no doc example; generated from schema 'ProfilerAddressHistoricalBalancesRequest'; request_schema=ProfilerAddressHistoricalBalancesRequest
- **Fields:**
  - `address` (anyOf, optional): Address to get historical balances for
  - `entity_name` (anyOf, optional): Entity name to get historical balances for
  - `chain` (string(enum), required): Blockchain chain for the historical balances
  - `date` (object, required): Date range for historical data
  - `filters` (anyOf, optional): Additional filters to apply. Only filters for columns that are being selected will be applied.
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering
- **Example body:**

```json
{
  "chain": "all",
  "date": {}
}
```

### 19. POST `/api/v1/profiler/address/pnl`

- **Label:** Retrieve address PnL data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Address PnL Summary Data
- **body_source:** generated
- **Required fields:** `chain`, `date`
- **Notes:** no doc example; generated from schema 'ProfilerAddressPnlSummaryRequest'; request_schema=ProfilerAddressPnlSummaryRequest
- **Fields:**
  - `address` (anyOf, optional): Address to get PnL summary for
  - `entity_name` (anyOf, optional): Entity name to get PnL summary for
  - `chain` (string(enum), required): Blockchain chain for the PnL data
  - `date` (object, required): Date range for the PnL data
- **Example body:**

```json
{
  "chain": "all",
  "date": {}
}
```

### 20. POST `/api/v1/profiler/address/pnl-summary`

- **Label:** Get Address PnL Summary Data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Address PnL Summary Data
- **body_source:** generated
- **Required fields:** `chain`, `date`
- **Notes:** no doc example; generated from schema 'ProfilerAddressPnlSummaryRequest'; request_schema=ProfilerAddressPnlSummaryRequest
- **Fields:**
  - `address` (anyOf, optional): Address to get PnL summary for
  - `entity_name` (anyOf, optional): Entity name to get PnL summary for
  - `chain` (string(enum), required): Blockchain chain for the PnL data
  - `date` (object, required): Date range for the PnL data
- **Example body:**

```json
{
  "chain": "all",
  "date": {}
}
```

### 21. POST `/api/v1/profiler/address/related-wallets`

- **Label:** Get Address Related Wallets Data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Address Related Wallets Data
- **body_source:** generated
- **Required fields:** `address`, `chain`
- **Notes:** no doc example; generated from schema 'ProfilerAddressRelatedWalletsRequest'; request_schema=ProfilerAddressRelatedWalletsRequest
- **Fields:**
  - `address` (string, required): Address to get related wallets for
  - `chain` (string(enum), required): Blockchain chain for the related wallets data
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering
- **Example body:**

```json
{
  "address": "",
  "chain": "arbitrum"
}
```

### 22. POST `/api/v1/profiler/address/transactions`

- **Label:** Get Address Transactions Data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Address Transactions Data
- **body_source:** generated
- **Required fields:** `address`, `chain`, `date`
- **Notes:** no doc example; generated from schema 'ProfilerAddressTransactionsRequest'; request_schema=ProfilerAddressTransactionsRequest
- **Fields:**
  - `address` (string, required): Address to get transactions for
  - `chain` (string(enum), required): Blockchain chain for the transactions
  - `date` (object, required): Date range for the transactions
  - `hide_spam_token` (boolean, optional): Removes suspicious tokens from the transaction list
  - `filters` (anyOf, optional): Additional filters to apply. Only filters for columns that are being selected will be applied.
  - `pagination` (object, optional): Pagination parameters (max 100 records per page for performance)
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering
- **Example body:**

```json
{
  "address": "",
  "chain": "all",
  "date": {}
}
```

### 23. POST `/api/v1/profiler/dex-trades`

- **Label:** Get Wallet DEX Trades
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Wallet DEX Trades
- **body_source:** generated
- **Required fields:** `address`, `chain`, `date`
- **Notes:** no doc example; generated from schema 'ProfilerDexTradeRequest'; request_schema=ProfilerDexTradeRequest
- **Fields:**
  - `address` (string, required): Trader address
  - `chain` (string(enum), required): Chain to query
  - `date` (object, required): Date range for the trades
  - `filters` (anyOf, optional): Additional filters for the trades
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Sort order for the trades
- **Example body:**

```json
{
  "address": "",
  "chain": "arbitrum",
  "date": {}
}
```

### 24. POST `/api/v1/profiler/perp-positions`

- **Label:** Get Perpetual Positions Data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Perpetual Positions Data
- **body_source:** generated
- **Required fields:** `address`
- **Notes:** no doc example; generated from schema 'PerpPositionsRequest'; request_schema=PerpPositionsRequest
- **Fields:**
  - `address` (string, required): User's Hyperliquid address in 42-character hexadecimal format
  - `filters` (anyOf, optional): Additional filters to apply to the query.
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "address": ""
}
```

### 25. POST `/api/v1/profiler/perp-trades`

- **Label:** Get Perpetual Trade Data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Perpetual Trade Data
- **body_source:** generated
- **Required fields:** `address`, `date`
- **Notes:** no doc example; generated from schema 'PerpTradeRequest'; request_schema=PerpTradeRequest
- **Fields:**
  - `address` (string, required): User's Hyperliquid address in 42-character hexadecimal format
  - `date` (object, required): Date range for the trades (ISO 8601 date-time)
  - `filters` (anyOf, optional): Additional filters for the trades
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Sort order for the trades
- **Example body:**

```json
{
  "address": "",
  "date": {}
}
```

### 26. POST `/api/v1/smart-money/dcas`

- **Label:** Get Smart Money DCAs Data
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get Smart Money DCAs Data
- **body_source:** generated
- **Required fields:** _(none)_
- **Notes:** no doc example; generated from schema 'SmartMoneyDcasRequest'; request_schema=SmartMoneyDcasRequest
- **Fields:**
  - `filters` (anyOf, optional): Additional filters to apply. Only filters for columns that are being selected will be applied.
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{}
```

### 27. POST `/api/v1/smart-money/dex-trades`

- **Label:** Get Smart Money DEX Trades Data
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get Smart Money DEX Trades Data
- **body_source:** generated
- **Required fields:** `chains`
- **Notes:** no doc example; generated from schema 'SmartMoneyDexTradesRequest'; request_schema=SmartMoneyDexTradesRequest
- **Fields:**
  - `chains` (array, required): Chains to include in the analysis (only smart money supported chains). Use 'all' to include all available chains.
  - `filters` (anyOf, optional): Additional filters to apply. Only filters for columns that are being selected will be applied.
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "chains": [
    "all"
  ]
}
```

### 28. POST `/api/v1/smart-money/holdings`

- **Label:** Get Smart Money Holdings Data
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get Smart Money Holdings Data
- **body_source:** generated
- **Required fields:** `chains`
- **Notes:** no doc example; generated from schema 'SmartMoneyHoldingsRequest'; request_schema=SmartMoneyHoldingsRequest
- **Fields:**
  - `chains` (array, required): Chains to include in the analysis (only smart money supported chains). Use 'all' to include all available chains.
  - `filters` (anyOf, optional): Additional filters to apply. Only filters for columns that are being selected will be applied.
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "chains": [
    "all"
  ]
}
```

### 29. POST `/api/v1/smart-money/netflow`

- **Label:** Get Smart Money Netflow Data
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get Smart Money Netflow Data
- **body_source:** generated
- **Required fields:** `chains`
- **Notes:** no doc example; generated from schema 'SmartMoneyNetflowRequest'; request_schema=SmartMoneyNetflowRequest
- **Fields:**
  - `chains` (array, required): Chains to include in the analysis (only smart money supported chains). Use 'all' to include all available chains.
  - `filters` (anyOf, optional): Additional filters to apply. Only filters for columns that are being selected will be applied.
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "chains": [
    "all"
  ]
}
```

### 30. POST `/api/v1/smart-money/perp-trades`

- **Label:** Get Smart Money Perpetual Trades Data
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get Smart Money Perpetual Trades Data
- **body_source:** generated
- **Required fields:** _(none)_
- **Notes:** no doc example; generated from schema 'SmartMoneyPerpTradesRequest'; request_schema=SmartMoneyPerpTradesRequest
- **Fields:**
  - `filters` (anyOf, optional): Additional filters to apply. Only filters for columns that are being selected will be applied.
  - `only_new_positions` (anyOf, optional): When True, includes 'Open' position actions (Open Long, Open Short). Can be combined with other action filters using OR …
  - `pagination` (object, optional): Pagination parameters
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{}
```

### 31. POST `/api/v1/smart-money/pnl-leaderboard`

- **Label:** Get Smart Money PnL Leaderboard
- **Price (USD):** 0.05
- **Matched:** False (none)
- **body_source:** none
- **Required fields:** _(none)_
- **Notes:** no matching doc section in llms-full.txt
- **Example body:**

```json
null
```

### 32. POST `/api/v1/tgm/dex-trades`

- **Label:** Get "Token God Mode" (TGM) DEX trades data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get "Token God Mode" (TGM) DEX trades data
- **body_source:** generated
- **Required fields:** `chain`, `token_address`, `date`
- **Notes:** no doc example; generated from schema 'TGMDexTradesRequest'; request_schema=TGMDexTradesRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain
  - `token_address` (string, required): Token address
  - `only_smart_money` (boolean, optional): Returns only the DEX Trades made by Smart Money wallets
  - `date` (object, required): ISO 8601 date-time range object with optional from and to fields
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Additional filters to apply to the query.
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "chain": "arbitrum",
  "token_address": "",
  "date": {}
}
```

### 33. POST `/api/v1/tgm/flow-intelligence`

- **Label:** Get "Token God Mode" (TGM) flow intelligence data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get "Token God Mode" (TGM) flow intelligence data
- **body_source:** generated
- **Required fields:** `chain`, `token_address`
- **Notes:** no doc example; generated from schema 'TGMFlowIntelligenceRequest'; request_schema=TGMFlowIntelligenceRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain
  - `token_address` (string, required): Token address
  - `timeframe` (string(enum), optional): Time window for the flow intelligence data
  - `filters` (anyOf, optional): Additional filters to apply to the query.
- **Example body:**

```json
{
  "chain": "arbitrum",
  "token_address": ""
}
```

### 34. POST `/api/v1/tgm/flows`

- **Label:** Get "Token God Mode" (TGM) flows data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get "Token God Mode" (TGM) flows data
- **body_source:** generated
- **Required fields:** `chain`, `token_address`, `date`
- **Notes:** no doc example; generated from schema 'TGMFlowsRequest'; request_schema=TGMFlowsRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain
  - `token_address` (string, required): Token address
  - `date` (object, required): ISO 8601 date-time range object with optional from and to fields
  - `label` (string(enum), optional): Label type for filtering flows
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Additional filters to apply to the query.
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "chain": "arbitrum",
  "token_address": "",
  "date": {}
}
```

### 35. POST `/api/v1/tgm/holders`

- **Label:** Get "Token God Mode" (TGM) holders data
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get "Token God Mode" (TGM) holders data
- **body_source:** generated
- **Required fields:** `chain`, `token_address`
- **Notes:** no doc example; generated from schema 'TGMHoldersRequest'; request_schema=TGMHoldersRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain
  - `token_address` (string, required): Token address
  - `aggregate_by_entity` (boolean, optional): Whether to return entity data
  - `label_type` (string(enum), optional): Label type. You must also include the labels filter to match the label type. For example, for label type 'smart_money', …
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Additional filters to apply to the query.
  - `premium_labels` (anyOf, optional): Controls label tier in the response. When null/omitted or false (the default), returns free-tier labels at the standard …
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "chain": "arbitrum",
  "token_address": ""
}
```

### 36. POST `/api/v1/tgm/jup-dca`

- **Label:** Get "Token God Mode" (TGM) Jupiter DCA data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get "Token God Mode" (TGM) Jupiter DCA data
- **body_source:** generated
- **Required fields:** `token_address`
- **Notes:** no doc example; generated from schema 'TGMJupDcaRequest'; request_schema=TGMJupDcaRequest
- **Fields:**
  - `token_address` (string, required): Token address on Solana
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Additional filters to apply to the query.
- **Example body:**

```json
{
  "token_address": ""
}
```

### 37. POST `/api/v1/tgm/pnl-leaderboard`

- **Label:** Get "Token God Mode" (TGM) PnL leaderboard data
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get "Token God Mode" (TGM) PnL leaderboard data
- **body_source:** generated
- **Required fields:** `chain`, `token_address`, `date`
- **Notes:** no doc example; generated from schema 'TGMPnlLeaderboardRequest'; request_schema=TGMPnlLeaderboardRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain
  - `token_address` (string, required): Token address
  - `date` (object, required): ISO 8601 date-time range object with optional from and to fields
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Additional filters to apply to the query.
  - `premium_labels` (anyOf, optional): Controls label tier in the response. When null/omitted or false (the default), returns free-tier labels at the standard …
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering
- **Example body:**

```json
{
  "chain": "arbitrum",
  "token_address": "",
  "date": {}
}
```

### 38. POST `/api/v1/tgm/position-intelligence`

- **Label:** Get "Token God Mode" (TGM) position intelligence data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get "Token God Mode" (TGM) position intelligence data
- **body_source:** generated
- **Required fields:** `token_address`
- **Notes:** no doc example; generated from schema 'TGMPositionIntelligenceRequest'; request_schema=TGMPositionIntelligenceRequest
- **Fields:**
  - `token_address` (string, required): Token address (for perps and hyperliquid, validation is skipped)
- **Example body:**

```json
{
  "token_address": ""
}
```

### 39. POST `/api/v1/tgm/token-information`

- **Label:** Get "Token God Mode" (TGM) token information data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get "Token God Mode" (TGM) token information data
- **body_source:** generated
- **Required fields:** `chain`, `token_address`, `timeframe`
- **Notes:** no doc example; generated from schema 'TGMTokenInformationRequest'; request_schema=TGMTokenInformationRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain
  - `token_address` (string, required): Token address
  - `timeframe` (string(enum), required): Timeframe for the token information query
- **Example body:**

```json
{
  "chain": "arbitrum",
  "token_address": "",
  "timeframe": "5m"
}
```

### 40. POST `/api/v1/tgm/token-ohlcv`

- **Label:** Retrieve token OHLCV candle data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Retrieve token OHLCV candle data
- **body_source:** generated
- **Required fields:** `chain`, `timeframe`
- **Notes:** no doc example; generated from schema 'TokenOHLCVRequest'; request_schema=TokenOHLCVRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain
  - `token_address` (anyOf, optional): Token contract address
  - `token_addresses` (anyOf, optional): Array of token contract addresses for batch queries (max 10, or max 5 for Hyperliquid, mutually exclusive with token_add…
  - `date_range` (anyOf, optional): DEPRECATED: Use 'date' instead. Date range with start/end fields.
  - `date` (anyOf, optional): Date range for the data (defaults to last 30 days if not specified)
  - `timeframe` (string(enum), required): Time resolution for OHLCV data
- **Example body:**

```json
{
  "chain": "algorand",
  "timeframe": "1m"
}
```

### 41. POST `/api/v1/tgm/transfers`

- **Label:** Get "Token God Mode" (TGM) transfers data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get "Token God Mode" (TGM) transfers data
- **body_source:** generated
- **Required fields:** `chain`, `token_address`, `date`
- **Notes:** no doc example; generated from schema 'TGMTransfersRequest'; request_schema=TGMTransfersRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain
  - `token_address` (string, required): Token address
  - `date` (object, required): ISO 8601 date-time range object with from and to fields (max 1 year).
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Additional filters to apply to the query.
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "chain": "arbitrum",
  "token_address": "",
  "date": {}
}
```

### 42. POST `/api/v1/tgm/who-bought-sold`

- **Label:** Get "Token God Mode" (TGM) who bought/sold data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get "Token God Mode" (TGM) who bought/sold data
- **body_source:** generated
- **Required fields:** `chain`, `token_address`, `date`
- **Notes:** no doc example; generated from schema 'TGMWhoBoughtSoldRequest'; request_schema=TGMWhoBoughtSoldRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain
  - `token_address` (string, required): Address of token
  - `buy_or_sell` (string(enum), optional): Are we checking buys or sells
  - `date` (object, required): ISO 8601 date-time range object with from and to fields
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Additional filters to apply to the query.
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "chain": "arbitrum",
  "token_address": "",
  "date": {}
}
```

### 43. POST `/api/v1/token-screener`

- **Label:** Retrieve token screener data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Retrieve token screener data
- **body_source:** generated
- **Required fields:** `chains`
- **Notes:** no doc example; generated from schema 'TokenScreenerRequest'; request_schema=TokenScreenerRequest
- **Fields:**
  - `chains` (array, required): List of blockchain chains to filter by
  - `timeframe` (anyOf, optional): **Required** (unless using deprecated 'date' parameter).
  - `date` (anyOf, optional): **DEPRECATED**: Use 'timeframe' instead for better reliability and performance.
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Additional filters to apply
  - `order_by` (anyOf, optional): Custom sort order to override the endpoint's default ordering.
- **Example body:**

```json
{
  "chains": [
    "arbitrum"
  ]
}
```

### 44. POST `/api/v1/transaction-with-token-transfer-lookup`

- **Label:** Get Transaction with Token Transfer Lookup Data
- **Price (USD):** 0.01
- **Matched:** True (path)
- **Doc heading:** Get Transaction with Token Transfer Lookup Data
- **body_source:** generated
- **Required fields:** `chain`, `transaction_hash`
- **Notes:** no doc example; generated from schema 'TransactionLookupRequest'; request_schema=TransactionLookupRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain for the transaction lookup
  - `transaction_hash` (string, required): Transaction hash to lookup
  - `block_timestamp` (anyOf, optional): Timestamp of the transaction block (format: 'YYYY-MM-DD HH:MM:SS'). Optional for most EVM chains — resolved automaticall…
- **Example body:**

```json
{
  "chain": "all",
  "transaction_hash": ""
}
```

### 45. POST `/api/v1beta1/profiler/address/historical-token-balances`

- **Label:** Get Historical Balances by Address (Beta)
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get Historical Balances by Address (Beta)
- **body_source:** generated
- **Required fields:** `address`, `as_of_date`, `chain`
- **Notes:** no doc example; generated from schema 'ProfilerHistoricalTokenBalancesRequest'; request_schema=ProfilerHistoricalTokenBalancesRequest
- **Fields:**
  - `address` (string, required): Wallet address (EVM hex or Solana base58)
  - `as_of_date` (string, required): Historical snapshot date — balances are computed up to this date
  - `chain` (string(enum), required): Chain filter
  - `apply_blacklist_filter` (boolean, optional): When True, exclude blacklisted addresses from the results. Defaults to True.
  - `pagination` (object, optional): Pagination parameters
- **Example body:**

```json
{
  "address": "",
  "as_of_date": "",
  "chain": "all"
}
```

### 46. POST `/api/v1beta1/profiler/address/historical-transactions`

- **Label:** Get Historical Transactions for an Address (Beta)
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get Historical Transactions for an Address (Beta)
- **body_source:** generated
- **Required fields:** `address`, `chain`, `as_of_date`
- **Notes:** no doc example; generated from schema 'ProfilerAddressHistoricalTransactionsRequest'; request_schema=ProfilerAddressHistoricalTransactionsRequest
- **Fields:**
  - `address` (string, required): Wallet address (EVM hex or Solana base58)
  - `chain` (string(enum), required): Blockchain chain
  - `as_of_date` (string, required): Historical snapshot date — only transactions on or before this date are returned, with labels resolved as of this date.
  - `hide_spam_token` (boolean, optional): Filter out tokens flagged as spam by Nansen
  - `pagination` (object, optional): Pagination parameters. The endpoint returns at most 20 rows, so pagination beyond that yields empty results.
  - `apply_blacklist_filter` (boolean, optional): When True, exclude blacklisted addresses from the results. Defaults to True.
- **Example body:**

```json
{
  "address": "",
  "chain": "all",
  "as_of_date": ""
}
```

### 47. POST `/api/v1beta1/profiler/historical-transaction-lookup`

- **Label:** Get Historical (Time-Travel) Transaction Lookup Data (Beta)
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get Historical (Time-Travel) Transaction Lookup Data (Beta)
- **body_source:** generated
- **Required fields:** `chain`, `transaction_hash`, `as_of_date`
- **Notes:** no doc example; generated from schema 'ProfilerHistoricalTransactionLookupRequest'; request_schema=ProfilerHistoricalTransactionLookupRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain for the historical transaction lookup
  - `transaction_hash` (string, required): Transaction hash to lookup (0x-prefixed, 66 chars)
  - `as_of_date` (string, required): Reference date for temporal label resolution and as-of-date pricing. Must be on/after the transaction's block_timestamp.…
  - `block_timestamp` (anyOf, optional): Optional block timestamp in 'YYYY-MM-DD HH:MM:SS' format. When provided, skips the slow (60-170s) hash-to-timestamp reso…
  - `apply_blacklist_filter` (boolean, optional): When True, exclude blacklisted addresses from the results. Defaults to True.
- **Example body:**

```json
{
  "chain": "base",
  "transaction_hash": "",
  "as_of_date": ""
}
```

### 48. POST `/api/v1beta1/smart-money/historical-token-balances`

- **Label:** Get Historical SM Token Balances (Beta)
- **Price (USD):** 0.25
- **Matched:** True (path)
- **Doc heading:** Get Historical SM Token Balances (Beta)
- **body_source:** generated
- **Required fields:** `as_of_date`
- **Notes:** no doc example; generated from schema 'SmartMoneyHistoricalTokenBalancesRequest'; request_schema=SmartMoneyHistoricalTokenBalancesRequest
- **Fields:**
  - `as_of_date` (string, required): Date to query balances for
  - `chains` (array, optional): Chains to include. Empty list returns all chains.
  - `filters` (anyOf, optional): Optional filters for SM labels and token types
  - `apply_blacklist_filter` (boolean, optional): When True, exclude blacklisted addresses from the results. Defaults to True.
  - `pagination` (object, optional): Pagination parameters
- **Example body:**

```json
{
  "as_of_date": ""
}
```

### 49. POST `/api/v1beta1/tgm/historical-pnl-leaderboard`

- **Label:** Get historical "Token God Mode" (TGM) PnL leaderboard (Beta)
- **Price (USD):** 0.25
- **Matched:** True (path)
- **Doc heading:** Get historical "Token God Mode" (TGM) PnL leaderboard (Beta)
- **body_source:** generated
- **Required fields:** `chain`, `token_address`, `date_range`
- **Notes:** no doc example; generated from schema 'TGMHistoricalPnlLeaderboardRequest'; request_schema=TGMHistoricalPnlLeaderboardRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain. Currently base, bnb, ethereum, solana.
  - `token_address` (string, required): Token contract address
  - `date_range` (object, required): Historical date range. Dates are truncated to YYYY-MM-DD server-side.
  - `pagination` (object, optional): Pagination parameters.
  - `filters` (anyOf, optional): Optional filters applied server-side
  - `order_by` (anyOf, optional): Sort order. Defaults to pnl_usd_total DESC. Only the first element is used.
  - `apply_blacklist_filter` (boolean, optional): When True, exclude blacklisted addresses from the results. Defaults to True.
- **Example body:**

```json
{
  "chain": "base",
  "token_address": "",
  "date_range": {}
}
```

### 50. POST `/api/v1beta1/tgm/historical-token-flow-summary`

- **Label:** Get historical "Token God Mode" (TGM) token flow summary (Beta)
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get historical "Token God Mode" (TGM) token flow summary (Beta)
- **body_source:** generated
- **Required fields:** `chain`, `token_address`, `date_range`
- **Notes:** no doc example; generated from schema 'TGMHistoricalTokenFlowSummaryRequest'; request_schema=TGMHistoricalTokenFlowSummaryRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain. Currently base, bnb, ethereum, solana.
  - `token_address` (string, required): Token contract address
  - `date_range` (object, required): Historical date range with explicit from and to dates. date_to is the as-of date for label resolution; the (date_from, d…
  - `apply_blacklist_filter` (boolean, optional): When True, exclude blacklisted addresses from the results. Defaults to True.
- **Example body:**

```json
{
  "chain": "base",
  "token_address": "",
  "date_range": {}
}
```

### 51. POST `/api/v1beta1/tgm/historical-token-ohlcv`

- **Label:** Get historical "Token God Mode" (TGM) token OHLCV (Beta)
- **Price (USD):** 0.05
- **Matched:** False (none)
- **body_source:** none
- **Required fields:** _(none)_
- **Notes:** no matching doc section in llms-full.txt
- **Example body:**

```json
null
```

### 52. POST `/api/v1beta1/tgm/historical-token-quant-scores`

- **Label:** Get Historical Token Quant Scores (Beta)
- **Price (USD):** 0.25
- **Matched:** True (path)
- **Doc heading:** Get Historical Token Quant Scores (Beta)
- **body_source:** generated
- **Required fields:** `as_of_date`, `chain`, `token_address`
- **Notes:** no doc example; generated from schema 'TgmHistoricalTokenQuantScoresRequest'; request_schema=TgmHistoricalTokenQuantScoresRequest
- **Fields:**
  - `as_of_date` (string, required): Date to query indicators for
  - `chain` (string(enum), required): Blockchain chain
  - `token_address` (string, required): Token contract address
- **Example body:**

```json
{
  "as_of_date": "",
  "chain": "arbitrum",
  "token_address": ""
}
```

### 53. POST `/api/v1beta1/tgm/historical-top-holders`

- **Label:** Get historical "Token God Mode" (TGM) top holders (Beta)
- **Price (USD):** 0.25
- **Matched:** True (path)
- **Doc heading:** Get historical "Token God Mode" (TGM) top holders (Beta)
- **body_source:** generated
- **Required fields:** `chain`, `token_address`, `as_of_date`
- **Notes:** no doc example; generated from schema 'TGMHistoricalTopHoldersRequest'; request_schema=TGMHistoricalTopHoldersRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain. Currently base, bnb, ethereum, solana.
  - `token_address` (string, required): Token contract address
  - `as_of_date` (string, required): Historical date (YYYY-MM-DD) to compute holder balances at.
  - `label_type` (string(enum), optional): Holder filter bucket. 'all_holders' returns everyone; the others restrict to a specific label class.
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Optional filters applied server-side
  - `order_by` (anyOf, optional): Sort order. Defaults to token_amount DESC. Only the first element is used.
  - `apply_blacklist_filter` (boolean, optional): When True, exclude blacklisted addresses from the results. Defaults to True.
- **Example body:**

```json
{
  "chain": "base",
  "token_address": "",
  "as_of_date": ""
}
```

### 54. POST `/api/v1beta1/tgm/historical-who-bought-sold`

- **Label:** Get historical "Token God Mode" (TGM) who bought/sold (Beta)
- **Price (USD):** 0.05
- **Matched:** True (path)
- **Doc heading:** Get historical "Token God Mode" (TGM) who bought/sold (Beta)
- **body_source:** generated
- **Required fields:** `chain`, `token_address`, `date_range`
- **Notes:** no doc example; generated from schema 'TGMHistoricalWhoBoughtSoldRequest'; request_schema=TGMHistoricalWhoBoughtSoldRequest
- **Fields:**
  - `chain` (string(enum), required): Blockchain chain. Currently base, bnb, ethereum, solana.
  - `token_address` (string, required): Token contract address
  - `date_range` (object, required): Historical date range with explicit from and to dates
  - `buy_or_sell` (string(enum), optional): Whether to return net buyers or net sellers
  - `pagination` (object, optional): Pagination parameters
  - `filters` (anyOf, optional): Optional filters applied server-side
  - `order_by` (anyOf, optional): Sort order. Defaults to bought_volume_usd DESC. Only the first element is used.
- **Example body:**

```json
{
  "chain": "base",
  "token_address": "",
  "date_range": {}
}
```
