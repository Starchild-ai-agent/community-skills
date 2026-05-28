---
name: "@4885/opensea"
version: 1.1.0
description: OpenSea API integration for NFT and token discovery, marketplace intelligence, and order/transaction workflows.

  Use when working with OpenSea data or trading flows (e.g. collection stats, trending collections/tokens, NFT metadata, listings/offers, swap quotes, transaction receipt polling).
author: kristina
tags: [opensea, nft, marketplace, listings, offers, swaps]
metadata:
  starchild:
    emoji: "🧿"
    skillKey: opensea
    requires:
      anyBins: [python3, python]
user-invocable: true
---

## What this skill is for
Use this skill when the user asks for anything OpenSea-specific: NFT collection research, account portfolio views, listing/offer discovery, market events, token intel, or OpenSea trading workflow support.

Primary docs source:
- https://docs.opensea.io
- https://docs.opensea.io/llms.txt (index of docs + endpoint map)

## API key strategy
OpenSea supports instant free-tier key creation (documented under `Create an instant API key`).

Use this decision rule:
1. If read-only request is small/occasional: create/use instant key.
2. If user wants sustained/production usage or higher throughput: request user-provided key via secure env input.

Never ask user to paste keys in chat.

## Request pattern (Python scripts)
For any script you write for this skill:
- Use `from core.http_client import proxied_get, proxied_post`
- Add usage tracking header: `headers={"SC-CALLER-ID": "chat:<thread_id>"}` (or job/preview typed prefix when relevant)
- Read key from env if available (e.g., `OPENSEA_API_KEY`) and pass as `X-API-KEY`
- If key missing and task needs authenticated throughput, use `request_env_input`

## Endpoint families to prioritize
Use OpenSea V2 reference endpoints grouped by intent:

1. **Discovery / analytics**
- collections: stats, traits, top/trending, holders, floor history
- NFTs: metadata, owners, analytics, by collection/account/contract
- events: global/by collection/by NFT/by account
- search: cross-entity search

2. **Marketplace intelligence**
- listings: best listing by NFT/collection, all listings by collection
- offers: best offer by NFT, collection offers, trait offers
- orders: get order, cancel order

3. **Execution planning (no fabricated confirmations)**
- listing/offer fulfillment data endpoints
- sweep and cross-chain fulfillment endpoints
- swaps: quote + execute transaction payloads
- transaction receipt endpoint for verification polling

## Safety and verification
- Never claim a buy/list/swap/fulfillment is complete without receipt/status confirmation.
- Treat OpenSea as quote/action builder unless on-chain submission + receipt confirms execution.
- If endpoint output omits a hash or status, explicitly say it was not returned.

## Common workflow templates

### A) Collection research request
1. Resolve slug/collection.
2. Pull stats + floor history + traits.
3. Pull recent events.
4. Summarize liquidity, turnover, and near-term risk (washy volume, thin listings, trait concentration).

### B) “Should I sweep this collection?”
1. Fetch best listings and recent sales events.
2. Compare spread vs recent clears.
3. Evaluate depth (how many items near floor).
4. If user wants action: generate sweep transaction plan and clearly label it as pending execution until receipt confirmed.

### C) “Buy/list this NFT”
1. Pull best listing/offer + order details.
2. Generate fulfillment/listing actions.
3. Have wallet sign/broadcast via wallet tooling.
4. Poll transaction receipt endpoint and report verified state.

## Known doc anchors
- API overview: `/reference/api-overview`
- API key flow: `/reference/api-keys`
- LLM/agent discovery: `/reference/llms-agent-discovery`
- SDKs: `/reference/opensea-js`, `/reference/opensea-cli`, `/reference/stream-js`

If endpoint behavior conflicts with assumptions, trust live docs and response payloads over memory.

## Script usage

Script-mode skill — import from `skills/opensea/exports.py`.

```bash
python3 - <<'EOF'
import sys, json
sys.path.insert(0, "/data/workspace/skills/opensea")
from exports import os_collection_stats, os_search

print(json.dumps(os_collection_stats("doodles-official"), indent=2))
print(json.dumps(os_search("doodles", limit=3), indent=2))
EOF
```

### Exports available
- API key: `os_create_instant_api_key`
- Collections: `os_collections`, `os_collection`, `os_collection_stats`, `os_collection_holders`, `os_collection_floor_prices`, `os_collections_trending`, `os_collections_top`
- Search: `os_search`
- NFTs: `os_nft`, `os_nfts_by_contract`
- Events: `os_events`, `os_events_by_collection`, `os_events_by_nft`
- Listings/Offers: `os_listings_best`, `os_listings_all`, `os_offers_all`, `os_offers_for_nft`, `os_best_offer_for_nft`
- Swap/verification: `os_swap_quote`, `os_swap_execute`, `os_transaction_receipt` (`swap_quote` required by OpenSea API; include at least one of `transaction_identifiers` / `relay_request_id` / `request_id`)

### Ready scripts
- `skills/opensea/scripts/smoke_test.py`
- `skills/opensea/scripts/get_collection_report.py`
- `skills/opensea/scripts/get_nft_snapshot.py`
- `skills/opensea/scripts/get_market_surface.py`
- `skills/opensea/scripts/poll_tx_receipt.py` (expects swap_quote JSON inline or via `@file.json`)

### End-to-end execution notes
1. `os_swap_execute` returns unsigned transaction payloads (`to`, `data`, `value`) and quote metadata; it does **not** broadcast.
2. Broadcast each transaction with wallet tooling (`wallet_transfer`) using chain-appropriate chain ID.
3. `wallet_transfer` may return `user_operation_hash` without a normal tx hash. You can use that value as `transaction_identifiers[].transaction_hash` for OpenSea receipt polling.
4. For receipt verification call `os_transaction_receipt` with:
   - a `swap_quote` object containing `from_assets` (and optionally `to_assets`), and
   - at least one identifier: `transaction_identifiers` (preferred), `relay_request_id`, or `request_id`.
5. `request_id` must be a valid UUID when supplied.
6. If `swap_quote`/identifier pairing is inconsistent, the API may return validation errors like provider-mapping failures.
7. Verified working pattern (Arbitrum USDC->WETH test):
   - `swap_provider` from quote: `ZERO_EX`
   - pass two `transaction_identifiers` with chain `arbitrum`, provider `ZERO_EX`, hashes from wallet `user_operation_hash`
   - receipt returns `status: PENDING` with populated `asset_receipts`/`total_spent` while settlement completes.

## Output style
Return:
- user’s requested answer first,
- key metrics in compact bullets or table,
- explicit confidence/limits when data is partial,
- next actionable step (e.g. monitor, place order, wait for receipt).

No hype language, no fabricated execution results.