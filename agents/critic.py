# agents/critic.py
from typing import Any, Dict
import logging

from google.adk.agents import Agent

logger = logging.getLogger(__name__)

class CriticAgent(Agent):
    model_config = {"extra": "allow"}
    name: str = "critic"

    def __init__(self, name: str = "critic"):
        super().__init__(name=name)

    async def on_message(self, message: Dict[str, Any], session: Dict[str, Any]):
        # Basic sanity checks
        data = message.get("data")
        forecast = message.get("forecast")
        issues = []
        if data is None:
            issues.append("no_data")
        else:
            if len(data) < 2:
                issues.append("insufficient_history")
        if forecast is None:
            issues.append("no_forecast")
        ok = len(issues) == 0
        return {"planned": message.get("planned"), "ok": ok, "issues": issues, "data": data, "forecast": forecast}