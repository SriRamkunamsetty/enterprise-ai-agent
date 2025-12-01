# agents/forecast_worker.py
from typing import Any, Dict
import logging
import pandas as pd

from google.adk.agents import Agent

logger = logging.getLogger(__name__)

class ForecastWorkerAgent(Agent):
    model_config = {"extra": "allow"}
    name: str = "forecast_worker"

    def __init__(self, name: str = "forecast_worker"):
        super().__init__(name=name)

    async def on_message(self, message: Dict[str, Any], session: Dict[str, Any]):
        payload = message.get("data")
        if not payload:
            return {"planned": message.get("planned"), "forecast": None}
        # convert to DataFrame
        df = pd.DataFrame(payload)
        if "Close" not in df.columns:
            return {"planned": message.get("planned"), "forecast": None}
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        # simple moving averages as naive forecast features
        df["SMA_3"] = df["Close"].rolling(window=3, min_periods=1).mean()
        df["SMA_7"] = df["Close"].rolling(window=7, min_periods=1).mean()
        # last row as forecast entry
        last = df.iloc[-1].to_dict()
        return {"planned": message.get("planned"), "forecast": {"last": last}}