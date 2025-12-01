# agents/planner.py
from typing import Any, Dict, Optional
import asyncio
import logging

from google.adk.agents import Agent

logger = logging.getLogger(__name__)

class PlannerAgent(Agent):
    model_config = {"extra": "allow"}  # allow dynamic attributes
    name: str = "planner"

    def __init__(self, name: Optional[str] = "planner"):
        super().__init__(name=name)

    async def on_message(self, message: Dict[str, Any], session: Dict[str, Any]):
        # Decide task details & normalize inputs
        logger.info("PlannerAgent received message: %s", message)
        params = message.get("params", {})
        # Choose default ticker if not provided
        ticker = params.get("symbol") or params.get("ticker") or "GOOGL"
        # Accept friendly names
        if ticker.lower() in ("google", "alphabet"):
            ticker = "GOOGL"
        # choose month/year if requested
        month = params.get("month") or "2025-10"  # yyyy-mm or fallback
        parsed = {"task": message.get("task", "fetch_stock"), "symbol": ticker, "month": month}
        logger.debug("PlannerAgent planned: %s", parsed)
        return {"planned": parsed}