"""
Post-Simulation Interview System — MiroFish Stage 5 Adaptation

MiroFish: zep_tools.py InterviewResult + simulation_runner.py interview mode
- After simulation completes, environment stays alive
- User can interview any agent by ID
- Agent responds from their accumulated memory + persona
- Supports both single and batch interviews

Ours:
- After simulation, agent profiles + memory are preserved
- User can ask any agent about their decisions
- Agent responds using their persona + full round memory
- Supports follow-up questions
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .profile_generator import MarketAgentProfile


@dataclass
class InterviewResult:
    """MiroFish equivalent: InterviewResult dataclass"""
    agent_name: str
    agent_emoji: str 
    question: str
    response: str
    confidence: float = 0.5
    
    def to_dict(self):
        return {
            "agent": f"{self.agent_emoji} {self.agent_name}",
            "question": self.question,
            "response": self.response,
            "confidence": self.confidence,
        }


class InterviewSystem:
    """
    Post-simulation interview system.
    
    MiroFish pattern: 
    - Simulation completes but environment persists
    - IPC commands send interview requests to running simulation
    - Agent reconstructs context from Zep memory and responds
    
    Our adaptation:
    - Simulation results + agent profiles kept in memory
    - LLM generates responses from agent persona + accumulated memory
    - No IPC needed (we're in the same process)
    """
    
    def __init__(self, agents: List[MarketAgentProfile], 
                 simulation_result=None, llm_client=None):
        self.agents = {a.agent_id: a for a in agents}
        self.agents_by_name = {}
        for a in agents:
            self.agents_by_name[a.name.lower()] = a
            self.agents_by_name[a.archetype.lower()] = a
            self.agents_by_name[a.emoji] = a
        self.simulation_result = simulation_result
        self.llm_client = llm_client
        self.conversation_history: Dict[int, List[Dict]] = {}
    
    def list_agents(self) -> List[Dict]:
        """List all agents available for interview."""
        return [{"id": a.agent_id, "name": f"{a.emoji} {a.name}",
                 "archetype": a.archetype, "position": a.position_side,
                 "rounds_memory": len(a.memory)}
                for a in self.agents.values()]
    
    def find_agent(self, query: str) -> Optional[MarketAgentProfile]:
        """Find agent by name, archetype, emoji, or ID."""
        q = query.lower().strip()
        # Try exact match
        if q in self.agents_by_name:
            return self.agents_by_name[q]
        # Try substring
        for key, agent in self.agents_by_name.items():
            if q in key:
                return agent
        # Try ID
        try:
            return self.agents.get(int(q))
        except (ValueError, TypeError):
            pass
        return None
    
    def interview(self, agent_query: str, question: str) -> InterviewResult:
        """
        Interview a simulated agent.
        
        MiroFish: sends IPC CommandType.INTERVIEW to running simulation
        Ours: reconstructs agent context and generates LLM response
        """
        agent = self.find_agent(agent_query)
        if not agent:
            return InterviewResult(
                agent_name="System", agent_emoji="❌",
                question=question,
                response=f"Agent '{agent_query}' not found. Available: {', '.join(a.emoji + ' ' + a.name for a in self.agents.values())}",
            )
        
        if self.llm_client:
            return self._llm_interview(agent, question)
        else:
            return self._memory_interview(agent, question)
    
    def _llm_interview(self, agent: MarketAgentProfile, question: str) -> InterviewResult:
        """LLM-powered interview (MiroFish approach)."""
        # Build conversation history
        history = self.conversation_history.get(agent.agent_id, [])
        
        system_prompt = f"""You are {agent.emoji} {agent.name}, being interviewed after a market simulation.

YOUR PERSONA: {agent.persona}
YOUR POSITION: {agent.position_side} ${agent.position_size_usd:,.0f}
YOUR TRADING STYLE: {agent.trading_style}

YOUR MEMORY OF THE SIMULATION:
{chr(10).join(agent.memory) if agent.memory else 'No simulation memory.'}

Answer as this character would — in first person, with their personality and biases.
Be specific about your reasoning during the simulation.
If asked about a decision, explain your thinking process from that round."""
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": question})
        
        try:
            response = self.llm_client.chat(messages=messages, temperature=0.7)
            
            # Update conversation history
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": response})
            self.conversation_history[agent.agent_id] = history
            
            return InterviewResult(
                agent_name=agent.name, agent_emoji=agent.emoji,
                question=question, response=response, confidence=0.7,
            )
        except Exception as e:
            return self._memory_interview(agent, question)
    
    def _memory_interview(self, agent: MarketAgentProfile, question: str) -> InterviewResult:
        """Fallback: answer from memory without LLM."""
        q = question.lower()
        
        relevant_memories = []
        for mem in agent.memory:
            if any(kw in q for kw in ["why", "decision", "round", "action", "think"]):
                relevant_memories.append(mem)
        
        if not relevant_memories:
            relevant_memories = agent.memory[-3:] if agent.memory else ["No simulation memory available."]
        
        response = f"[{agent.emoji} {agent.name} — {agent.archetype}]\n\n"
        response += f"My position: {agent.position_side} ${agent.position_size_usd:,.0f}\n\n"
        response += "My recollection:\n"
        for mem in relevant_memories:
            response += f"  - {mem}\n"
        
        return InterviewResult(
            agent_name=agent.name, agent_emoji=agent.emoji,
            question=question, response=response, confidence=0.3,
        )
    
    def batch_interview(self, question: str) -> List[InterviewResult]:
        """
        Interview ALL agents with the same question.
        MiroFish: batch interview mode via IPC.
        """
        return [self.interview(str(agent_id), question) for agent_id in self.agents]
