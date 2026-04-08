"""Fetch comprehensive market data from Yahoo Finance for day trading analysis."""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_stock_data(ticker: str) -> dict:
    """Fetch comprehensive stock data including options, insider, earnings, and market context."""
    stock = yf.Ticker(ticker)

    # Company info
    try:
        info = stock.info
    except Exception:
        info = {}

    current_price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose", 0)

    # ── Price Data ──
    try:
        intraday = stock.history(period="5d", interval="15m")
    except Exception:
        intraday = pd.DataFrame()

    try:
        daily_short = stock.history(period="1mo", interval="1d")
    except Exception:
        daily_short = pd.DataFrame()

    try:
        daily_long = stock.history(period="6mo", interval="1d")
    except Exception:
        daily_long = pd.DataFrame()

    # ── News ──
    try:
        news = stock.news or []
    except Exception:
        news = []

    news_items = []
    for item in news[:10]:
        content = item.get("content", item) if isinstance(item, dict) else item
        if isinstance(content, dict):
            news_items.append({
                "title": content.get("title", ""),
                "publisher": content.get("provider", {}).get("displayName", "") if isinstance(content.get("provider"), dict) else "",
                "date": content.get("pubDate", ""),
                "summary": content.get("summary", ""),
            })

    # ── Insider Transactions ──
    insider_buys = 0
    insider_sells = 0
    try:
        insider = stock.insider_transactions
        if insider is not None and len(insider) > 0:
            recent = insider.head(20)
            for _, row in recent.iterrows():
                text = str(row.get("Text", "")).lower()
                if "purchase" in text or "buy" in text:
                    insider_buys += 1
                elif "sale" in text or "sell" in text:
                    insider_sells += 1
    except Exception:
        pass

    # ── Earnings Date ──
    days_to_earnings = None
    try:
        earnings = stock.earnings_dates
        if earnings is not None and len(earnings) > 0:
            future = earnings[earnings.index >= pd.Timestamp.now(tz=earnings.index.tz)]
            if len(future) > 0:
                next_earnings = future.index[-1]
                days_to_earnings = (next_earnings - pd.Timestamp.now(tz=next_earnings.tz)).days
    except Exception:
        pass

    # ── Options Data (Put/Call Ratio) ──
    put_call_ratio = None
    try:
        if stock.options:
            nearest_exp = stock.options[0]
            chain = stock.option_chain(nearest_exp)
            total_call_vol = chain.calls["volume"].sum()
            total_put_vol = chain.puts["volume"].sum()
            if total_call_vol > 0:
                put_call_ratio = round(total_put_vol / total_call_vol, 2)
    except Exception:
        pass

    # ── Market Context (VIX + S&P 500) ──
    vix_level = None
    spy_change_1d = None
    try:
        vix = yf.Ticker("^VIX")
        vix_info = vix.info
        vix_level = vix_info.get("regularMarketPrice") or vix_info.get("previousClose")
    except Exception:
        pass

    try:
        spy = yf.Ticker("SPY")
        spy_hist = spy.history(period="5d", interval="1d")
        if len(spy_hist) >= 2:
            spy_change_1d = round(
                (spy_hist["Close"].iloc[-1] - spy_hist["Close"].iloc[-2]) / spy_hist["Close"].iloc[-2] * 100, 2
            )
    except Exception:
        pass

    return {
        "ticker": ticker.upper(),
        "company_name": info.get("shortName", ticker.upper()),
        "current_price": current_price,
        "previous_close": info.get("previousClose", 0),
        "open_price": info.get("open") or info.get("regularMarketOpen", 0),
        "day_high": info.get("dayHigh") or info.get("regularMarketDayHigh", 0),
        "day_low": info.get("dayLow") or info.get("regularMarketDayLow", 0),
        "volume": info.get("volume") or info.get("regularMarketVolume", 0),
        "avg_volume": info.get("averageVolume", 0),
        "market_cap": info.get("marketCap", 0),
        "pe_ratio": info.get("trailingPE", None),
        "week_52_high": info.get("fiftyTwoWeekHigh", 0),
        "week_52_low": info.get("fiftyTwoWeekLow", 0),
        "beta": info.get("beta", None),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        # Price data
        "intraday": intraday,
        "daily_short": daily_short,
        "daily_long": daily_long,
        # News
        "news": news_items,
        # Insider
        "insider_buys": insider_buys,
        "insider_sells": insider_sells,
        # Earnings
        "days_to_earnings": days_to_earnings,
        # Options
        "put_call_ratio": put_call_ratio,
        # Market context
        "vix": vix_level,
        "spy_change_1d": spy_change_1d,
    }
