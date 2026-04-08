"""Format analysis results into a clean, readable report."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box


console = Console()


def print_report(results: dict, holdings: dict):
    """Print the full analysis report to the console."""
    data = results["data"]
    indicators = results["indicators"]

    console.print()

    # ── Header ──
    console.rule(f"[bold cyan]{data['ticker']} - {data['company_name']}[/bold cyan]", style="cyan")
    console.print()

    # ── Price Snapshot ──
    _print_price_snapshot(data, indicators)

    # ── Holdings ──
    if holdings["shares"] > 0:
        _print_holdings(data, holdings)

    # ── Key Indicators ──
    _print_indicators(indicators)

    # ── Technical Analysis ──
    console.print(Panel(
        results["technical_report"],
        title="[bold yellow]Technical Analysis[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
    ))

    # ── News Analysis ──
    console.print(Panel(
        results["news_report"],
        title="[bold magenta]News & Sentiment[/bold magenta]",
        border_style="magenta",
        padding=(1, 2),
    ))

    # ── Decision & Strategy ──
    console.print(Panel(
        results["decision_report"],
        title="[bold green]DECISION & STRATEGY[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))

    # ── Disclaimer ──
    console.print()
    console.print(
        "[dim italic]Disclaimer: This is AI-generated analysis for informational purposes only. "
        "Not financial advice. Always do your own research before trading.[/dim italic]"
    )
    console.print()


def _print_price_snapshot(data: dict, indicators: dict):
    """Print current price and key stats."""
    change = data["current_price"] - data["previous_close"]
    change_pct = (change / data["previous_close"] * 100) if data["previous_close"] > 0 else 0
    color = "green" if change >= 0 else "red"
    arrow = "+" if change >= 0 else ""

    table = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 2))
    table.add_column("Label", style="bold")
    table.add_column("Value")

    table.add_row("Price", f"[bold {color}]${data['current_price']:.2f}  ({arrow}{change:.2f} / {arrow}{change_pct:.1f}%)[/bold {color}]")
    table.add_row("Day Range", f"${data['day_low']:.2f} - ${data['day_high']:.2f}")
    table.add_row("52W Range", f"${data['week_52_low']:.2f} - ${data['week_52_high']:.2f}")

    vol_str = f"{data['volume']:,}"
    avg_vol_str = f"{data['avg_volume']:,}"
    vol_ratio = indicators.get("volume_ratio", 0)
    vol_color = "green" if vol_ratio and vol_ratio > 1.2 else ("red" if vol_ratio and vol_ratio < 0.8 else "white")
    table.add_row("Volume", f"[{vol_color}]{vol_str}[/{vol_color}]  (Avg: {avg_vol_str})")

    table.add_row("Sector", f"{data['sector']} / {data['industry']}")

    if data.get("pe_ratio"):
        table.add_row("P/E Ratio", f"{data['pe_ratio']:.1f}")

    console.print(Panel(table, title="[bold]Price Snapshot[/bold]", border_style="blue"))


def _print_holdings(data: dict, holdings: dict):
    """Print current holdings and P&L."""
    cost_basis = holdings["avg_price"] * holdings["shares"]
    current_value = data["current_price"] * holdings["shares"]
    pnl = current_value - cost_basis
    pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
    color = "green" if pnl >= 0 else "red"

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Label", style="bold")
    table.add_column("Value")

    table.add_row("Shares", f"{holdings['shares']}")
    table.add_row("Avg Buy Price", f"${holdings['avg_price']:.2f}")
    table.add_row("Current Value", f"${current_value:,.2f}")
    table.add_row("P&L", f"[bold {color}]${pnl:,.2f} ({'+' if pnl >= 0 else ''}{pnl_pct:.1f}%)[/bold {color}]")

    console.print(Panel(table, title="[bold]Your Position[/bold]", border_style="white"))


def _print_indicators(indicators: dict):
    """Print key technical indicators in a compact table."""
    table = Table(title="Key Indicators", box=box.ROUNDED, padding=(0, 1))
    table.add_column("Indicator", style="bold", min_width=12)
    table.add_column("Value", min_width=10)
    table.add_column("Signal", min_width=10)

    # RSI
    rsi = indicators.get("rsi_14")
    if rsi is not None:
        if rsi > 70:
            sig = "[red]Overbought[/red]"
        elif rsi < 30:
            sig = "[green]Oversold[/green]"
        else:
            sig = "[white]Neutral[/white]"
        table.add_row("RSI (14)", str(rsi), sig)

    # MACD
    hist = indicators.get("macd_histogram")
    if hist is not None:
        sig = "[green]Bullish[/green]" if hist > 0 else "[red]Bearish[/red]"
        table.add_row("MACD Hist", str(hist), sig)

    # Bollinger
    bb_u = indicators.get("bb_upper")
    bb_l = indicators.get("bb_lower")
    price = indicators.get("vwap") or 0
    if bb_u and bb_l:
        table.add_row("BB Range", f"${bb_l} - ${bb_u}", "")

    # VWAP
    vwap = indicators.get("vwap")
    if vwap:
        table.add_row("VWAP", f"${vwap}", "")

    # Moving Averages
    for label, key in [("EMA 9", "ema_9"), ("SMA 20", "sma_20"), ("SMA 50", "sma_50")]:
        val = indicators.get(key)
        if val is not None:
            table.add_row(label, f"${val}", "")

    console.print(table)
    console.print()
