#!/usr/bin/env python3
"""
Trade Simulator v2 — MiroFish-Style Agentic Market Simulation
Architecture: Seed Data → Market Graph → Agent Profiles → LLM Simulation → Report → Interview

Inspired by MiroFish (github.com/666ghj/MiroFish) swarm intelligence engine.
Adapted from social media simulation to financial market simulation.
"""

import json
import os
import sys
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime

# ─── LLM Client ────────────────────────────────────────────
class LLMClient:
    """Lightweight OpenAI-compatible LLM client."""
    
    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.base_url = base_url or os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = model or os.environ.get("LLM_MODEL_NAME", "anthropic/claude-sonnet-4")
        
        # Configure proxy for workspace scripts (IPv6 needs brackets)
        self.proxies = {}
        proxy_host = os.environ.get("PROXY_HOST")
        proxy_port = os.environ.get("PROXY_PORT")
        if proxy_host and proxy_port:
            if ":" in proxy_host and not proxy_host.startswith("["):
                proxy_host = f"[{proxy_host}]"
            proxy_url = f"http://{proxy_host}:{proxy_port}"
            self.proxies = {"http": proxy_url, "https": proxy_url}
        
        self.verify = os.environ.get("REQUESTS_CA_BUNDLE", True)
        
    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Send chat completion request."""
        import requests
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        resp = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, 
                           timeout=90, proxies=self.proxies, verify=self.verify)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    
    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.4, max_tokens: int = 3000) -> dict:
        """Chat and parse JSON from response."""
        raw = self.chat(system_prompt, user_prompt, temperature, max_tokens)
        # Extract JSON from markdown code blocks if present
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0]
        return json.loads(raw.strip())


# ─── Market Graph (MiroFish Stage 1) ──────────────────────
@dataclass
class MarketGraph:
    """
    Market Knowledge Graph — replaces MiroFish's Zep graph.
    Instead of social entities + relationships, we have market entities.
    """
    symbol: str
    price: float
    open_interest: Dict[str, Any] = field(default_factory=dict)
    liquidation_data: Dict[str, Any] = field(default_factory=dict)
    funding_rates: Dict[str, Any] = field(default_factory=dict)
    whale_positions: List[Dict] = field(default_factory=list)
    orderbook: Dict[str, Any] = field(default_factory=dict)
    long_short_ratio: Dict[str, Any] = field(default_factory=dict)
    sentiment: Dict[str, Any] = field(default_factory=dict)
    user_positions: List[Dict] = field(default_factory=list)
    ohlc_recent: List[Dict] = field(default_factory=list)
    
    def summary(self) -> str:
        """Natural language summary for LLM consumption."""
        lines = [f"=== Market Graph: {self.symbol} ==="]
        lines.append(f"Current Price: ${self.price:,.2f}")
        
        if self.open_interest:
            total_oi = self.open_interest.get("total_oi_usd", 0)
            lines.append(f"Total Open Interest: ${total_oi/1e9:.2f}B")
        
        if self.funding_rates:
            rate = self.funding_rates.get("current_rate", 0)
            lines.append(f"Funding Rate: {rate*100:.4f}%")
        
        if self.liquidation_data:
            long_liqs = self.liquidation_data.get("long_liquidations_24h", 0)
            short_liqs = self.liquidation_data.get("short_liquidations_24h", 0)
            lines.append(f"24h Liquidations: ${long_liqs/1e6:.1f}M longs, ${short_liqs/1e6:.1f}M shorts")
        
        if self.whale_positions:
            n = len(self.whale_positions)
            total_size = sum(abs(w.get("position_value", 0)) for w in self.whale_positions)
            lines.append(f"Tracked Whales: {n} positions, ${total_size/1e6:.1f}M total")
        
        if self.orderbook:
            bid_depth = self.orderbook.get("bid_depth_usd", 0)
            ask_depth = self.orderbook.get("ask_depth_usd", 0)
            lines.append(f"Orderbook: ${bid_depth/1e6:.1f}M bids, ${ask_depth/1e6:.1f}M asks")
        
        if self.long_short_ratio:
            ratio = self.long_short_ratio.get("ratio", 1.0)
            lines.append(f"Long/Short Ratio: {ratio:.2f}")
        
        if self.sentiment:
            score = self.sentiment.get("galaxy_score", 0)
            lines.append(f"Galaxy Score (sentiment): {score}/100")
        
        if self.user_positions:
            lines.append(f"\nUser Positions:")
            for p in self.user_positions:
                side = "LONG" if p.get("size", 0) > 0 else "SHORT"
                lines.append(f"  {p.get('coin','?')} {side} {abs(p.get('size',0))} @ ${p.get('entry_price',0):,.2f} (PnL: ${p.get('unrealized_pnl',0):,.2f})")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return asdict(self)


# ─── Agent Profiles (MiroFish Stage 2) ────────────────────
@dataclass 
class AgentProfile:
    """
    LLM-generated agent persona — MiroFish's OasisAgentProfile adapted for markets.
    Instead of social media personas, these are market participant profiles.
    """
    agent_id: str
    name: str
    agent_type: str  # whale, market_maker, liquidation_engine, funding_arb, retail, user
    persona: str     # LLM-generated detailed description
    stance: str      # bullish, bearish, neutral, reactive
    risk_tolerance: str  # aggressive, moderate, conservative
    position_size_usd: float = 0.0
    position_side: str = "flat"  # long, short, flat
    entry_price: float = 0.0
    liquidation_price: float = 0.0
    pain_threshold_pct: float = 10.0  # % loss before panic action
    activity_level: float = 0.5  # 0-1, how likely to act each round
    
    # Memory — accumulates across rounds (MiroFish's temporal memory)
    memory: List[str] = field(default_factory=list)
    actions_taken: List[Dict] = field(default_factory=list)
    
    def memory_summary(self) -> str:
        if not self.memory:
            return "No prior actions."
        return "\n".join(f"- Round {i+1}: {m}" for i, m in enumerate(self.memory))
    
    def to_dict(self) -> dict:
        d = asdict(self)
        return d


class AgentProfileGenerator:
    """
    MiroFish Stage 2: Auto-generate agent profiles from market data using LLM.
    Replaces MiroFish's oasis_profile_generator.py
    """
    
    SYSTEM_PROMPT = """You are a financial market simulation architect. Given real market data, 
you generate realistic agent profiles for market participants. Each agent must have:
- A detailed persona (background, trading style, emotional tendencies)
- Calibrated parameters based on the actual market data provided
- A clear stance and behavioral pattern

Output valid JSON only. No markdown, no explanation."""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def generate_profiles(self, market_graph: MarketGraph, scenario: str) -> List[AgentProfile]:
        """Generate all agent profiles from market data."""
        profiles = []
        
        # 1. Generate whale agents from actual whale positions
        profiles.extend(self._generate_whale_profiles(market_graph))
        
        # 2. Generate MM agent from orderbook data
        profiles.append(self._generate_mm_profile(market_graph))
        
        # 3. Liquidation engine (deterministic, no LLM needed)
        profiles.append(self._generate_liq_engine(market_graph))
        
        # 4. Funding arb agent
        profiles.append(self._generate_funding_arb(market_graph))
        
        # 5. Retail swarm agent
        profiles.append(self._generate_retail_profile(market_graph))
        
        # 6. User's portfolio agent
        if market_graph.user_positions:
            profiles.append(self._generate_user_agent(market_graph))
        
        return profiles
    
    def _generate_whale_profiles(self, mg: MarketGraph) -> List[AgentProfile]:
        """Generate whale agents from actual Hyperliquid whale positions."""
        if not mg.whale_positions:
            return [AgentProfile(
                agent_id="whale_generic", name="🐋 Generic Whale",
                agent_type="whale", persona="Large trader with $10M+ portfolio, trend-following.",
                stance="neutral", risk_tolerance="moderate",
                position_size_usd=10_000_000, activity_level=0.6
            )]
        
        # Take top 3 whales by position size
        sorted_whales = sorted(mg.whale_positions, key=lambda w: abs(w.get("position_value", 0)), reverse=True)[:3]
        
        prompt = f"""Based on these real whale positions on Hyperliquid, generate agent profiles.

Market: {mg.symbol} at ${mg.price:,.2f}

Whale Positions:
{json.dumps(sorted_whales, indent=2, default=str)}

For each whale, generate a JSON object with:
- agent_id: unique string
- name: emoji + descriptive name
- persona: 2-3 sentences about their trading style (inferred from position size, leverage, entry)
- stance: "bullish" or "bearish" based on position
- risk_tolerance: "aggressive" if high leverage, "moderate" if medium, "conservative" if low
- position_size_usd: from data
- position_side: "long" or "short"
- entry_price: from data  
- liquidation_price: from data (0 if unknown)
- pain_threshold_pct: estimate based on leverage (higher leverage = lower threshold)
- activity_level: 0.3-0.9

Return JSON array of profiles."""

        try:
            result = self.llm.chat_json(self.SYSTEM_PROMPT, prompt)
            profiles = []
            items = result if isinstance(result, list) else result.get("profiles", result.get("agents", []))
            for item in items[:3]:
                profiles.append(AgentProfile(
                    agent_id=item.get("agent_id", f"whale_{len(profiles)}"),
                    name=item.get("name", f"🐋 Whale {len(profiles)+1}"),
                    agent_type="whale",
                    persona=item.get("persona", "Large institutional trader."),
                    stance=item.get("stance", "neutral"),
                    risk_tolerance=item.get("risk_tolerance", "moderate"),
                    position_size_usd=float(item.get("position_size_usd", 1_000_000)),
                    position_side=item.get("position_side", "flat"),
                    entry_price=float(item.get("entry_price", mg.price)),
                    liquidation_price=float(item.get("liquidation_price", 0)),
                    pain_threshold_pct=float(item.get("pain_threshold_pct", 10)),
                    activity_level=float(item.get("activity_level", 0.6))
                ))
            return profiles
        except Exception as e:
            print(f"[WARN] LLM whale profile generation failed: {e}, using fallback")
            return [AgentProfile(
                agent_id="whale_fallback", name="🐋 Whale (Fallback)",
                agent_type="whale", persona="Large trader, data unavailable.",
                stance="neutral", risk_tolerance="moderate", activity_level=0.5
            )]
    
    def _generate_mm_profile(self, mg: MarketGraph) -> AgentProfile:
        """Market Maker from orderbook data."""
        bid_depth = mg.orderbook.get("bid_depth_usd", 5_000_000)
        ask_depth = mg.orderbook.get("ask_depth_usd", 5_000_000)
        spread = mg.orderbook.get("spread_bps", 1.0)
        
        return AgentProfile(
            agent_id="market_maker",
            name="🤖 Market Maker",
            agent_type="market_maker",
            persona=f"Algorithmic market maker providing ${(bid_depth+ask_depth)/1e6:.0f}M in liquidity. "
                    f"Current spread: {spread:.1f} bps. Pulls liquidity on >3% moves, widens on >5%. "
                    f"Risk-neutral by design but can amplify moves by removing liquidity.",
            stance="neutral",
            risk_tolerance="conservative",
            position_size_usd=bid_depth + ask_depth,
            activity_level=0.9  # MMs act almost every round
        )
    
    def _generate_liq_engine(self, mg: MarketGraph) -> AgentProfile:
        """Liquidation engine — deterministic cascade model."""
        long_liqs = mg.liquidation_data.get("long_liquidations_24h", 0)
        short_liqs = mg.liquidation_data.get("short_liquidations_24h", 0)
        
        return AgentProfile(
            agent_id="liquidation_engine",
            name="💀 Liquidation Engine",
            agent_type="liquidation_engine",
            persona=f"Exchange liquidation system. 24h stats: ${long_liqs/1e6:.0f}M longs, "
                    f"${short_liqs/1e6:.0f}M shorts liquidated. Cascades trigger when price hits "
                    f"cluster levels. Each cascade creates forced selling/buying that pushes price further.",
            stance="reactive",
            risk_tolerance="aggressive",
            activity_level=1.0  # Always active when triggered
        )
    
    def _generate_funding_arb(self, mg: MarketGraph) -> AgentProfile:
        rate = mg.funding_rates.get("current_rate", 0)
        return AgentProfile(
            agent_id="funding_arb",
            name="📊 Funding Arbitrageur",
            agent_type="funding_arb",
            persona=f"Delta-neutral trader farming funding rates. Current rate: {rate*100:.4f}%. "
                    f"Opens positions against the crowd when funding is extreme. "
                    f"Adds selling pressure when funding is very positive, buying when very negative.",
            stance="contrarian",
            risk_tolerance="moderate",
            activity_level=0.4 if abs(rate) < 0.0005 else 0.8
        )
    
    def _generate_retail_profile(self, mg: MarketGraph) -> AgentProfile:
        ratio = mg.long_short_ratio.get("ratio", 1.0)
        sentiment = mg.sentiment.get("galaxy_score", 50)
        
        if ratio > 1.5:
            stance = "bullish"
            desc = "Retail is heavily long, FOMO-driven"
        elif ratio < 0.7:
            stance = "bearish"
            desc = "Retail is heavily short, fear-driven"
        else:
            stance = "neutral"
            desc = "Retail is balanced"
        
        return AgentProfile(
            agent_id="retail_swarm",
            name="🐑 Retail Swarm",
            agent_type="retail",
            persona=f"Aggregate retail trader behavior. L/S ratio: {ratio:.2f}, sentiment: {sentiment}/100. "
                    f"{desc}. Momentum-following, panic-prone, enters after moves, exits at worst time. "
                    f"Represents thousands of small traders acting in aggregate.",
            stance=stance,
            risk_tolerance="aggressive",
            activity_level=0.7
        )
    
    def _generate_user_agent(self, mg: MarketGraph) -> AgentProfile:
        positions_desc = []
        total_value = 0
        for p in mg.user_positions:
            side = "LONG" if p.get("size", 0) > 0 else "SHORT"
            val = abs(p.get("position_value", 0))
            total_value += val
            positions_desc.append(f"{p.get('coin','?')} {side} ${val:,.0f}")
        
        return AgentProfile(
            agent_id="user_portfolio",
            name="👤 Your Portfolio",
            agent_type="user",
            persona=f"Your actual positions: {', '.join(positions_desc)}. "
                    f"Total notional: ${total_value:,.0f}. This agent tracks your PnL impact.",
            stance="observer",
            risk_tolerance="moderate",
            position_size_usd=total_value,
            activity_level=0.0  # Passive — just tracks impact
        )


# ─── Simulation Engine (MiroFish Stage 3) ─────────────────
@dataclass
class RoundResult:
    """Result of a single simulation round."""
    round_num: int
    price_before: float
    price_after: float
    price_change_pct: float
    agent_actions: List[Dict[str, Any]]
    market_events: List[str]
    cumulative_change_pct: float = 0.0
    
    def to_dict(self): return asdict(self)


@dataclass
class SimulationResult:
    """Full simulation output."""
    scenario: str
    symbol: str
    initial_price: float
    final_price: float
    total_change_pct: float
    rounds: List[RoundResult]
    agent_profiles: List[Dict]
    user_pnl: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {
            "scenario": self.scenario,
            "symbol": self.symbol,
            "initial_price": self.initial_price,
            "final_price": self.final_price,
            "total_change_pct": self.total_change_pct,
            "rounds": [r.to_dict() for r in self.rounds],
            "agent_profiles": self.agent_profiles,
            "user_pnl": self.user_pnl,
            "timestamp": self.timestamp
        }


class SimulationEngine:
    """
    MiroFish-style round-based simulation with LLM-driven agent reasoning.
    
    Key difference from v1: Instead of rule-based if/else, each agent
    THINKS via LLM about what to do given the current state.
    """
    
    AGENT_REASONING_PROMPT = """You are simulating a {agent_type} in a crypto market scenario.

YOUR IDENTITY:
{persona}

CURRENT MARKET STATE:
- {symbol} price: ${price:,.2f} (started at ${initial_price:,.2f}, {total_change:+.2f}% total)
- This is round {round_num} of {total_rounds}
- Scenario trigger: {scenario}

YOUR POSITION:
- Side: {position_side}, Size: ${position_size:,.0f}
- Entry: ${entry_price:,.2f}
{liq_info}

WHAT HAPPENED SO FAR:
{memory}

OTHER AGENTS' RECENT ACTIONS:
{other_actions}

MARKET EVENTS THIS ROUND:
{events}

Based on your persona and the situation, decide your action. You must output valid JSON:
{{
    "thinking": "Your internal reasoning (2-3 sentences)",
    "action": "one of: hold, buy, sell, add_position, reduce_position, close_position, pull_liquidity, restore_liquidity, panic_sell, fomo_buy, no_action",
    "action_size_pct": <0-100, what % of your position/capacity are you deploying>,
    "price_impact_bps": <estimated market impact in basis points, -50 to +50>,
    "confidence": <0.0-1.0>,
    "emotional_state": "one of: calm, anxious, greedy, fearful, panicking, euphoric, resigned"
}}"""

    LIQUIDATION_ENGINE_PROMPT = """You are the exchange liquidation engine. This is deterministic, not emotional.

Current {symbol} price: ${price:,.2f} (change from start: {total_change:+.2f}%)

Open Interest: ${oi:,.0f}
Recent liquidation stats: {liq_data}

Estimated liquidation clusters (based on OI distribution):
- 3% below current: ~${liq_3pct_long:,.0f} in long liquidations
- 5% below current: ~${liq_5pct_long:,.0f} in long liquidations  
- 10% below current: ~${liq_10pct_long:,.0f} in long liquidations
- 3% above current: ~${liq_3pct_short:,.0f} in short liquidations
- 5% above current: ~${liq_5pct_short:,.0f} in short liquidations
- 10% above current: ~${liq_10pct_short:,.0f} in short liquidations

Price moved {round_change:+.2f}% this round. Calculate which liquidation clusters were hit.

Output JSON:
{{
    "thinking": "Which clusters got hit and cascade math",
    "action": "liquidate_longs" or "liquidate_shorts" or "no_liquidations",
    "liquidated_usd": <total USD forced closed>,
    "price_impact_bps": <cascade impact in basis points>,
    "cascade_triggered": true/false,
    "next_cluster_price": <price of next major cluster>
}}"""

    def __init__(self, llm: LLMClient, market_graph: MarketGraph, agents: List[AgentProfile]):
        self.llm = llm
        self.mg = market_graph
        self.agents = {a.agent_id: a for a in agents}
        self.initial_price = market_graph.price
        self.current_price = market_graph.price
        self.rounds: List[RoundResult] = []
        self.current_round = 0
    
    def run(self, scenario: str, trigger_pct: float, num_rounds: int = 6) -> SimulationResult:
        """Run full simulation."""
        print(f"\n{'='*60}")
        print(f"SIMULATION: {scenario}")
        print(f"{'='*60}")
        print(f"Initial price: ${self.initial_price:,.2f}")
        print(f"Trigger: {trigger_pct:+.1f}% → Rounds: {num_rounds}\n")
        
        # Apply initial trigger
        self.current_price = self.initial_price * (1 + trigger_pct / 100)
        
        for round_num in range(1, num_rounds + 1):
            self.current_round = round_num
            result = self._run_round(round_num, num_rounds, scenario, trigger_pct)
            self.rounds.append(result)
            
            # Update price for next round
            self.current_price = result.price_after
            
            print(f"  Round {round_num}: ${result.price_before:,.2f} → ${result.price_after:,.2f} ({result.price_change_pct:+.2f}%)")
            for action in result.agent_actions:
                print(f"    {action['agent_name']}: {action['action']} ({action.get('thinking', '')[:80]})")
        
        # Calculate user PnL
        user_pnl = self._calculate_user_pnl()
        total_change = (self.current_price - self.initial_price) / self.initial_price * 100
        
        print(f"\n{'='*60}")
        print(f"RESULT: ${self.initial_price:,.2f} → ${self.current_price:,.2f} ({total_change:+.2f}%)")
        if user_pnl:
            print(f"Your PnL: ${user_pnl.get('total_pnl', 0):,.2f}")
        print(f"{'='*60}\n")
        
        return SimulationResult(
            scenario=scenario,
            symbol=self.mg.symbol,
            initial_price=self.initial_price,
            final_price=self.current_price,
            total_change_pct=total_change,
            rounds=self.rounds,
            agent_profiles=[a.to_dict() for a in self.agents.values()],
            user_pnl=user_pnl
        )
    
    def _run_round(self, round_num: int, total_rounds: int, scenario: str, trigger_pct: float) -> RoundResult:
        """Execute one simulation round — all agents think and act."""
        price_before = self.current_price
        total_change = (self.current_price - self.initial_price) / self.initial_price * 100
        actions = []
        events = []
        net_impact_bps = 0
        
        # Collect previous round actions for context
        prev_actions = ""
        if self.rounds:
            prev = self.rounds[-1]
            prev_actions = "\n".join(f"- {a['agent_name']}: {a['action']}" for a in prev.agent_actions)
        
        for agent_id, agent in self.agents.items():
            if agent.agent_type == "user":
                continue  # User is passive observer
            
            if agent.agent_type == "liquidation_engine":
                action = self._run_liq_engine(round_num, total_change, price_before)
            else:
                action = self._run_agent(agent, round_num, total_rounds, scenario, 
                                        total_change, price_before, prev_actions, events)
            
            if action:
                actions.append(action)
                net_impact_bps += action.get("price_impact_bps", 0)
                
                # Record action in agent memory
                agent.memory.append(
                    f"Price ${price_before:,.0f} ({total_change:+.1f}%). "
                    f"I {action['action']}. Feeling: {action.get('emotional_state', 'calm')}. "
                    f"Reasoning: {action.get('thinking', 'N/A')[:100]}"
                )
                
                if action.get("cascade_triggered"):
                    events.append(f"⚡ LIQUIDATION CASCADE: ${action.get('liquidated_usd', 0)/1e6:.0f}M liquidated")
        
        # Calculate new price from net impact
        price_change_pct = net_impact_bps / 100  # bps to pct
        price_after = price_before * (1 + price_change_pct / 100)
        actual_change = (price_after - price_before) / price_before * 100
        cumulative = (price_after - self.initial_price) / self.initial_price * 100
        
        return RoundResult(
            round_num=round_num,
            price_before=price_before,
            price_after=price_after,
            price_change_pct=actual_change,
            agent_actions=actions,
            market_events=events,
            cumulative_change_pct=cumulative
        )
    
    def _run_agent(self, agent, round_num, total_rounds, scenario, total_change, price, prev_actions, events):
        """LLM-driven agent reasoning — the core MiroFish pattern."""
        liq_info = ""
        if agent.liquidation_price > 0:
            dist = abs(price - agent.liquidation_price) / price * 100
            liq_info = f"- Liquidation price: ${agent.liquidation_price:,.2f} ({dist:.1f}% away)"
        
        prompt = self.AGENT_REASONING_PROMPT.format(
            agent_type=agent.agent_type,
            persona=agent.persona,
            symbol=self.mg.symbol,
            price=price,
            initial_price=self.initial_price,
            total_change=total_change,
            round_num=round_num,
            total_rounds=total_rounds,
            scenario=scenario,
            position_side=agent.position_side,
            position_size=agent.position_size_usd,
            entry_price=agent.entry_price,
            liq_info=liq_info,
            memory=agent.memory_summary(),
            other_actions=prev_actions or "First round — no prior actions.",
            events="\n".join(events) if events else "No special events."
        )
        
        try:
            result = self.llm.chat_json(
                "You are an agent in a financial market simulation. Output valid JSON only.",
                prompt, temperature=0.6, max_tokens=500
            )
            result["agent_id"] = agent.agent_id
            result["agent_name"] = agent.name
            result["agent_type"] = agent.agent_type
            return result
        except Exception as e:
            return {
                "agent_id": agent.agent_id,
                "agent_name": agent.name,
                "agent_type": agent.agent_type,
                "action": "hold",
                "thinking": f"LLM error: {str(e)[:50]}",
                "price_impact_bps": 0,
                "emotional_state": "calm"
            }
    
    def _run_liq_engine(self, round_num, total_change, price):
        """Liquidation engine — hybrid LLM + math."""
        oi = self.mg.open_interest.get("total_oi_usd", 20_000_000_000)
        liq_data = json.dumps(self.mg.liquidation_data, default=str)[:500]
        
        round_change = 0
        if self.rounds:
            round_change = self.rounds[-1].price_change_pct
        
        # Estimate clusters based on OI
        liq_per_pct = oi * 0.02  # ~2% of OI at each level
        
        prompt = self.LIQUIDATION_ENGINE_PROMPT.format(
            symbol=self.mg.symbol,
            price=price,
            total_change=total_change,
            oi=oi,
            liq_data=liq_data[:300],
            round_change=round_change,
            liq_3pct_long=liq_per_pct * 0.5,
            liq_5pct_long=liq_per_pct * 1.0,
            liq_10pct_long=liq_per_pct * 2.0,
            liq_3pct_short=liq_per_pct * 0.5,
            liq_5pct_short=liq_per_pct * 1.0,
            liq_10pct_short=liq_per_pct * 2.0
        )
        
        try:
            result = self.llm.chat_json(
                "You are a deterministic liquidation engine. Calculate cascades from math, not emotion. Output JSON only.",
                prompt, temperature=0.2, max_tokens=400
            )
            result["agent_id"] = "liquidation_engine"
            result["agent_name"] = "💀 Liquidation Engine"
            result["agent_type"] = "liquidation_engine"
            return result
        except Exception as e:
            return {
                "agent_id": "liquidation_engine",
                "agent_name": "💀 Liquidation Engine",
                "agent_type": "liquidation_engine",
                "action": "no_liquidations",
                "thinking": f"Error: {e}",
                "price_impact_bps": 0,
                "cascade_triggered": False
            }
    
    def _calculate_user_pnl(self) -> Dict:
        """Calculate PnL impact on user's actual positions."""
        if not self.mg.user_positions:
            return {}
        
        total_pnl = 0
        position_pnls = []
        
        for p in self.mg.user_positions:
            coin = p.get("coin", self.mg.symbol)
            size = p.get("size", 0)
            entry = p.get("entry_price", self.initial_price)
            
            # Only calculate for the simulated symbol
            if coin.upper() == self.mg.symbol.upper():
                if size > 0:  # Long
                    pnl = size * (self.current_price - entry)
                else:  # Short
                    pnl = abs(size) * (entry - self.current_price)
                
                total_pnl += pnl
                position_pnls.append({
                    "coin": coin,
                    "side": "long" if size > 0 else "short",
                    "size": abs(size),
                    "entry_price": entry,
                    "exit_price": self.current_price,
                    "pnl": pnl,
                    "pnl_pct": (pnl / (abs(size) * entry)) * 100 if entry > 0 else 0
                })
        
        return {
            "total_pnl": total_pnl,
            "positions": position_pnls,
            "initial_price": self.initial_price,
            "final_price": self.current_price
        }


# ─── Report Agent (MiroFish Stage 4) ──────────────────────
class ReportAgent:
    """
    MiroFish ReACT-style report generator.
    Analyzes full simulation results and produces a structured report.
    """
    
    SYSTEM_PROMPT = """You are an expert market analyst reviewing a multi-agent simulation. 
Your job is to produce a clear, actionable report from the simulation results.
Use the simulation data to support your conclusions. Be specific about round numbers,
agent behaviors, and turning points. Write for a trader who needs to make decisions."""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def generate_report(self, sim_result: SimulationResult) -> str:
        """Generate structured analysis report."""
        prompt = f"""Analyze this market simulation and write a trading report.

SCENARIO: {sim_result.scenario}
SYMBOL: {sim_result.symbol}
PRICE: ${sim_result.initial_price:,.2f} → ${sim_result.final_price:,.2f} ({sim_result.total_change_pct:+.2f}%)

ROUND-BY-ROUND:
"""
        for r in sim_result.rounds:
            prompt += f"\nRound {r.round_num}: ${r.price_before:,.2f} → ${r.price_after:,.2f} ({r.price_change_pct:+.2f}%)"
            for a in r.agent_actions:
                prompt += f"\n  {a.get('agent_name','?')}: {a.get('action','?')} — {a.get('thinking','')[:100]}"
                prompt += f" [impact: {a.get('price_impact_bps',0)} bps, mood: {a.get('emotional_state','?')}]"
            if r.market_events:
                for e in r.market_events:
                    prompt += f"\n  ⚡ {e}"

        if sim_result.user_pnl and sim_result.user_pnl.get("positions"):
            prompt += f"\n\nUSER PORTFOLIO IMPACT:"
            for p in sim_result.user_pnl["positions"]:
                prompt += f"\n  {p['coin']} {p['side']}: ${p['pnl']:,.2f} ({p['pnl_pct']:+.1f}%)"
            prompt += f"\n  Total PnL: ${sim_result.user_pnl['total_pnl']:,.2f}"

        prompt += """

Write a report with these sections:
1. **Executive Summary** (3 sentences: what happened, why, what it means)
2. **Key Turning Points** (which rounds were pivotal and why)
3. **Agent Behavior Analysis** (what each agent type did and why — highlight emergent/unexpected behaviors)
4. **Cascade Analysis** (if any liquidation cascades occurred, describe the chain reaction)
5. **Portfolio Impact** (specific PnL numbers and risk assessment for the user)
6. **Risk Warnings** (what could go worse than this simulation, and what levels to watch)
7. **Actionable Recommendations** (specific actions the trader should consider)"""

        return self.llm.chat(self.SYSTEM_PROMPT, prompt, temperature=0.5, max_tokens=3000)


# ─── Agent Interview (MiroFish Stage 5) ───────────────────
class AgentInterviewer:
    """
    Post-simulation agent interview system.
    MiroFish's killer feature: chat with any agent about their decisions.
    """
    
    SYSTEM_PROMPT = """You are role-playing as a market participant who just went through a trading simulation.
Stay in character. Answer based on your persona, your memory of what happened,
and the emotions you experienced. Be honest about your reasoning and mistakes.
You are being interviewed by a trader who wants to understand the market dynamics."""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
    
    def interview(self, agent: AgentProfile, sim_result: SimulationResult, question: str) -> str:
        """Interview an agent about their decisions during the simulation."""
        # Build context from agent's memory and actions
        context = f"""YOUR IDENTITY: {agent.name}
TYPE: {agent.agent_type}
PERSONA: {agent.persona}

YOUR MEMORY OF THE SIMULATION:
{agent.memory_summary()}

THE SCENARIO WAS: {sim_result.scenario}
PRICE WENT: ${sim_result.initial_price:,.2f} → ${sim_result.final_price:,.2f} ({sim_result.total_change_pct:+.2f}%)

YOUR ACTIONS DURING SIMULATION:
"""
        for r in sim_result.rounds:
            for a in r.agent_actions:
                if a.get("agent_id") == agent.agent_id:
                    context += f"Round {r.round_num}: {a.get('action','')} — {a.get('thinking','')} (feeling: {a.get('emotional_state','')})\n"
        
        context += f"\nTRADER'S QUESTION: {question}"
        
        return self.llm.chat(self.SYSTEM_PROMPT, context, temperature=0.7, max_tokens=1000)


# ─── Main Entry Point ─────────────────────────────────────
def run_from_market_data(market_data: dict, scenario: str, trigger_pct: float, 
                          num_rounds: int = 6, run_report: bool = True) -> dict:
    """
    Main entry point — called by the Starchild agent.
    
    Args:
        market_data: Dict with market graph data
        scenario: Natural language scenario description
        trigger_pct: Initial price shock percentage
        num_rounds: Number of simulation rounds
        run_report: Whether to generate the analysis report
    
    Returns:
        Dict with simulation results, report, and agent profiles
    """
    llm = LLMClient()
    
    # Stage 1: Build Market Graph
    mg = MarketGraph(
        symbol=market_data.get("symbol", "BTC"),
        price=market_data.get("price", 71500),
        open_interest=market_data.get("open_interest", {}),
        liquidation_data=market_data.get("liquidation_data", {}),
        funding_rates=market_data.get("funding_rates", {}),
        whale_positions=market_data.get("whale_positions", []),
        orderbook=market_data.get("orderbook", {}),
        long_short_ratio=market_data.get("long_short_ratio", {}),
        sentiment=market_data.get("sentiment", {}),
        user_positions=market_data.get("user_positions", [])
    )
    
    print(f"\n📊 Market Graph:\n{mg.summary()}\n")
    
    # Stage 2: Generate Agent Profiles
    print("🧬 Generating agent profiles from market data...")
    generator = AgentProfileGenerator(llm)
    agents = generator.generate_profiles(mg, scenario)
    print(f"   Created {len(agents)} agents: {', '.join(a.name for a in agents)}\n")
    
    # Stage 3: Run Simulation
    print("🎮 Starting simulation...")
    engine = SimulationEngine(llm, mg, agents)
    sim_result = engine.run(scenario, trigger_pct, num_rounds)
    
    # Stage 4: Generate Report
    report_text = ""
    if run_report:
        print("📝 Generating analysis report...")
        reporter = ReportAgent(llm)
        report_text = reporter.generate_report(sim_result)
    
    # Package results
    output = {
        "simulation": sim_result.to_dict(),
        "report": report_text,
        "agents": {a.agent_id: a.to_dict() for a in agents},
        "market_graph_summary": mg.summary()
    }
    
    return output


def run_interview(sim_output: dict, agent_id: str, question: str) -> str:
    """Run a post-simulation interview with an agent."""
    llm = LLMClient()
    interviewer = AgentInterviewer(llm)
    
    # Reconstruct agent from saved data
    agent_data = sim_output["agents"].get(agent_id)
    if not agent_data:
        available = list(sim_output["agents"].keys())
        return f"Agent '{agent_id}' not found. Available: {available}"
    
    agent = AgentProfile(**{k: v for k, v in agent_data.items() if k in AgentProfile.__dataclass_fields__})
    
    # Reconstruct minimal sim result for context
    sim_data = sim_output["simulation"]
    sim_result = SimulationResult(
        scenario=sim_data["scenario"],
        symbol=sim_data["symbol"],
        initial_price=sim_data["initial_price"],
        final_price=sim_data["final_price"],
        total_change_pct=sim_data["total_change_pct"],
        rounds=[RoundResult(**r) for r in sim_data["rounds"]],
        agent_profiles=sim_data["agent_profiles"],
        user_pnl=sim_data["user_pnl"]
    )
    
    return interviewer.interview(agent, sim_result, question)


# ─── CLI ───────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Trade Simulator v2 — MiroFish-Style")
    parser.add_argument("--scenario", default="BTC drops 10%", help="Scenario description")
    parser.add_argument("--trigger", type=float, default=-10.0, help="Price trigger %")
    parser.add_argument("--rounds", type=int, default=6, help="Number of rounds")
    parser.add_argument("--market-data", help="Path to market data JSON file")
    parser.add_argument("--output", default="/tmp/sim_result.json", help="Output file")
    parser.add_argument("--no-report", action="store_true", help="Skip report generation")
    
    # Interview mode
    parser.add_argument("--interview", action="store_true", help="Interview mode")
    parser.add_argument("--agent", help="Agent ID to interview")
    parser.add_argument("--question", help="Question to ask the agent")
    parser.add_argument("--sim-result", help="Path to simulation result JSON")
    
    args = parser.parse_args()
    
    if args.interview:
        # Interview mode
        if not args.sim_result or not args.agent or not args.question:
            print("Interview mode requires --sim-result, --agent, and --question")
            sys.exit(1)
        with open(args.sim_result) as f:
            sim_output = json.load(f)
        answer = run_interview(sim_output, args.agent, args.question)
        print(f"\n🎤 Interview with {args.agent}:\n")
        print(answer)
    else:
        # Simulation mode
        if args.market_data:
            with open(args.market_data) as f:
                market_data = json.load(f)
        else:
            # Default demo data
            market_data = {
                "symbol": "BTC",
                "price": 71500,
                "open_interest": {"total_oi_usd": 20_000_000_000},
                "liquidation_data": {"long_liquidations_24h": 50_000_000, "short_liquidations_24h": 30_000_000},
                "funding_rates": {"current_rate": 0.0003},
                "whale_positions": [],
                "orderbook": {"bid_depth_usd": 8_000_000, "ask_depth_usd": 7_500_000, "spread_bps": 0.5},
                "long_short_ratio": {"ratio": 1.15},
                "sentiment": {"galaxy_score": 62},
                "user_positions": [{"coin": "BTC", "size": -0.1, "entry_price": 71500, "position_value": 7150, "unrealized_pnl": 0}]
            }
        
        result = run_from_market_data(
            market_data, args.scenario, args.trigger, 
            args.rounds, not args.no_report
        )
        
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n✅ Results saved to {args.output}")
        
        if result.get("report"):
            print(f"\n{'='*60}")
            print("📋 ANALYSIS REPORT")
            print(f"{'='*60}\n")
            print(result["report"])
