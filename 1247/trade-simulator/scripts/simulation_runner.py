"""
Market Simulation Runner — MiroFish Stage 3 Adaptation

MiroFish: simulation_runner.py + run_parallel_simulation.py
- Runs OASIS Twitter/Reddit environments in parallel
- Agents take social actions (post, like, reply) each round
- Actions logged to JSONL, state tracked per round
- Time-aware activity: agents more active during peak hours

Ours:
- Single "Market" environment (no social platforms needed)
- Agents take market actions (hold, add, reduce, close) each round
- Each agent LLM-reasons about their action given current state
- Price evolves based on aggregate agent actions + scenario shocks
- All actions logged with thinking traces
"""

import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .profile_generator import MarketAgentProfile
from .market_graph import MarketGraph


@dataclass
class AgentAction:
    """
    MiroFish equivalent: AgentAction dataclass
    Records what an agent did in a round with full reasoning trace.
    """
    round_num: int
    agent_id: int
    agent_name: str
    agent_emoji: str
    thinking: str        # Internal reasoning (MiroFish: agent's thought process)
    action: str          # hold, add, reduce, close, flip
    size_change_pct: float
    reasoning_public: str  # What they'd say publicly
    confidence: float
    market_impact: str
    price_before: float
    price_after: float
    
    def to_dict(self):
        return {
            "round": self.round_num, "agent": f"{self.agent_emoji} {self.agent_name}",
            "thinking": self.thinking, "action": self.action,
            "size_change_pct": self.size_change_pct,
            "public": self.reasoning_public, "confidence": self.confidence,
            "impact": self.market_impact,
            "price": f"${self.price_before:,.0f} -> ${self.price_after:,.0f}",
        }


@dataclass
class RoundResult:
    """State after each simulation round."""
    round_num: int
    price: float
    price_change_pct: float
    actions: List[AgentAction]
    cumulative_change_pct: float
    event_injected: Optional[str] = None
    
    def to_dict(self):
        return {
            "round": self.round_num, "price": self.price,
            "change_pct": f"{self.price_change_pct:+.2f}%",
            "cumulative_pct": f"{self.cumulative_change_pct:+.2f}%",
            "event": self.event_injected,
            "actions": [a.to_dict() for a in self.actions],
        }


@dataclass
class SimulationResult:
    """Complete simulation output."""
    scenario: str
    initial_price: float
    final_price: float
    total_rounds: int
    rounds: List[RoundResult]
    agent_profiles: List[Dict]
    graph_summary: str
    elapsed_seconds: float = 0
    
    def to_dict(self):
        return {
            "scenario": self.scenario,
            "price_path": f"${self.initial_price:,.0f} -> ${self.final_price:,.0f}",
            "total_change_pct": f"{(self.final_price/self.initial_price - 1)*100:+.2f}%",
            "rounds": [r.to_dict() for r in self.rounds],
            "agents": self.agent_profiles,
            "elapsed_seconds": self.elapsed_seconds,
        }


class MarketSimulation:
    """
    MiroFish equivalent: SimulationRunner + run_parallel_simulation
    
    Key MiroFish patterns adapted:
    1. Round-based loop with agent actions
    2. Time-aware activity (peak/dead hours -> scenario phases)
    3. Event injection mid-simulation
    4. Action logging to structured format
    5. State tracking per round
    """
    
    def __init__(self, graph: MarketGraph, agents: List[MarketAgentProfile],
                 llm_client=None, num_rounds: int = 6):
        self.graph = graph
        self.agents = agents
        self.llm_client = llm_client
        self.num_rounds = num_rounds
        self.action_log: List[AgentAction] = []
    
    def run(self, scenario: str, initial_price: float,
            scenario_shock_pct: float = 10.0,
            events: List[Dict] = None,
            progress_callback: Callable = None) -> SimulationResult:
        """
        Run the full simulation.
        
        MiroFish parallel: runs Twitter + Reddit simultaneously
        Ours: runs all agents sequentially per round (market is single env)
        """
        start = time.time()
        price = initial_price
        rounds = []
        events = events or []
        
        # Scenario shock schedule (MiroFish: timed events)
        # Distribute the total shock across rounds with front-loading
        shock_schedule = self._build_shock_schedule(scenario_shock_pct, self.num_rounds)
        
        graph_context = self.graph.get_full_context()
        
        for round_num in range(self.num_rounds):
            price_before = price
            
            # Check for event injection (MiroFish: dynamic event injection)
            event_text = None
            for evt in events:
                if evt.get("round") == round_num:
                    event_text = evt.get("description", "")
            
            # Apply scenario shock for this round
            base_shock = shock_schedule[round_num]
            
            # Each agent reasons and acts
            round_actions = []
            agent_impacts = []
            
            for agent in self.agents:
                action = self._agent_act(agent, round_num, price, base_shock,
                                         graph_context, event_text)
                round_actions.append(action)
                agent_impacts.append(self._calculate_impact(agent, action))
                
                # Update agent memory (MiroFish: zep memory update per round)
                agent.memory.append(
                    f"Round {round_num+1}: Price ${price:,.0f} ({base_shock:+.1f}% shock). "
                    f"I decided to {action.action}. {action.reasoning_public}"
                )
            
            # Aggregate impacts to determine actual price move
            total_impact = sum(agent_impacts)
            actual_move_pct = base_shock + total_impact
            price = price * (1 + actual_move_pct / 100)
            
            # Update actions with final price
            for action in round_actions:
                action.price_after = price
            
            cumulative = (price / initial_price - 1) * 100
            
            rounds.append(RoundResult(
                round_num=round_num + 1,
                price=price,
                price_change_pct=actual_move_pct,
                actions=round_actions,
                cumulative_change_pct=cumulative,
                event_injected=event_text,
            ))
            
            self.action_log.extend(round_actions)
            
            if progress_callback:
                progress_callback(round_num + 1, self.num_rounds, price)
        
        return SimulationResult(
            scenario=scenario,
            initial_price=initial_price,
            final_price=price,
            total_rounds=self.num_rounds,
            rounds=rounds,
            agent_profiles=[a.to_dict() for a in self.agents],
            graph_summary=self.graph.get_full_context(),
            elapsed_seconds=time.time() - start,
        )
    
    def _build_shock_schedule(self, total_shock: float, num_rounds: int) -> List[float]:
        """
        Distribute scenario shock across rounds.
        MiroFish equivalent: time-of-day activity multipliers.
        Front-loaded: biggest move in round 1, then diminishing.
        """
        if num_rounds <= 0:
            return []
        weights = [1.0 / (i + 1) for i in range(num_rounds)]
        total_w = sum(weights)
        return [total_shock * w / total_w for w in weights]
    
    def _agent_act(self, agent: MarketAgentProfile, round_num: int,
                   price: float, shock_pct: float, graph_context: str,
                   event: Optional[str] = None) -> AgentAction:
        """
        Get an agent's action for this round.
        
        MiroFish pattern: Each agent has an LLM call with their persona prompt.
        The agent "thinks" and decides their action.
        """
        if self.llm_client and agent.archetype != "liquidation_engine":
            try:
                system = agent.get_system_prompt(graph_context)
                user_msg = f"Round {round_num+1}: Price moved {shock_pct:+.2f}% this round."
                if event:
                    user_msg += f"\n\nBREAKING EVENT: {event}"
                user_msg += "\n\nWhat is your action? Respond in JSON format."
                
                response = self.llm_client.chat_json(messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg}
                ], temperature=0.7)
                
                return AgentAction(
                    round_num=round_num + 1,
                    agent_id=agent.agent_id,
                    agent_name=agent.name,
                    agent_emoji=agent.emoji,
                    thinking=response.get("thinking", ""),
                    action=response.get("action", "hold"),
                    size_change_pct=response.get("size_change_pct", 0),
                    reasoning_public=response.get("reasoning_public", ""),
                    confidence=response.get("confidence", 0.5),
                    market_impact=response.get("market_impact", "minimal"),
                    price_before=price,
                    price_after=price,  # Updated after all agents act
                )
            except Exception as e:
                pass  # Fall through to rule-based
        
        # Rule-based fallback (for liquidation engine or when no LLM)
        return self._rule_based_action(agent, round_num, price, shock_pct)
    
    def _rule_based_action(self, agent: MarketAgentProfile, round_num: int,
                           price: float, shock_pct: float) -> AgentAction:
        """Fallback rule-based action when LLM not available."""
        action = "hold"
        thinking = ""
        size_pct = 0
        
        if agent.archetype == "liquidation_engine":
            # Check if shock exceeds liquidation thresholds
            if abs(shock_pct) > 5:
                action = "liquidate"
                size_pct = min(abs(shock_pct) * 10, 80)
                thinking = f"Shock of {shock_pct:+.1f}% triggers margin calls"
            else:
                action = "hold"
                thinking = "No margin breaches this round"
        elif agent.archetype == "retail":
            if shock_pct > agent.panic_threshold * 100:
                action = "add"
                size_pct = 30
                thinking = "FOMO buying into momentum"
            elif shock_pct < -agent.panic_threshold * 100:
                action = "close"
                size_pct = 50
                thinking = "Panic selling"
            else:
                action = "hold"
                thinking = "Waiting for clearer signal"
        elif agent.archetype == "market_maker":
            if abs(shock_pct) > agent.panic_threshold * 100:
                action = "reduce"
                size_pct = 40
                thinking = "Pulling liquidity — vol too high"
            else:
                action = "hold"
                thinking = "Providing liquidity, spread is manageable"
        elif agent.archetype == "whale":
            if agent.position_side == "short" and shock_pct > 10:
                action = "close"
                size_pct = 60
                thinking = f"Covering short — move against me too large"
            elif agent.position_side == "long" and shock_pct < -10:
                action = "close"
                size_pct = 60
                thinking = f"Cutting long — pain threshold reached"
            else:
                action = "hold"
                thinking = "Position within tolerance"
        else:
            action = "hold"
            thinking = "No edge this round"
        
        return AgentAction(
            round_num=round_num + 1, agent_id=agent.agent_id,
            agent_name=agent.name, agent_emoji=agent.emoji,
            thinking=thinking, action=action, size_change_pct=size_pct,
            reasoning_public=thinking, confidence=0.5,
            market_impact="", price_before=price, price_after=price,
        )
    
    def _calculate_impact(self, agent: MarketAgentProfile, action: AgentAction) -> float:
        """Calculate price impact of an agent's action."""
        if action.action == "hold":
            return 0.0
        
        # Impact scales with position size and action aggressiveness
        base_impact = (action.size_change_pct / 100) * agent.aggression
        
        if action.action in ("add", "flip"):
            direction = 1.0  # Buying pressure
        elif action.action in ("reduce", "close", "liquidate"):
            direction = -1.0  # Selling pressure
            if agent.archetype == "liquidation_engine":
                direction *= 2.0  # Liquidations have outsized impact
        else:
            direction = 0.0
        
        # Flip direction based on position side
        if agent.position_side == "short":
            direction *= -1.0  # Short covering = buying
        
        return base_impact * direction * 0.5  # Dampen for realism
