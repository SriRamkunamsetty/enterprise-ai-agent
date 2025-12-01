# tools/finance_tool.py
from typing import Any, Dict, Optional
import yfinance as yf

class FinanceTool:
    def __init__(self):
        pass

    def get_history(self, symbol: str, start: str, end: str):
        # returns dict/list similar to DataWorker
        df = yf.download(symbol, start=start, end=end, progress=False)
        if df is None or df.empty:
            return []
        return df.reset_index()[["Date","Open","High","Low","Close","Volume"]].to_dict(orient="records")