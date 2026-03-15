"""
MiroFish Market Simulation Engine — All 5 Stages

Orchestrates the complete MiroFish pipeline adapted for trading:
1. Graph Construction  (market_graph.py)
2. Profile Generation  (profile_generator.py)
3. Simulation Run      (simulation_runner.py)
4. Report Generation   (report_agent.py)
5. Interview System    (interview.py)

Usage:
    echo '{"scenario": "BTC pumps 10%", "symbol": "BTC", ...}' | \
        python3 -m skills.trade-simulator.scripts.mirofish_engine

    OR import and use programmatically
"""

import os
import sys
import json
import re
import time
from typing import Dict, Any, List, Optional

# Add workspace to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from skills.trade_simulator.scripts.market_graph import MarketGraph, build_market_graph
from skills.trade_simulator.scripts.profile_generator import MarketAgentProfile, generate_profiles_from_graph
from skills.trade_simulator.scripts.simulation_runner import MarketSimulation, SimulationResult
from skills.trade_simulator.scripts.report_agent import ReportAgent, SimulationReport
from skills.trade_simulator.scripts.interview import InterviewSystem


class LLMClient:
    """
    Minimal LLM client matching MiroFish's LLMClient interface.
    Uses OpenAI-compatible API (same as MiroFish's backend/app/utils/llm_client.py).
    """
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        from openai import OpenAI
        import httpx
        self.api_key = api_key or os.environ.get("LLM_API_KEY") or os.environ.get("OPENROUTER_API_KEY", "")
        self.base_url = base_url or os.environ.get("LLM_BASE_URL") or "https://openrouter.ai/api/v1"
        self.model = model or os.environ.get("LLM_MODEL_NAME") or "anthropic/claude-sonnet-4"
        # Use proxy if available (MiroFish uses direct; we route through sc-proxy)
        proxy_host = os.environ.get("PROXY_HOST", "")
        proxy_port = os.environ.get("PROXY_PORT", "")
        ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE", "")
        http_client = None
        if proxy_host and proxy_port:
            proxy_url = f"http://[{proxy_host}]:{proxy_port}"
            http_client = httpx.Client(proxy=proxy_url, verify=ca_bundle if ca_bundle else True)
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, http_client=http_client)
    
    def chat(self, messages, temperature=0.7, max_tokens=4096):
        response = self.client.chat.completions.create(
            model=self.model, messages=messages,
            temperature=temperature, max_tokens=max_tokens)
        content = response.choices[0].message.content
        # MiroFish pattern: strip <think> tags from reasoning models
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content
    
    def chat_json(self, messages, temperature=0.3, max_tokens=4096):
        # Add JSON instruction
        if messages:
            messages = list(messages)
            messages[-1] = dict(messages[-1])
            messages[-1]["content"] = messages[-1]["content"] + "\n\nRespond with valid JSON only. No markdown code blocks."
        response = self.chat(messages, temperature, max_tokens)
        # Clean markdown fences
        cleaned = response.strip()
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        return json.loads(cleaned)


class MiroFishEngine:
    """
    Complete 5-stage pipeline orchestrator.
    
    MiroFish equivalent: The Flask app + simulation_manager.py
    that coordinates graph building, profile generation, simulation,
    report generation, and interviews.
    """
    
    def __init__(self, use_llm: bool = True):
        self.llm_client = None
        if use_llm:
            try:
                self.llm_client = LLMClient()
            except Exception as e:
                print(f"[WARN] LLM not available: {e}. Using rule-based mode.", file=sys.stderr)
        
        self.graph: Optional[MarketGraph] = None
        self.agents: List[MarketAgentProfile] = []
        self.simulation_result: Optional[SimulationResult] = None
        self.report: Optional[SimulationReport] = None
        self.interview_system: Optional[InterviewSystem] = None
    
    def run_full_pipeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all 5 MiroFish stages.
        
        Config:
            scenario: str - Natural language scenario description
            symbol: str - Asset symbol (BTC, ETH, etc.)
            shock_pct: float - Scenario price shock percentage
            num_rounds: int - Simulation rounds (default 6)
            market_data: dict - Live market data (price, oi, funding, etc.)
            user_positions: list - User's current positions
            events: list - Mid-simulation event injections
        """
        scenario = config.get("scenario", "Unknown scenario")
        symbol = config.get("symbol", "BTC")
        
        results = {"scenario": scenario, "symbol": symbol, "stages": {}}
        t0 = time.time()
        
        # === STAGE 1: Graph Construction ===
        print(f"[Stage 1/5] Building market state graph...", file=sys.stderr)
        market_data = config.get("market_data", {})
        market_data["symbol"] = symbol
        self.graph = build_market_graph(market_data)
        results["stages"]["graph"] = {
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "built_at": self.graph.built_at,
        }
        print(f"  -> {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges", file=sys.stderr)
        
        # === STAGE 2: Profile Generation ===
        print(f"[Stage 2/5] Generating agent profiles...", file=sys.stderr)
        whales = market_data.get("whales", [])
        graph_context = self.graph.get_full_context()
        self.agents = generate_profiles_from_graph(
            graph_context=graph_context,
            whales=whales,
            llm_client=self.llm_client
        )
        results["stages"]["profiles"] = [a.to_dict() for a in self.agents]
        print(f"  -> {len(self.agents)} agents created", file=sys.stderr)
        
        # === STAGE 3: Simulation ===
        print(f"[Stage 3/5] Running simulation ({config.get('num_rounds', 6)} rounds)...", file=sys.stderr)
        sim = MarketSimulation(
            graph=self.graph,
            agents=self.agents,
            llm_client=self.llm_client,
            num_rounds=config.get("num_rounds", 6),
        )
        self.simulation_result = sim.run(
            scenario=scenario,
            initial_price=market_data.get("price", 0),
            scenario_shock_pct=config.get("shock_pct", 10.0),
            events=config.get("events", []),
            progress_callback=lambda r, t, p: print(
                f"  Round {r}/{t}: ${p:,.0f}", file=sys.stderr),
        )
        results["stages"]["simulation"] = self.simulation_result.to_dict()
        print(f"  -> Final price: ${self.simulation_result.final_price:,.0f}", file=sys.stderr)
        
        # === STAGE 4: Report Generation ===
        print(f"[Stage 4/5] Generating ReACT report...", file=sys.stderr)
        reporter = ReportAgent(llm_client=self.llm_client)
        self.report = reporter.generate(
            simulation_result=self.simulation_result,
            graph=self.graph,
            user_positions=config.get("user_positions", []),
        )
        results["stages"]["report"] = self.report.to_dict()
        results["report_text"] = self.report.to_text()
        print(f"  -> Report: {len(self.report.sections)} sections", file=sys.stderr)
        
        # === STAGE 5: Interview System Ready ===
        print(f"[Stage 5/5] Interview system initialized.", file=sys.stderr)
        self.interview_system = InterviewSystem(
            agents=self.agents,
            simulation_result=self.simulation_result,
            llm_client=self.llm_client,
        )
        results["stages"]["interview"] = {
            "available_agents": self.interview_system.list_agents(),
            "status": "ready",
        }
        
        results["elapsed_seconds"] = time.time() - t0
        results["llm_powered"] = self.llm_client is not None
        
        print(f"\n✅ All 5 stages complete in {results['elapsed_seconds']:.1f}s", file=sys.stderr)
        return results
    
    def interview(self, agent_query: str, question: str) -> Dict:
        """Interview an agent post-simulation."""
        if not self.interview_system:
            return {"error": "Run simulation first"}
        result = self.interview_system.interview(agent_query, question)
        return result.to_dict()


def main():
    """CLI entry point — reads config from stdin or file."""
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)
    
    engine = MiroFishEngine(use_llm=config.get("use_llm", True))
    results = engine.run_full_pipeline(config)
    
    # Output results
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
