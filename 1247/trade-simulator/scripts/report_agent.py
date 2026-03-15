"""
Report Agent — MiroFish Stage 4 Adaptation

MiroFish: report_agent.py
- ReACT pattern: Plan -> Think -> Act (use tools) -> Observe -> Reflect
- Plans report outline first, then generates each section
- Has tool access to query Zep graph during generation
- Multi-round reflection per section

Ours:
- Same ReACT pattern for market analysis
- Plans report structure, generates sections with tool queries
- Tools: market graph queries, agent action analysis, cascade detection
- Produces structured prediction report
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass  
class ReportSection:
    title: str
    content: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.5


@dataclass
class SimulationReport:
    title: str
    executive_summary: str
    sections: List[ReportSection]
    recommendations: List[str]
    risk_warnings: List[str]
    overall_confidence: float
    
    def to_text(self) -> str:
        parts = [f"# {self.title}\n", f"## Executive Summary\n{self.executive_summary}\n"]
        for s in self.sections:
            parts.append(f"## {s.title}\n{s.content}\n")
            if s.evidence:
                parts.append("Evidence:")
                for e in s.evidence:
                    parts.append(f"  - {e}")
                parts.append("")
        if self.recommendations:
            parts.append("## Recommendations")
            for r in self.recommendations:
                parts.append(f"- {r}")
        if self.risk_warnings:
            parts.append("\n## ⚠️ Risk Warnings")
            for w in self.risk_warnings:
                parts.append(f"- {w}")
        parts.append(f"\n_Overall confidence: {self.overall_confidence:.0%}_")
        return "\n".join(parts)
    
    def to_dict(self):
        return {
            "title": self.title, "summary": self.executive_summary,
            "sections": [{"title": s.title, "content": s.content,
                          "evidence": s.evidence, "confidence": s.confidence}
                         for s in self.sections],
            "recommendations": self.recommendations,
            "risk_warnings": self.risk_warnings,
            "confidence": self.overall_confidence,
        }


class ReportAgent:
    """
    MiroFish ReACT Report Agent adapted for market simulation.
    
    MiroFish pattern:
    1. Plan outline (LLM generates section structure)
    2. For each section: Think -> Act (query graph) -> Observe -> Reflect
    3. Final synthesis across all sections
    
    Tool set (MiroFish: InsightForge, PanoramaSearch, QuickSearch, Interview):
    - query_graph: Search market state graph
    - analyze_actions: Aggregate agent actions by type
    - detect_cascades: Find cascade sequences in simulation
    - calculate_pnl: Compute portfolio impact
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    def generate(self, simulation_result, graph, user_positions=None) -> SimulationReport:
        """Generate full report from simulation results."""
        sim = simulation_result
        
        # Tool functions (equivalent to MiroFish's Zep tools)
        tools = {
            "query_graph": lambda q: graph.query(q),
            "analyze_actions": lambda: self._analyze_actions(sim),
            "detect_cascades": lambda: self._detect_cascades(sim),
            "calculate_pnl": lambda: self._calculate_pnl(sim, user_positions or []),
        }
        
        if self.llm_client:
            return self._llm_report(sim, graph, tools, user_positions)
        else:
            return self._rule_based_report(sim, graph, tools, user_positions)
    
    def _llm_report(self, sim, graph, tools, positions) -> SimulationReport:
        """LLM-powered ReACT report generation."""
        # Gather tool outputs
        action_analysis = tools["analyze_actions"]()
        cascade_analysis = tools["detect_cascades"]()
        pnl_analysis = tools["calculate_pnl"]()
        
        prompt = f"""You are a market simulation report agent using ReACT reasoning.

SIMULATION: {sim.scenario}
PRICE PATH: ${sim.initial_price:,.0f} -> ${sim.final_price:,.0f} ({(sim.final_price/sim.initial_price-1)*100:+.1f}%)
ROUNDS: {sim.total_rounds}

MARKET STATE:
{graph.get_full_context()[:3000]}

AGENT ACTIONS ANALYSIS:
{action_analysis}

CASCADE ANALYSIS:
{cascade_analysis}

PORTFOLIO IMPACT:
{pnl_analysis}

Generate a prediction report in this JSON format:
{{
    "title": "report title",
    "executive_summary": "2-3 paragraph summary of key findings",
    "sections": [
        {{"title": "section name", "content": "detailed analysis", "evidence": ["evidence 1", "evidence 2"], "confidence": 0.7}},
    ],
    "recommendations": ["actionable recommendation 1", "..."],
    "risk_warnings": ["risk warning 1", "..."],
    "overall_confidence": 0.6
}}

Be specific. Cite agent behaviors. Identify turning points. Quantify risks."""
        
        try:
            data = self.llm_client.chat_json(messages=[
                {"role": "system", "content": "You are a quantitative market analyst generating simulation reports."},
                {"role": "user", "content": prompt}
            ], temperature=0.3, max_tokens=4096)
            
            sections = [ReportSection(title=s["title"], content=s["content"],
                        evidence=s.get("evidence", []), confidence=s.get("confidence", 0.5))
                        for s in data.get("sections", [])]
            
            return SimulationReport(
                title=data.get("title", sim.scenario),
                executive_summary=data.get("executive_summary", ""),
                sections=sections,
                recommendations=data.get("recommendations", []),
                risk_warnings=data.get("risk_warnings", []),
                overall_confidence=data.get("overall_confidence", 0.5),
            )
        except Exception as e:
            return self._rule_based_report(sim, graph, {"analyze_actions": lambda: "", 
                "detect_cascades": lambda: "", "calculate_pnl": lambda: ""}, positions)
    
    def _rule_based_report(self, sim, graph, tools, positions) -> SimulationReport:
        """Fallback rule-based report when no LLM."""
        total_chg = (sim.final_price / sim.initial_price - 1) * 100
        
        # Find key turning points
        turning_points = []
        for r in sim.rounds:
            aggressive = [a for a in r.actions if a.action in ("close", "liquidate", "flip")]
            if aggressive:
                turning_points.append(f"Round {r.round_num}: {', '.join(a.agent_emoji + ' ' + a.action for a in aggressive)}")
        
        # Portfolio impact
        pnl_text = self._calculate_pnl(sim, positions or [])
        
        sections = [
            ReportSection("Price Evolution",
                f"Price moved from ${sim.initial_price:,.0f} to ${sim.final_price:,.0f} ({total_chg:+.1f}%) over {sim.total_rounds} rounds.",
                [f"Round {r.round_num}: ${r.price:,.0f} ({r.price_change_pct:+.1f}%)" for r in sim.rounds]),
            ReportSection("Agent Behavior", self._analyze_actions(sim)),
            ReportSection("Cascade Analysis", self._detect_cascades(sim)),
            ReportSection("Portfolio Impact", pnl_text),
        ]
        
        if turning_points:
            sections.append(ReportSection("Turning Points", "\n".join(turning_points)))
        
        return SimulationReport(
            title=f"Simulation: {sim.scenario}",
            executive_summary=f"In the '{sim.scenario}' scenario, {sim.rounds[0].actions[0].agent_emoji if sim.rounds and sim.rounds[0].actions else ''} price moved {total_chg:+.1f}% from ${sim.initial_price:,.0f} to ${sim.final_price:,.0f}.",
            sections=sections,
            recommendations=[],
            risk_warnings=["This is a simulation, not a prediction. Actual markets are more complex."],
            overall_confidence=0.4,
        )
    
    def _analyze_actions(self, sim) -> str:
        """Analyze agent actions across all rounds."""
        by_agent = {}
        for r in sim.rounds:
            for a in r.actions:
                key = f"{a.agent_emoji} {a.agent_name}"
                by_agent.setdefault(key, []).append(a)
        
        lines = []
        for agent_name, actions in by_agent.items():
            action_seq = " -> ".join(a.action for a in actions)
            lines.append(f"{agent_name}: {action_seq}")
            # Key moments
            for a in actions:
                if a.action != "hold":
                    lines.append(f"  R{a.round_num}: {a.action} ({a.thinking[:80]})")
        return "\n".join(lines)
    
    def _detect_cascades(self, sim) -> str:
        """Detect liquidation cascades in simulation."""
        cascades = []
        for r in sim.rounds:
            liq_actions = [a for a in r.actions if a.action == "liquidate"]
            panic_actions = [a for a in r.actions if a.action == "close" and "panic" in a.thinking.lower()]
            if liq_actions or panic_actions:
                cascades.append(f"Round {r.round_num} ({r.price_change_pct:+.1f}%): "
                    f"{len(liq_actions)} liquidations, {len(panic_actions)} panic exits")
        
        if not cascades:
            return "No cascades detected — market absorbed the shock."
        return "CASCADES DETECTED:\n" + "\n".join(cascades)
    
    def _calculate_pnl(self, sim, positions) -> str:
        """Calculate PnL impact on user positions."""
        if not positions:
            return "No user positions to evaluate."
        
        total_chg = (sim.final_price / sim.initial_price - 1) * 100
        lines = []
        total_pnl = 0
        for pos in positions:
            side = pos.get("side", "long")
            size = pos.get("size", 0)
            entry = pos.get("entry_price", sim.initial_price)
            
            if side == "long":
                pnl = size * (sim.final_price - entry)
            else:
                pnl = size * (entry - sim.final_price)
            
            total_pnl += pnl
            pnl_pct = (pnl / (size * entry)) * 100 if size * entry > 0 else 0
            lines.append(f"  {pos.get('symbol','BTC')} {side} {size}: ${pnl:+,.0f} ({pnl_pct:+.1f}%)")
            
            liq = pos.get("liquidation_price", 0)
            if liq > 0:
                dist = abs(sim.final_price - liq) / sim.final_price * 100
                if dist < 10:
                    lines.append(f"    ⚠️ DANGER: Only {dist:.1f}% from liquidation at ${liq:,.0f}")
        
        lines.insert(0, f"Total PnL: ${total_pnl:+,.0f}")
        return "\n".join(lines)
