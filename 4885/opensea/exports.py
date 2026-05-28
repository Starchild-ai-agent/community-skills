"""
OpenSea skill exports — script-mode helper functions.

Usage from a bash block:
    python3 - <<'EOF'
    import sys
    sys.path.insert(0, "/data/workspace/skills/opensea")
    from exports import os_collection_stats, os_nft, os_listings_best
    print(os_collection_stats("doodles-official"))
    EOF
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from client import OpenSeaClient


_client_singleton: Optional[OpenSeaClient] = None


def _client(caller_id: str = "chat:opensea-skill") -> OpenSeaClient:
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = OpenSeaClient(caller_id=caller_id)
    return _client_singleton


# -------- API key --------

def os_create_instant_api_key(caller_id: str = "chat:opensea-skill") -> Dict[str, Any]:
    return OpenSeaClient(caller_id=caller_id).post("/api/v2/auth/keys", data={})


# -------- Collections --------

def os_collections(
    limit: int = 20,
    next_value: Optional[str] = None,
    chain: Optional[str] = None,
    creator_username: Optional[str] = None,
    include_hidden: Optional[bool] = None,
    order_by: Optional[str] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {"limit": limit}
    if next_value:
        params["next.value"] = next_value
    if chain:
        params["chain"] = chain
    if creator_username:
        params["creator_username"] = creator_username
    if include_hidden is not None:
        params["include_hidden"] = str(include_hidden).lower()
    if order_by:
        params["order_by"] = order_by
    return _client().get("/api/v2/collections", params=params)


def os_collection(slug: str) -> Dict[str, Any]:
    return _client().get(f"/api/v2/collections/{slug}")


def os_collection_stats(slug: str) -> Dict[str, Any]:
    return _client().get(f"/api/v2/collections/{slug}/stats")


def os_collection_holders(slug: str, limit: int = 50, next_value: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"limit": limit}
    if next_value:
        params["next.value"] = next_value
    return _client().get(f"/api/v2/collections/{slug}/holders", params=params)


def os_collection_floor_prices(slug: str, interval: str = "1d") -> Dict[str, Any]:
    return _client().get(f"/api/v2/collections/{slug}/floor_prices", params={"interval": interval})


def os_collections_trending(limit: int = 10, chain: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"limit": limit}
    if chain:
        params["chain"] = chain
    return _client().get("/api/v2/collections/trending", params=params)


def os_collections_top(
    limit: int = 10,
    chain: Optional[str] = None,
    order_by: str = "one_day_volume",
) -> Dict[str, Any]:
    params: Dict[str, Any] = {"limit": limit, "order_by": order_by}
    if chain:
        params["chain"] = chain
    return _client().get("/api/v2/collections/top", params=params)


# -------- Search --------

def os_search(query: str, chains: Optional[str] = None, asset_types: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    params: Dict[str, Any] = {"query": query, "limit": limit}
    if chains:
        params["chains"] = chains
    if asset_types:
        params["asset_types"] = asset_types
    return _client().get("/api/v2/search", params=params)


# -------- NFTs --------

def os_nft(chain: str, contract: str, identifier: str) -> Dict[str, Any]:
    return _client().get(f"/api/v2/chain/{chain}/contract/{contract}/nfts/{identifier}")


def os_nfts_by_contract(chain: str, contract: str, limit: int = 20, next_value: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"limit": limit}
    if next_value:
        params["next.value"] = next_value
    return _client().get(f"/api/v2/chain/{chain}/contract/{contract}/nfts", params=params)


# -------- Events --------

def os_events(after: Optional[int] = None, before: Optional[int] = None, event_type: Optional[str] = None, limit: int = 20, next_value: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"limit": limit}
    if after is not None:
        params["after"] = after
    if before is not None:
        params["before"] = before
    if event_type:
        params["event_type"] = event_type
    if next_value:
        params["next.value"] = next_value
    return _client().get("/api/v2/events", params=params)


def os_events_by_collection(slug: str, after: Optional[int] = None, before: Optional[int] = None, event_type: Optional[str] = None, traits: Optional[str] = None, limit: int = 20, next_value: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"limit": limit}
    if after is not None:
        params["after"] = after
    if before is not None:
        params["before"] = before
    if event_type:
        params["event_type"] = event_type
    if traits:
        params["traits"] = traits
    if next_value:
        params["next.value"] = next_value
    return _client().get(f"/api/v2/events/collection/{slug}", params=params)


def os_events_by_nft(chain: str, contract: str, identifier: str, after: Optional[int] = None, before: Optional[int] = None, event_type: Optional[str] = None, limit: int = 20, next_value: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"limit": limit}
    if after is not None:
        params["after"] = after
    if before is not None:
        params["before"] = before
    if event_type:
        params["event_type"] = event_type
    if next_value:
        params["next.value"] = next_value
    return _client().get(
        f"/api/v2/events/chain/{chain}/contract/{contract}/nfts/{identifier}",
        params=params,
    )


# -------- Listings / Offers --------

def os_listings_best(slug: str, include_private_listings: bool = False, traits: Optional[str] = None, limit: int = 20, next_value: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "include_private_listings": str(include_private_listings).lower(),
        "limit": limit,
    }
    if traits:
        params["traits"] = traits
    if next_value:
        params["next.value"] = next_value
    return _client().get(f"/api/v2/listings/collection/{slug}/best", params=params)


def os_listings_all(slug: str, include_private_listings: bool = False, maker: Optional[str] = None, limit: int = 20, next_value: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "include_private_listings": str(include_private_listings).lower(),
        "limit": limit,
    }
    if maker:
        params["maker"] = maker
    if next_value:
        params["next.value"] = next_value
    return _client().get(f"/api/v2/listings/collection/{slug}/all", params=params)


def os_offers_all(slug: str, maker: Optional[str] = None, limit: int = 20, next_value: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"limit": limit}
    if maker:
        params["maker"] = maker
    if next_value:
        params["next.value"] = next_value
    return _client().get(f"/api/v2/offers/collection/{slug}/all", params=params)


def os_offers_for_nft(slug: str, identifier: str, limit: int = 20, next_value: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"limit": limit}
    if next_value:
        params["next.value"] = next_value
    return _client().get(f"/api/v2/offers/collection/{slug}/nfts/{identifier}", params=params)


def os_best_offer_for_nft(slug: str, identifier: str) -> Dict[str, Any]:
    return _client().get(f"/api/v2/offers/collection/{slug}/nfts/{identifier}/best")


# -------- Swap + Receipt --------

def os_swap_quote(from_chain: str, from_address: str, to_chain: str, to_address: str, quantity: str, address: str, slippage: Optional[str] = None, recipient: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "from_chain": from_chain,
        "from_address": from_address,
        "to_chain": to_chain,
        "to_address": to_address,
        "quantity": quantity,
        "address": address,
    }
    if slippage is not None:
        params["slippage"] = slippage
    if recipient:
        params["recipient"] = recipient
    return _client().get("/api/v2/swap/quote", params=params)


def os_swap_execute(payload: Dict[str, Any]) -> Dict[str, Any]:
    return _client().post("/api/v2/swap/execute", data=payload)


def os_transaction_receipt(
    swap_quote: Dict[str, Any],
    transaction_identifiers: Optional[list] = None,
    relay_request_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"swap_quote": swap_quote}
    if transaction_identifiers:
        payload["transaction_identifiers"] = transaction_identifiers
    if relay_request_id:
        payload["relay_request_id"] = relay_request_id
    if request_id:
        payload["request_id"] = request_id
    return _client().post("/api/v2/transactions/receipt", data=payload)


__all__ = [
    "os_create_instant_api_key",
    "os_collections",
    "os_collection",
    "os_collection_stats",
    "os_collection_holders",
    "os_collection_floor_prices",
    "os_collections_trending",
    "os_collections_top",
    "os_search",
    "os_nft",
    "os_nfts_by_contract",
    "os_events",
    "os_events_by_collection",
    "os_events_by_nft",
    "os_listings_best",
    "os_listings_all",
    "os_offers_all",
    "os_offers_for_nft",
    "os_best_offer_for_nft",
    "os_swap_quote",
    "os_swap_execute",
    "os_transaction_receipt",
]
