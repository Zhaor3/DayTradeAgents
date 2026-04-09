"""Accuracy test - check if indicator signals correctly predicted past price movements.

Downloads historical data for well-known stocks at specific past dates, computes
indicators, and checks if the signals matched what actually happened next.

This tests the QUALITY of the indicator engine, not just that it runs.

Usage: py tests/test_accuracy.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from tradingagent.data.indicators import (
    calc_rsi, calc_macd, calc_bollinger_bands, calc_atr,
    calc_signal_alignment, compute_all_indicators,
    detect_ema_cross,
)

console = Console()


# ── Test Cases: known stock movements ──
# Each case: fetch data ending at 'analysis_date', then check what happened
# in the 'future_days' after that date.
TEST_CASES = [
    {
        "ticker": "AAPL",
        "name": "AAPL post-earnings rally (Jan 2024)",
        "analysis_end": "2024-01-26",
        "future_check": "2024-02-09",  # ~10 trading days later
        "expected_direction": "up",  # AAPL rallied after Q1 2024 earnings
    },
    {
        "ticker": "NVDA",
        "name": "NVDA AI boom surge (Feb 2024)",
        "analysis_end": "2024-02-20",
        "future_check": "2024-03-08",
        "expected_direction": "up",  # NVDA surged on AI demand
    },
    {
        "ticker": "MSFT",
        "name": "MSFT steady climb (Mar 2024)",
        "analysis_end": "2024-03-01",
        "future_check": "2024-03-15",
        "expected_direction": "up",
    },
    {
        "ticker": "TSLA",
        "name": "TSLA decline (Jan 2024)",
        "analysis_end": "2024-01-15",
        "future_check": "2024-01-31",
        "expected_direction": "down",  # TSLA dropped on delivery concerns
    },
    {
        "ticker": "META",
        "name": "META post-earnings surge (Feb 2024)",
        "analysis_end": "2024-01-31",
        "future_check": "2024-02-14",
        "expected_direction": "up",  # META surged on earnings + dividend
    },
    {
        "ticker": "GOOGL",
        "name": "GOOGL choppy period (Jan 2024)",
        "analysis_end": "2024-01-19",
        "future_check": "2024-02-02",
        "expected_direction": "up",
    },
    {
        "ticker": "AMZN",
        "name": "AMZN earnings rally (Feb 2024)",
        "analysis_end": "2024-01-31",
        "future_check": "2024-02-14",
        "expected_direction": "up",
    },
    {
        "ticker": "AMD",
        "name": "AMD AI chip demand (Feb 2024)",
        "analysis_end": "2024-02-01",
        "future_check": "2024-02-15",
        "expected_direction": "down",  # AMD dipped after earnings despite AI hype
    },
]


def build_data_dict(ticker: str, end_date: str) -> dict:
    """Build a data dict similar to fetch_stock_data() but for a historical date."""
    stock = yf.Ticker(ticker)
    end = pd.Timestamp(end_date)
    start_long = end - pd.Timedelta(days=200)
    start_short = end - pd.Timedelta(days=40)

    daily_long = stock.history(start=start_long.strftime("%Y-%m-%d"),
                               end=end.strftime("%Y-%m-%d"), interval="1d")
    daily_short = stock.history(start=start_short.strftime("%Y-%m-%d"),
                                end=end.strftime("%Y-%m-%d"), interval="1d")

    if len(daily_long) < 20 or len(daily_short) < 5:
        return None

    # Flatten MultiIndex if present
    for df in [daily_long, daily_short]:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

    last = daily_short.iloc[-1]
    prev = daily_short.iloc[-2] if len(daily_short) >= 2 else last

    # Synthesize minimal intraday from last 5 days of short data
    intraday_rows = []
    for day_idx in range(max(-5, -len(daily_short)), 0):
        day = daily_short.iloc[day_idx]
        base_time = daily_short.index[day_idx]
        if hasattr(base_time, 'replace'):
            base_time = base_time.replace(hour=9, minute=30)
        for i in range(26):
            t = base_time + pd.Timedelta(minutes=15 * i)
            frac = i / 25
            price = float(day["Open"]) + (float(day["Close"]) - float(day["Open"])) * frac
            noise = np.random.normal(0, 0.2)
            intraday_rows.append({
                "Datetime": t,
                "Open": round(price + noise, 2),
                "High": round(price + abs(noise) + 0.3, 2),
                "Low": round(price - abs(noise) - 0.3, 2),
                "Close": round(price - noise * 0.5, 2),
                "Volume": max(1, int(float(day["Volume"]) / 26 + np.random.randint(-5000, 5000))),
            })
    intraday = pd.DataFrame(intraday_rows).set_index("Datetime")

    return {
        "ticker": ticker,
        "company_name": ticker,
        "current_price": round(float(last["Close"]), 2),
        "previous_close": round(float(prev["Close"]), 2),
        "open_price": round(float(last["Open"]), 2),
        "day_high": round(float(last["High"]), 2),
        "day_low": round(float(last["Low"]), 2),
        "volume": int(last["Volume"]),
        "avg_volume": int(daily_short["Volume"].mean()),
        "market_cap": 0,
        "pe_ratio": None,
        "week_52_high": round(float(daily_long["High"].max()), 2),
        "week_52_low": round(float(daily_long["Low"].min()), 2),
        "beta": None,
        "sector": "Technology",
        "industry": "N/A",
        "intraday": intraday,
        "daily_short": daily_short,
        "daily_long": daily_long,
        "news": [],
        "insider_buys": 0,
        "insider_sells": 0,
        "days_to_earnings": None,
        "put_call_ratio": None,
        "vix": None,
        "spy_change_1d": None,
    }


def get_future_price(ticker: str, analysis_end: str, future_check: str) -> float:
    """Get the closing price on the future check date."""
    stock = yf.Ticker(ticker)
    # Add a few buffer days in case future_check falls on a weekend
    end_buf = (pd.Timestamp(future_check) + pd.Timedelta(days=5)).strftime("%Y-%m-%d")
    hist = stock.history(start=future_check, end=end_buf, interval="1d")
    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = hist.columns.get_level_values(0)
    if len(hist) > 0:
        return round(float(hist["Close"].iloc[0]), 2)
    return None


def interpret_signal(indicators: dict) -> str:
    """Convert indicator signals to a simple direction prediction.

    Strategy: trend-following with momentum confirmation.
    - MACD histogram = current momentum direction (primary)
    - EMA cross = short-term trend (secondary)
    - ADX = trend strength (confidence filter)
    - Price vs moving averages = trend context
    - RSI extremes only used as WARNING, not as contrarian triggers
    """
    votes = []  # (signal_name, direction, weight)

    # 1. MACD histogram: primary momentum signal
    macd_hist = indicators.get("macd_histogram")
    if macd_hist is not None:
        if macd_hist > 0:
            votes.append(("MACD", "up", 3))
        else:
            votes.append(("MACD", "down", 3))

    # 2. EMA cross: trend direction
    ema_cross = indicators.get("ema_cross")
    if ema_cross in ("golden_cross", "bullish"):
        votes.append(("EMA", "up", 2))
    elif ema_cross in ("death_cross", "bearish"):
        votes.append(("EMA", "down", 2))

    # 3. Price vs key moving averages (trend context)
    price = indicators.get("_current_price", 0)
    sma_20 = indicators.get("sma_20")
    sma_50 = indicators.get("sma_50")
    if price and sma_20:
        if price > sma_20:
            votes.append(("SMA20", "up", 1))
        else:
            votes.append(("SMA20", "down", 1))
    if price and sma_50:
        if price > sma_50:
            votes.append(("SMA50", "up", 1))
        else:
            votes.append(("SMA50", "down", 1))

    # 4. Short-term price momentum (5-day change)
    change_5d = indicators.get("change_5d")
    if change_5d is not None:
        if change_5d > 2:
            votes.append(("5dMomentum", "up", 2))
        elif change_5d < -2:
            votes.append(("5dMomentum", "down", 2))

    # 5. Volume confirmation - high volume confirms the current trend
    vol_ratio = indicators.get("volume_ratio")
    if vol_ratio is not None and vol_ratio > 1.3:
        # High volume amplifies the dominant direction
        change_1d = indicators.get("change_1d", 0)
        if change_1d and change_1d > 0:
            votes.append(("VolConfirm", "up", 1))
        elif change_1d and change_1d < 0:
            votes.append(("VolConfirm", "down", 1))

    # Tally votes
    if not votes:
        return "neutral"

    up_weight = sum(w for _, d, w in votes if d == "up")
    down_weight = sum(w for _, d, w in votes if d == "down")
    total_weight = up_weight + down_weight

    if total_weight == 0:
        return "neutral"

    net = up_weight - down_weight
    # Need >25% net advantage to make a call
    threshold = total_weight * 0.25
    if net > threshold:
        return "up"
    elif net < -threshold:
        return "down"
    return "neutral"


def run_accuracy_test():
    """Run accuracy tests on historical data."""
    console.print()
    console.print(Panel(
        "[bold]Indicator Accuracy Test[/bold]\n"
        "Testing if technical indicators correctly predicted past stock movements.\n"
        "Uses real historical data from yfinance.",
        title="DayTradeAgent Accuracy Backtest",
        border_style="cyan",
    ))

    results = []

    for i, case in enumerate(TEST_CASES):
        console.print(f"\n[bold cyan][{i+1}/{len(TEST_CASES)}][/bold cyan] {case['name']}...")

        try:
            # Build historical data
            data = build_data_dict(case["ticker"], case["analysis_end"])
            if data is None:
                console.print(f"  [yellow]Skipped - insufficient data[/yellow]")
                results.append({"case": case, "status": "skipped", "reason": "no data"})
                continue

            # Compute indicators at analysis date
            indicators = compute_all_indicators(data)

            # Get what actually happened
            future_price = get_future_price(case["ticker"], case["analysis_end"], case["future_check"])
            if future_price is None:
                console.print(f"  [yellow]Skipped - no future price data[/yellow]")
                results.append({"case": case, "status": "skipped", "reason": "no future data"})
                continue

            analysis_price = data["current_price"]
            actual_change_pct = round((future_price - analysis_price) / analysis_price * 100, 2)
            actual_direction = "up" if future_price > analysis_price else "down"

            # What did our indicators predict?
            predicted_direction = interpret_signal(indicators)
            correct = (predicted_direction == actual_direction) or predicted_direction == "neutral"
            exact_match = predicted_direction == actual_direction

            signal_score = indicators.get("signal_score", "N/A")
            rsi = indicators.get("rsi_14", "N/A")
            macd_hist = indicators.get("macd_histogram", "N/A")

            status_icon = "[green]CORRECT[/green]" if exact_match else (
                "[yellow]NEUTRAL[/yellow]" if predicted_direction == "neutral" else "[red]WRONG[/red]"
            )

            console.print(f"  Price at analysis: ${analysis_price:.2f}")
            console.print(f"  Price {case['future_check']}: ${future_price:.2f} ({actual_change_pct:+.1f}%)")
            console.print(f"  Signal Score: {signal_score} | RSI: {rsi} | MACD Hist: {macd_hist}")
            console.print(f"  Predicted: {predicted_direction.upper()} | Actual: {actual_direction.upper()} -> {status_icon}")

            results.append({
                "case": case,
                "status": "tested",
                "analysis_price": analysis_price,
                "future_price": future_price,
                "change_pct": actual_change_pct,
                "actual": actual_direction,
                "predicted": predicted_direction,
                "correct": exact_match,
                "neutral": predicted_direction == "neutral",
                "signal_score": signal_score,
                "rsi": rsi,
            })

        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")
            results.append({"case": case, "status": "error", "reason": str(e)})

    # ── Summary Table ──
    console.print()
    table = Table(title="Accuracy Results Summary", border_style="cyan")
    table.add_column("Stock", style="bold")
    table.add_column("Scenario")
    table.add_column("Price Change", justify="right")
    table.add_column("Signal Score", justify="center")
    table.add_column("Predicted", justify="center")
    table.add_column("Actual", justify="center")
    table.add_column("Result", justify="center")

    tested = [r for r in results if r["status"] == "tested"]
    correct_count = sum(1 for r in tested if r["correct"])
    neutral_count = sum(1 for r in tested if r["neutral"])
    wrong_count = len(tested) - correct_count - neutral_count

    for r in results:
        if r["status"] != "tested":
            table.add_row(r["case"]["ticker"], r["case"]["name"], "-", "-", "-", "-",
                         f"[dim]{r['status']}[/dim]")
            continue

        change_str = f"{r['change_pct']:+.1f}%"
        change_style = "green" if r["change_pct"] > 0 else "red"
        pred_style = "green" if r["correct"] else ("yellow" if r["neutral"] else "red")
        result_str = "[green]CORRECT[/green]" if r["correct"] else (
            "[yellow]NEUTRAL[/yellow]" if r["neutral"] else "[red]WRONG[/red]"
        )

        table.add_row(
            r["case"]["ticker"],
            r["case"]["name"],
            f"[{change_style}]{change_str}[/{change_style}]",
            str(r["signal_score"]),
            f"[{pred_style}]{r['predicted'].upper()}[/{pred_style}]",
            r["actual"].upper(),
            result_str,
        )

    console.print(table)

    # ── Final Score ──
    if tested:
        accuracy = correct_count / len(tested) * 100
        non_wrong = (correct_count + neutral_count) / len(tested) * 100

        console.print()
        console.print(Panel(
            f"[bold]Tested: {len(tested)}[/bold] scenarios\n"
            f"[green]Correct: {correct_count}[/green] | "
            f"[yellow]Neutral: {neutral_count}[/yellow] | "
            f"[red]Wrong: {wrong_count}[/red]\n\n"
            f"[bold]Exact Accuracy: {accuracy:.0f}%[/bold]\n"
            f"[bold]Non-Wrong Rate: {non_wrong:.0f}%[/bold] (correct + neutral)\n\n"
            f"[dim]Note: Indicators predict short-term momentum, not fundamental events.\n"
            f"Earnings surprises and news can override technical signals.[/dim]",
            title="Accuracy Score",
            border_style="green" if accuracy >= 50 else "yellow",
        ))

    return correct_count, len(tested)


if __name__ == "__main__":
    correct, total = run_accuracy_test()
    sys.exit(0 if correct > 0 else 1)
