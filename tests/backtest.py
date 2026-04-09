"""Backtest script - run the full pipeline on historical stock data.

This script tests the complete system by:
1. Fetching real historical data from yfinance
2. Computing all technical indicators
3. Running the full LLM pipeline (requires API keys)
4. Validating the output structure and quality

Usage:
  python tests/backtest.py                    # Default: AAPL, no LLM (mock mode)
  python tests/backtest.py MSFT               # Specific ticker, mock mode
  python tests/backtest.py AAPL --live        # Real LLM calls (needs API keys)
  python tests/backtest.py NVDA --live --holdings 50 120.5
"""

import sys
import os
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


def parse_args():
    parser = argparse.ArgumentParser(description="Backtest the trading agent pipeline")
    parser.add_argument("ticker", nargs="?", default="AAPL", help="Stock ticker (default: AAPL)")
    parser.add_argument("--live", action="store_true", help="Use real LLM (requires API keys)")
    parser.add_argument("--holdings", nargs=2, type=float, metavar=("SHARES", "AVG_PRICE"),
                        help="Current holdings: shares avg_price")
    return parser.parse_args()


def validate_data(data: dict) -> list:
    """Validate the market data dict has all required fields."""
    issues = []
    required = ["ticker", "current_price", "volume", "daily_short", "daily_long", "intraday"]
    for key in required:
        if key not in data:
            issues.append(f"MISSING: data['{key}']")
    if data.get("current_price", 0) == 0:
        issues.append("CRITICAL: current_price is 0")
    if hasattr(data.get("daily_short"), "__len__") and len(data["daily_short"]) < 5:
        issues.append(f"WARNING: daily_short only has {len(data['daily_short'])} rows (need 5+)")
    if hasattr(data.get("daily_long"), "__len__") and len(data["daily_long"]) < 20:
        issues.append(f"WARNING: daily_long only has {len(data['daily_long'])} rows (need 20+)")
    return issues


def validate_indicators(indicators: dict) -> list:
    """Validate computed indicators are reasonable."""
    issues = []

    # Check RSI range
    rsi = indicators.get("rsi_14")
    if rsi is not None and not (0 <= rsi <= 100):
        issues.append(f"FAIL: RSI out of range: {rsi}")

    # Check Bollinger band ordering
    bb_u = indicators.get("bb_upper")
    bb_m = indicators.get("bb_middle")
    bb_l = indicators.get("bb_lower")
    if all(v is not None for v in [bb_u, bb_m, bb_l]):
        if not (bb_u >= bb_m >= bb_l):
            issues.append(f"FAIL: Bollinger bands misordered: {bb_u} / {bb_m} / {bb_l}")

    # Check ATR is positive
    atr = indicators.get("atr_14")
    if atr is not None and atr <= 0:
        issues.append(f"FAIL: ATR is non-positive: {atr}")

    # Check signal score range
    score = indicators.get("signal_score")
    if score is not None and not (-100 <= score <= 100):
        issues.append(f"FAIL: Signal score out of range: {score}")

    # Check that key indicators exist
    expected = ["rsi_14", "macd_line", "macd_histogram", "bb_upper", "atr_14",
                "signal_score", "signal_label"]
    for key in expected:
        if key not in indicators or indicators[key] is None:
            issues.append(f"WARNING: indicator '{key}' is missing or None")

    return issues


def validate_decision(decision_report: str) -> list:
    """Validate the final decision report structure."""
    issues = []

    if not decision_report or len(decision_report) < 100:
        issues.append("FAIL: Decision report is empty or too short")
        return issues

    required_sections = {
        "FINAL DECISION": ["Rating:", "Confidence:"],
        "SHORT-TERM PLAY": ["Entry:", "Target:", "Stop Loss:"],
        "LONG-TERM PLAY": ["Entry:", "Target:", "Stop Loss:"],
        "RISK MANAGEMENT": ["Risk Level:", "Position Size:"],
    }

    for section, fields in required_sections.items():
        if section not in decision_report:
            issues.append(f"MISSING SECTION: {section}")
        else:
            for field in fields:
                if field not in decision_report:
                    issues.append(f"MISSING FIELD: {field} in {section}")

    valid_ratings = ["BUY", "SELL", "HOLD", "OVERWEIGHT", "UNDERWEIGHT"]
    if not any(f"Rating: {r}" in decision_report for r in valid_ratings):
        issues.append("WARNING: No valid rating found (BUY/SELL/HOLD/OVERWEIGHT/UNDERWEIGHT)")

    return issues


def run_backtest(ticker: str, live: bool, holdings: dict):
    """Run the full backtest."""
    console.print()
    console.print(Panel(
        f"[bold]Backtesting: {ticker}[/bold]\n"
        f"Mode: {'LIVE (real LLM)' if live else 'MOCK (no API keys needed)'}\n"
        f"Holdings: {holdings['shares']} shares @ ${holdings['avg_price']:.2f}"
        if holdings["shares"] > 0 else
        f"[bold]Backtesting: {ticker}[/bold]\n"
        f"Mode: {'LIVE (real LLM)' if live else 'MOCK (no API keys needed)'}\n"
        f"Holdings: None",
        title="TradingAgent V2 Backtest",
        border_style="cyan",
    ))

    # ── Step 1: Fetch Data ──
    console.print("\n[bold cyan]Step 1:[/bold cyan] Fetching market data...")
    t0 = time.time()

    from tradingagent.data.market_data import fetch_stock_data
    data = fetch_stock_data(ticker)
    fetch_time = time.time() - t0

    data_issues = validate_data(data)
    _print_validation("Market Data", data_issues, {
        "Ticker": data.get("ticker"),
        "Price": f"${data.get('current_price', 0):.2f}",
        "Volume": f"{data.get('volume', 0):,}",
        "Daily Short Rows": len(data.get("daily_short", [])),
        "Daily Long Rows": len(data.get("daily_long", [])),
        "Intraday Rows": len(data.get("intraday", [])),
        "News Items": len(data.get("news", [])),
        "Fetch Time": f"{fetch_time:.1f}s",
    })

    if any("CRITICAL" in i for i in data_issues):
        console.print("[bold red]Cannot continue - critical data issues.[/bold red]")
        return False

    # ── Step 2: Compute Indicators ──
    console.print("\n[bold cyan]Step 2:[/bold cyan] Computing technical indicators...")
    t0 = time.time()

    from tradingagent.data.indicators import compute_all_indicators
    indicators = compute_all_indicators(data)
    indicator_time = time.time() - t0

    ind_issues = validate_indicators(indicators)
    _print_validation("Indicators", ind_issues, {
        "RSI(14)": indicators.get("rsi_14"),
        "MACD": indicators.get("macd_histogram"),
        "BB Upper": indicators.get("bb_upper"),
        "BB Lower": indicators.get("bb_lower"),
        "ATR(14)": indicators.get("atr_14"),
        "Signal Score": f"{indicators.get('signal_score', 'N/A')} ({indicators.get('signal_label', 'N/A')})",
        "Compute Time": f"{indicator_time:.2f}s",
    })

    # ── Step 3: Run Pipeline ──
    console.print(f"\n[bold cyan]Step 3:[/bold cyan] Running analysis pipeline ({'LIVE' if live else 'MOCK'})...")

    if live:
        results = _run_live_pipeline(ticker, holdings)
    else:
        results = _run_mock_pipeline(data, indicators, holdings)

    if results is None:
        return False

    # ── Step 4: Validate Decision ──
    console.print("\n[bold cyan]Step 4:[/bold cyan] Validating decision output...")
    decision = results.get("decision_report", "")
    dec_issues = validate_decision(decision)
    _print_validation("Decision Report", dec_issues, {
        "Length": f"{len(decision)} chars",
        "Has Rating": any(r in decision for r in ["BUY", "SELL", "HOLD", "OVERWEIGHT", "UNDERWEIGHT"]),
        "Has Entry Price": "Entry:" in decision,
        "Has Stop Loss": "Stop Loss:" in decision,
    })

    # ── Summary ──
    all_issues = data_issues + ind_issues + dec_issues
    fails = [i for i in all_issues if "FAIL" in i or "CRITICAL" in i]
    warns = [i for i in all_issues if "WARNING" in i]

    console.print()
    if not fails:
        console.print(Panel(
            f"[bold green]ALL CHECKS PASSED[/bold green]\n"
            f"Warnings: {len(warns)} | Failures: 0\n"
            f"Pipeline is working correctly!",
            title="Result",
            border_style="green",
        ))
        return True
    else:
        console.print(Panel(
            f"[bold red]FAILURES DETECTED[/bold red]\n"
            f"Failures: {len(fails)} | Warnings: {len(warns)}\n"
            + "\n".join(f"  - {f}" for f in fails),
            title="Result",
            border_style="red",
        ))
        return False


def _run_live_pipeline(ticker, holdings):
    """Run pipeline with real LLM calls."""
    try:
        from tradingagent.agents.pipeline import run_analysis
        t0 = time.time()
        results = run_analysis(ticker, holdings, on_status=lambda m: console.print(f"  [dim]{m}[/dim]"))
        elapsed = time.time() - t0
        console.print(f"  Pipeline completed in {elapsed:.1f}s")
        return results
    except Exception as e:
        console.print(f"  [bold red]Pipeline failed: {e}[/bold red]")
        return None


def _run_mock_pipeline(data, indicators, holdings):
    """Run pipeline with mocked LLM responses."""
    from tests.conftest import MOCK_LLM_RESPONSES

    console.print("  [dim]Using mock LLM responses (no API keys required)[/dim]")

    # Simulate the pipeline output structure
    results = {
        "data": data,
        "indicators": indicators,
        "technical_report": MOCK_LLM_RESPONSES["technical"],
        "news_report": MOCK_LLM_RESPONSES["news"],
        "fundamentals_report": MOCK_LLM_RESPONSES["fundamentals"],
        "bull_case": MOCK_LLM_RESPONSES["bull"],
        "bear_case": MOCK_LLM_RESPONSES["bear"],
        "bull_rebuttal": MOCK_LLM_RESPONSES["bull_rebuttal"],
        "bear_counter": MOCK_LLM_RESPONSES["bear_counter"],
        "research_verdict": MOCK_LLM_RESPONSES["verdict"],
        "trade_proposal": MOCK_LLM_RESPONSES["trade"],
        "risk_aggressive": MOCK_LLM_RESPONSES["risk_aggressive"],
        "risk_conservative": MOCK_LLM_RESPONSES["risk_conservative"],
        "risk_neutral": MOCK_LLM_RESPONSES["risk_neutral"],
        "decision_report": MOCK_LLM_RESPONSES["decision"],
        "chart_path": None,
    }
    return results


def _print_validation(title, issues, details):
    """Print validation results in a nice table."""
    table = Table(title=title, show_header=False, border_style="dim")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    for key, val in details.items():
        table.add_row(key, str(val))

    console.print(table)

    if issues:
        for issue in issues:
            if "FAIL" in issue or "CRITICAL" in issue:
                console.print(f"  [red]{issue}[/red]")
            else:
                console.print(f"  [yellow]{issue}[/yellow]")
    else:
        console.print(f"  [green]All checks passed[/green]")


if __name__ == "__main__":
    args = parse_args()
    holdings = {"shares": 0, "avg_price": 0.0}
    if args.holdings:
        holdings = {"shares": int(args.holdings[0]), "avg_price": args.holdings[1]}

    success = run_backtest(args.ticker, args.live, holdings)
    sys.exit(0 if success else 1)
