"""Download and save historical stock data as test fixtures.

Run this once to create fixture files that tests can use offline.
Uses AAPL data from July 2023 - January 2024 (stable, unchanging historical data).

Usage: python tests/generate_fixtures.py
"""

import sys
import os
import json
import pickle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
import numpy as np

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def download_and_save():
    os.makedirs(FIXTURE_DIR, exist_ok=True)

    stock = yf.Ticker("AAPL")

    # --- Price data ---
    daily_long = stock.history(start="2023-07-01", end="2024-01-31", interval="1d")
    daily_short = stock.history(start="2024-01-01", end="2024-01-31", interval="1d")

    # Synthesize intraday from short-term daily (yfinance doesn't keep old intraday)
    # Create 15-min bars by interpolating daily data
    intraday_rows = []
    for idx, row in daily_short.tail(5).iterrows():
        base_time = idx.replace(hour=9, minute=30)
        open_p, high_p, low_p, close_p = row["Open"], row["High"], row["Low"], row["Close"]
        vol = row["Volume"]
        n_bars = 26  # 6.5 hours / 15 min
        for i in range(n_bars):
            t = base_time + pd.Timedelta(minutes=15 * i)
            frac = i / (n_bars - 1)
            # Simulate price path: open -> high -> low -> close
            if frac < 0.3:
                price = open_p + (high_p - open_p) * (frac / 0.3)
            elif frac < 0.6:
                price = high_p + (low_p - high_p) * ((frac - 0.3) / 0.3)
            else:
                price = low_p + (close_p - low_p) * ((frac - 0.6) / 0.4)
            noise = np.random.normal(0, 0.1)
            intraday_rows.append({
                "Datetime": t,
                "Open": round(price + noise, 2),
                "High": round(price + abs(noise) + 0.2, 2),
                "Low": round(price - abs(noise) - 0.2, 2),
                "Close": round(price - noise * 0.5, 2),
                "Volume": int(vol / n_bars + np.random.randint(-5000, 5000)),
            })
    intraday = pd.DataFrame(intraday_rows).set_index("Datetime")

    # --- Build the data dict matching fetch_stock_data() output ---
    last_row = daily_short.iloc[-1]
    prev_row = daily_short.iloc[-2]

    data = {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "current_price": round(float(last_row["Close"]), 2),
        "previous_close": round(float(prev_row["Close"]), 2),
        "open_price": round(float(last_row["Open"]), 2),
        "day_high": round(float(last_row["High"]), 2),
        "day_low": round(float(last_row["Low"]), 2),
        "volume": int(last_row["Volume"]),
        "avg_volume": int(daily_short["Volume"].mean()),
        "market_cap": 2890000000000,
        "pe_ratio": 29.5,
        "week_52_high": round(float(daily_long["High"].max()), 2),
        "week_52_low": round(float(daily_long["Low"].min()), 2),
        "beta": 1.28,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        # DataFrames
        "intraday": intraday,
        "daily_short": daily_short,
        "daily_long": daily_long,
        # News (synthetic for testing)
        "news": [
            {
                "title": "Apple Vision Pro Pre-Orders Open This Friday",
                "publisher": "Bloomberg",
                "date": "2024-01-15",
                "summary": "Apple set to open pre-orders for Vision Pro headset, priced at $3,499."
            },
            {
                "title": "Apple Reports Record Services Revenue",
                "publisher": "Reuters",
                "date": "2024-01-12",
                "summary": "Apple's services segment continues to grow, hitting new quarterly record."
            },
            {
                "title": "iPhone Sales Slow in China Amid Competition",
                "publisher": "WSJ",
                "date": "2024-01-10",
                "summary": "Huawei and other Chinese brands cutting into Apple's market share."
            },
        ],
        "insider_buys": 2,
        "insider_sells": 5,
        "days_to_earnings": 12,
        "put_call_ratio": 0.85,
        "vix": 13.5,
        "spy_change_1d": 0.35,
    }

    # Save with pickle (preserves DataFrames)
    with open(os.path.join(FIXTURE_DIR, "aapl_data.pkl"), "wb") as f:
        pickle.dump(data, f)

    # Save a JSON-friendly summary for inspection
    summary = {k: v for k, v in data.items() if not isinstance(v, pd.DataFrame)}
    summary["daily_short_rows"] = len(daily_short)
    summary["daily_long_rows"] = len(daily_long)
    summary["intraday_rows"] = len(intraday)
    with open(os.path.join(FIXTURE_DIR, "aapl_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"Fixtures saved to {FIXTURE_DIR}/")
    print(f"  daily_long:  {len(daily_long)} rows ({daily_long.index[0].date()} to {daily_long.index[-1].date()})")
    print(f"  daily_short: {len(daily_short)} rows ({daily_short.index[0].date()} to {daily_short.index[-1].date()})")
    print(f"  intraday:    {len(intraday)} rows (synthesized)")
    print(f"  price:       ${data['current_price']}")


if __name__ == "__main__":
    download_and_save()
