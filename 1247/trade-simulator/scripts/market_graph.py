"""
Market State Graph — MiroFish Stage 1 Adaptation

MiroFish uses Zep Cloud to build a knowledge graph from seed documents.
We build an equivalent in-memory graph from live market data.

Original: graph_builder.py -> Zep EpisodeData -> nodes/edges
Ours: market data tools -> MarketNode/MarketEdge -> MarketGraph
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


@dataclass
class MarketNode:
    uuid: str
    name: str
    node_type: str  # asset, exchange, whale, funding_state, etc.
    attributes: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    
    def to_dict(self):
        return {"uuid": self.uuid, "name": self.name, "type": self.node_type,
                "attributes": self.attributes, "summary": self.summary}


@dataclass 
class MarketEdge:
    source_uuid: str
    target_uuid: str
    relation: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return {"source": self.source_uuid, "target": self.target_uuid,
                "relation": self.relation, "attributes": self.attributes}


class MarketGraph:
    """In-memory knowledge graph replacing MiroFish's Zep Cloud dependency."""
    
    def __init__(self):
        self.nodes: Dict[str, MarketNode] = {}
        self.edges: List[MarketEdge] = []
        self.built_at: Optional[str] = None
    
    def add_node(self, node: MarketNode):
        self.nodes[node.uuid] = node
    
    def add_edge(self, edge: MarketEdge):
        self.edges.append(edge)
    
    def get_nodes_by_type(self, node_type: str) -> List[MarketNode]:
        return [n for n in self.nodes.values() if n.node_type == node_type]
    
    def get_edges_for_node(self, uuid: str) -> List[MarketEdge]:
        return [e for e in self.edges if e.source_uuid == uuid or e.target_uuid == uuid]
    
    def query(self, query: str) -> str:
        """Simple text search. MiroFish equivalent: ZepToolsService.quick_search()"""
        results = []
        q = query.lower()
        for node in self.nodes.values():
            if q in node.summary.lower() or q in node.name.lower():
                results.append(f"[{node.node_type}] {node.name}: {node.summary}")
        return "\n".join(results[:20]) if results else f"No results for '{query}'"
    
    def get_full_context(self) -> str:
        """Complete graph as readable text for LLM context."""
        parts = [f"=== MARKET STATE GRAPH (built {self.built_at}) ===\n"]
        by_type: Dict[str, List[MarketNode]] = {}
        for node in self.nodes.values():
            by_type.setdefault(node.node_type, []).append(node)
        for ntype, nodes in by_type.items():
            parts.append(f"\n--- {ntype.upper()} ---")
            for node in nodes:
                parts.append(f"  {node.name}: {node.summary}")
                for k, v in node.attributes.items():
                    parts.append(f"    {k}: {v}")
        parts.append(f"\n--- RELATIONSHIPS ({len(self.edges)}) ---")
        for edge in self.edges:
            src = self.nodes.get(edge.source_uuid, MarketNode("?","?","?"))
            tgt = self.nodes.get(edge.target_uuid, MarketNode("?","?","?"))
            parts.append(f"  {src.name} --[{edge.relation}]--> {tgt.name}")
        return "\n".join(parts)
    
    def to_dict(self):
        return {"built_at": self.built_at, "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "nodes": [n.to_dict() for n in self.nodes.values()],
                "edges": [e.to_dict() for e in self.edges]}


def build_market_graph(market_data: Dict[str, Any]) -> MarketGraph:
    """
    Build market state graph from collected data.
    MiroFish equivalent: GraphBuilderService.build_graph_async()
    """
    graph = MarketGraph()
    graph.built_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    symbol = market_data.get("symbol", "BTC")
    price = market_data.get("price", 0)
    
    # Asset node
    asset_id = f"asset_{symbol}"
    graph.add_node(MarketNode(uuid=asset_id, name=symbol, node_type="asset",
        summary=f"{symbol} at ${price:,.0f}",
        attributes={"price": price, "change_24h": market_data.get("price_change_24h", "?")}))
    
    # Open Interest
    oi = market_data.get("oi", {})
    if oi:
        oi_id = f"oi_{symbol}"
        total = oi.get("total", 0)
        graph.add_node(MarketNode(uuid=oi_id, name=f"{symbol} OI", node_type="open_interest",
            summary=f"Total OI: ${total/1e9:.1f}B" if total > 1e9 else f"Total OI: ${total/1e6:.0f}M",
            attributes=oi))
        graph.add_edge(MarketEdge(asset_id, oi_id, "has_open_interest"))
    
    # Funding
    funding = market_data.get("funding", {})
    if funding:
        fund_id = f"funding_{symbol}"
        rate = funding.get("rate", 0)
        sent = "bullish" if rate > 0.005 else "bearish" if rate < -0.005 else "neutral"
        graph.add_node(MarketNode(uuid=fund_id, name=f"{symbol} Funding", node_type="funding_state",
            summary=f"Rate: {rate*100:.4f}% ({sent})", attributes=funding))
        graph.add_edge(MarketEdge(asset_id, fund_id, "has_funding_state"))
    
    # Liquidations
    liqs = market_data.get("liquidations", {})
    if liqs:
        liq_id = f"liqs_{symbol}"
        long_l = liqs.get("long_liquidations", 0)
        short_l = liqs.get("short_liquidations", 0)
        dom = "long-dominant" if long_l > short_l else "short-dominant"
        graph.add_node(MarketNode(uuid=liq_id, name=f"{symbol} Liquidations", node_type="liquidation_state",
            summary=f"24h: ${(long_l+short_l)/1e6:.1f}M ({dom})",
            attributes={"long_usd": long_l, "short_usd": short_l}))
        graph.add_edge(MarketEdge(asset_id, liq_id, "has_liquidation_state"))
    
    # Long/Short
    ls = market_data.get("long_short", {})
    if ls:
        ls_id = f"ls_{symbol}"
        ratio = ls.get("ratio", 1.0)
        crowd = "net long" if ratio > 1.1 else "net short" if ratio < 0.9 else "balanced"
        graph.add_node(MarketNode(uuid=ls_id, name=f"{symbol} L/S", node_type="positioning",
            summary=f"Ratio: {ratio:.2f} ({crowd})", attributes=ls))
        graph.add_edge(MarketEdge(asset_id, ls_id, "has_positioning"))
    
    # Whales (top 5)
    for i, w in enumerate(market_data.get("whales", [])[:5]):
        w_id = f"whale_{i}"
        side = w.get("side", "?")
        sz = w.get("size_usd", 0)
        pnl = w.get("unrealized_pnl", 0)
        graph.add_node(MarketNode(uuid=w_id, name=f"Whale#{i+1} ({side})", node_type="whale",
            summary=f"${sz/1e6:.1f}M {side}, PnL: ${pnl:,.0f}", attributes=w))
        graph.add_edge(MarketEdge(w_id, asset_id, f"holds_{side}"))
        if f"liqs_{symbol}" in graph.nodes:
            graph.add_edge(MarketEdge(w_id, f"liqs_{symbol}", "could_cascade_if_liquidated"))
    
    # ETF flows
    etf = market_data.get("etf_flows", {})
    if etf:
        etf_id = f"etf_{symbol}"
        nf = etf.get("net_flow", 0)
        d = "inflow" if nf > 0 else "outflow"
        graph.add_node(MarketNode(uuid=etf_id, name=f"{symbol} ETF", node_type="etf",
            summary=f"Net: ${nf/1e6:.1f}M ({d})", attributes=etf))
        graph.add_edge(MarketEdge(etf_id, asset_id, "institutional_flow"))
    
    # User positions
    for i, pos in enumerate(market_data.get("user_positions", [])):
        pos_id = f"user_pos_{i}"
        side = pos.get("side", "?")
        graph.add_node(MarketNode(uuid=pos_id, name=f"Your {pos.get('symbol',symbol)} {side}",
            node_type="user_position",
            summary=f"{side} {pos.get('size',0)} @ ${pos.get('entry_price',0):,.0f}, liq ${pos.get('liquidation_price',0):,.0f}",
            attributes=pos))
        graph.add_edge(MarketEdge(pos_id, asset_id, "user_exposure"))
    
    return graph
