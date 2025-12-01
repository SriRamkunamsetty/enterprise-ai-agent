# data/fetcher.py

import datetime
import asyncio
import yfinance as yf
from pathlib import Path

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

async def fetch_stock_data(symbol: str, start: str, end: str):
    """
    Fetch historical stock data asynchronously using yfinance.
    Automatically caches results.
    """

    # Cache file path
    cache_file = CACHE_DIR / f"{symbol}_{start}_{end}.csv"

    # If already cached → return cached version
    if cache_file.exists():
        return cache_file.read_text()

    # Fetch async via thread executor
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(
        None,
        lambda: yf.download(
            symbol,
            start=start,
            end=(datetime.date.fromisoformat(end) + datetime.timedelta(days=1)),
            progress=False
        )
    )

    if df is None or df.empty:
        raise ValueError(f"No data returned for {symbol}")

    # Save to cache
    df.to_csv(cache_file)

    return df.to_csv()