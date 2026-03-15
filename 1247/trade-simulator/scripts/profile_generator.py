"""
Agent Profile Generator — MiroFish Stage 2 Adaptation

MiroFish: oasis_profile_generator.py
- Reads Zep graph entities
- LLM generates detailed persona (bio, MBTI, stance, activity patterns)
- Creates OasisAgentProfile with personality traits

Ours:
- Reads MarketGraph nodes (whales, funding state, OI, etc.)
- LLM generates market participant personas calibrated to live data
- Each agent gets behavioral parameters + reasoning prompt
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class MarketAgentProfile:
    """
    Equivalent to MiroFish's OasisAgentProfile.
    Instead of social media personality, this is a market participant persona.
    """
    agent_id: int
    name: str
    emoji: str
    archetype: str  # whale, market_maker, retail, funding_arb, liquidation_engine
    
    # LLM-generated persona (MiroFish pattern: detailed bio from graph context)
    persona: str = ""           # Full persona description
    trading_style: str = ""     # How they trade
    risk_tolerance: str = ""    # Conservative / moderate / aggressive
    pain_point: str = ""        # What would force them to act
    
    # Calibration from live data
    position_side: Optional[str] = None  # long / short / neutral
    position_size_usd: float = 0
    entry_price: float = 0
    liquidation_price: float = 0
    unrealized_pnl: float = 0
    
    # Behavioral params (MiroFish: activity_level, posts_per_hour, etc.)
    aggression: float = 0.5     # 0=passive, 1=aggressive
    herd_tendency: float = 0.5  # 0=contrarian, 1=follows crowd
    panic_threshold: float = 0.1  # price move % that triggers panic
    
    # Memory (MiroFish: zep long-term memory per agent)
    memory: List[str] = field(default_factory=list)
    
    def get_system_prompt(self, graph_context: str) -> str:
        """Generate the agent's system prompt for LLM reasoning."""
        return f"""You are {self.emoji} {self.name}, a {self.archetype} in the crypto derivatives market.

PERSONA: {self.persona}
TRADING STYLE: {self.trading_style}
RISK TOLERANCE: {self.risk_tolerance}
PAIN POINT: {self.pain_point}

CURRENT POSITION: {self.position_side or 'flat'} ${self.position_size_usd:,.0f}
ENTRY: ${self.entry_price:,.0f} | LIQUIDATION: ${self.liquidation_price:,.0f}
UNREALIZED PnL: ${self.unrealized_pnl:,.0f}

BEHAVIORAL PARAMETERS:
- Aggression: {self.aggression:.1f}/1.0
- Herd tendency: {self.herd_tendency:.1f}/1.0  
- Panic threshold: {self.panic_threshold*100:.0f}% move

MARKET CONTEXT:
{graph_context}

MEMORY OF PRIOR ROUNDS:
{chr(10).join(self.memory[-5:]) if self.memory else 'No prior rounds.'}

Each round, you must decide your action. Respond in JSON:
{{
    "thinking": "your internal reasoning (2-3 sentences)",
    "action": "hold | add | reduce | close | flip",
    "size_change_pct": 0-100,
    "reasoning_public": "what you'd say on a trading desk (1 sentence)",
    "confidence": 0.0-1.0,
    "market_impact": "your estimate of how your action affects the market"
}}"""
    
    def to_dict(self):
        return {
            "agent_id": self.agent_id, "name": self.name, "emoji": self.emoji,
            "archetype": self.archetype, "persona": self.persona,
            "position_side": self.position_side,
            "position_size_usd": self.position_size_usd,
            "aggression": self.aggression, "herd_tendency": self.herd_tendency,
            "panic_threshold": self.panic_threshold,
        }


# Default archetypes — used when LLM generation is not available
DEFAULT_ARCHETYPES = [
    {
        "archetype": "whale",
        "emoji": "🐋",
        "name_template": "The {stance} Whale",
        "persona_template": "A large-position holder with ${size}M at stake. {stance_desc}. Will defend position aggressively but has clear pain points.",
        "aggression": 0.7, "herd_tendency": 0.2, "panic_threshold": 0.15,
    },
    {
        "archetype": "market_maker",
        "emoji": "🤖",
        "name_template": "MM Desk",
        "persona_template": "Systematic market maker providing liquidity. Profits from spread, not direction. Pulls quotes when volatility exceeds risk limits. Has inventory to manage.",
        "aggression": 0.3, "herd_tendency": 0.1, "panic_threshold": 0.08,
    },
    {
        "archetype": "retail",
        "emoji": "🐑",
        "name_template": "Retail Crowd",
        "persona_template": "Aggregate retail behavior. Momentum-chasing, high leverage, panic-prone. Enters after moves, exits at worst time. Social media driven.",
        "aggression": 0.6, "herd_tendency": 0.9, "panic_threshold": 0.05,
    },
    {
        "archetype": "funding_arb",
        "emoji": "📊",
        "name_template": "Funding Arbitrageur",
        "persona_template": "Delta-neutral trader harvesting funding rate differentials. Only enters when funding is extreme. Stabilizing force in the market.",
        "aggression": 0.2, "herd_tendency": 0.0, "panic_threshold": 0.20,
    },
    {
        "archetype": "liquidation_engine",
        "emoji": "💀",
        "name_template": "Liquidation Cascade Engine",
        "persona_template": "Not a trader — represents the exchange liquidation mechanism. When positions breach margin, forced-closes them at market. Creates cascading selling/buying pressure.",
        "aggression": 1.0, "herd_tendency": 0.0, "panic_threshold": 0.0,
    },
]


def generate_profiles_from_graph(graph_context: str, whales: List[Dict] = None,
                                  llm_client=None) -> List[MarketAgentProfile]:
    """
    Generate agent profiles from market graph.
    
    MiroFish equivalent: OasisProfileGenerator.generate_profiles()
    - Reads entity nodes from Zep graph
    - LLM enriches each entity into a detailed persona
    - Returns list of OasisAgentProfile
    
    If llm_client is provided, uses LLM to generate rich personas (MiroFish approach).
    Otherwise falls back to template-based generation.
    """
    profiles = []
    whales = whales or []
    
    for i, archetype in enumerate(DEFAULT_ARCHETYPES):
        profile = MarketAgentProfile(
            agent_id=i,
            name=archetype["name_template"],
            emoji=archetype["emoji"],
            archetype=archetype["archetype"],
            persona=archetype["persona_template"],
            aggression=archetype["aggression"],
            herd_tendency=archetype["herd_tendency"],
            panic_threshold=archetype["panic_threshold"],
        )
        
        # Calibrate whale from live data
        if archetype["archetype"] == "whale" and whales:
            biggest = max(whales, key=lambda w: abs(w.get("size_usd", 0)))
            profile.position_side = biggest.get("side", "long")
            profile.position_size_usd = abs(biggest.get("size_usd", 0))
            profile.entry_price = biggest.get("entry_price", 0)
            profile.liquidation_price = biggest.get("liquidation_price", 0)
            profile.unrealized_pnl = biggest.get("unrealized_pnl", 0)
            stance = "Bearish" if profile.position_side == "short" else "Bullish"
            profile.name = f"The {stance} Whale"
            profile.persona = archetype["persona_template"].format(
                size=profile.position_size_usd/1e6, stance=stance,
                stance_desc=f"Currently {profile.position_side} with ${profile.unrealized_pnl:,.0f} unrealized PnL")
        
        # LLM persona enrichment (MiroFish pattern)
        if llm_client and archetype["archetype"] != "liquidation_engine":
            try:
                enrichment = llm_client.chat_json(messages=[
                    {"role": "system", "content": "You generate detailed trader personas for market simulation. Return JSON with: persona, trading_style, risk_tolerance, pain_point"},
                    {"role": "user", "content": f"Generate a detailed persona for this market participant:\nArchetype: {archetype['archetype']}\nCurrent market context:\n{graph_context}\n\nMake it specific to current conditions, not generic."}
                ])
                profile.persona = enrichment.get("persona", profile.persona)
                profile.trading_style = enrichment.get("trading_style", "")
                profile.risk_tolerance = enrichment.get("risk_tolerance", "moderate")
                profile.pain_point = enrichment.get("pain_point", "")
            except Exception:
                pass  # Fall back to template
        
        profiles.append(profile)
    
    return profiles
