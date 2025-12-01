# agents/supervisor.py
import asyncio
import logging
from typing import Any, Dict, List, Optional

from google.adk.agents import Agent

from agents.planner import PlannerAgent
from agents.data_worker import DataWorkerAgent
from agents.forecast_worker import ForecastWorkerAgent
from agents.critic import CriticAgent
from agents.reporter import ReporterAgent

logger = logging.getLogger(__name__)

class EnterpriseTeam:
    """
    Sequential runner + optional parallel mode.
    """
    def __init__(self, agents: List[Any], routing: str = "planner_first", max_turns: int = 10, name: Optional[str] = None):
        self.agents = agents
        self.routing = routing
        self.max_turns = max_turns
        self.name = name or "enterprise_team"

    async def _call_agent(self, agent, message, session):
        for method_name in ("on_message", "call", "run", "handle"):
            method = getattr(agent, method_name, None)
            if method is None:
                continue
            if asyncio.iscoroutinefunction(method):
                return await method(message, session)
            else:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: method(message, session))
        if hasattr(agent, "__call__"):
            method = agent.__call__
            if asyncio.iscoroutinefunction(method):
                return await method(message, session)
            else:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: method(message, session))
        return None

    async def call(self, message: Dict, session: Dict):
        current = message
        turns = 0
        agent_list = self.agents.copy()

        if self.routing == "planner_first":
            for i, a in enumerate(agent_list):
                if a.__class__.__name__.lower().startswith("planner"):
                    agent_list.insert(0, agent_list.pop(i))
                    break

        # parallel routing if configured
        if self.routing == "parallel":
            # run all agents on the same input in parallel and gather outputs
            tasks = [self._call_agent(a, current, session) for a in agent_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # merge results: later results overwrite earlier keys
            merged = {}
            for r in results:
                if isinstance(r, Exception):
                    logger.exception("Parallel agent error: %s", r)
                elif isinstance(r, dict):
                    merged.update(r)
            return merged

        for agent in agent_list:
            if turns >= self.max_turns:
                logger.info("Reached max_turns=%s for team %s", self.max_turns, self.name)
                break
            try:
                out = await self._call_agent(agent, current, session)
            except Exception as e:
                logger.exception("Agent %s crashed: %s", agent.__class__.__name__, e)
                current = {"error": str(e), "agent": agent.__class__.__name__}
                break
            if out is not None:
                # prefer dicts; otherwise store under 'result'
                if isinstance(out, dict):
                    current.update(out)
                else:
                    current = {"result": out, **current}
            turns += 1
        return current

# create instance
enterprise_team = EnterpriseTeam(
    agents=[
        PlannerAgent(name="planner"),
        DataWorkerAgent(name="data_worker"),
        ForecastWorkerAgent(name="forecast_worker"),
        CriticAgent(name="critic"),
        ReporterAgent(name="reporter"),
    ],
    routing="planner_first",
    max_turns=10,
    name="enterprise_team",
)

class SupervisorAgent(Agent):
    model_config = {"extra": "allow"}   # allow dynamic attributes like team
    team: Any = None                    # declare the field so Pydantic accepts it

    def __init__(self):
        super().__init__(name="supervisor")
        # bypass pydantic frozen-setting to attach team
        object.__setattr__(self, "team", enterprise_team)

    async def on_message(self, message, session):
        # expected input: {"task": "...", "params": {...}}
        return await self.team.call(message, session)