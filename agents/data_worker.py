# agents/data_worker.py
from typing import Any, Dict
import logging
import datetime
import calendar

from google.adk.agents import Agent

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

class DataWorkerAgent(Agent):
    model_config = {"extra": "allow"}
    name: str = "data_worker"

    def __init__(self, name: str = "data_worker"):
        super().__init__(name=name)

    async def on_message(self, message: Dict[str, Any], session: Dict[str, Any]):
        # Expect message like {"planned": {"symbol": "GOOGL", "month": "2025-10", ...}}
        planned = message.get("planned", message)
        symbol = planned.get("symbol", "GOOGL")
        month = planned.get("month", "2025-10")
        # parse month into start/end
        year, mon = month.split("-")
        year_i, mon_i = int(year), int(mon)
        start = datetime.date(year_i, mon_i, 1)
        last_day = calendar.monthrange(year_i, mon_i)[1]
        end = datetime.date(year_i, mon_i, last_day)
        logger.info("Fetching %s data from %s to %s", symbol, start, end)
        # yfinance can be blocking; run in thread pool
        loop = __import__("asyncio").get_event_loop()
        df = await loop.run_in_executor(None, lambda: yf.download(symbol, start=start, end=end + datetime.timedelta(days=1), progress=False))
        if df is None or df.empty:
            logger.warning("No data returned for %s in %s", symbol, month)
            return {"planned": planned, "data": None}
        # reduce to CSV-friendly; reset index
        df = df.reset_index()
        # Keep only Date, Open, High, Low, Close, Volume
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
        # Convert to iso dates and simple list of rows
        rows = df.to_dict(orient="records")
        logger.debug("Fetched %d rows", len(rows))
        return {"planned": planned, "data": rows}