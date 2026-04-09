"""
TradingAgent V2 - Day Trading Assistant
========================================
An AI-powered day trading analysis tool that provides:
  - Technical analysis (RSI, MACD, Bollinger Bands, S/R levels)
  - News sentiment analysis
  - BUY / SELL / HOLD decisions
  - Short-term (1-5 days) and Long-term (1-4 weeks) strategies
  - Clear entry, target, and stop-loss prices

Usage: python main.py
"""

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text

from tradingagent.agents.pipeline import run_analysis
from tradingagent.report import print_report

console = Console()


def print_banner():
    banner = r"""
  ____              _____              _         _                    _
 |  _ \  __ _ _   _|_   _| __ __ _  __| | ___   / \   __ _  ___ _ __ | |_
 | | | |/ _` | | | | | || '__/ _` |/ _` |/ _ \ / _ \ / _` |/ _ \ '_ \| __|
 | |_| | (_| | |_| | | || | | (_| | (_| |  __// ___ \ (_| |  __/ | | | |_
 |____/ \__,_|\__, | |_||_|  \__,_|\__,_|\___/_/   \_\__, |\___|_| |_|\__|
              |___/                                   |___/
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    console.print("[bold]AI-Powered Day Trading Assistant[/bold]", justify="center")
    console.print("[dim]Technical Analysis + News Sentiment + Trading Strategies[/dim]", justify="center")
    console.print()


def get_user_input() -> tuple:
    """Get ticker and holdings info from user."""
    console.rule("[bold]Setup[/bold]")
    console.print()

    # Get ticker
    ticker = Prompt.ask("[bold]Enter stock ticker[/bold]", default="AAPL").strip().upper()

    # Ask about holdings
    console.print()
    has_position = Prompt.ask(
        f"[bold]Are you currently holding {ticker}?[/bold]",
        choices=["y", "n"],
        default="n"
    )

    shares = 0
    avg_price = 0.0

    if has_position == "y":
        shares = IntPrompt.ask("  How many shares do you hold?", default=0)
        if shares > 0:
            avg_price = FloatPrompt.ask("  What is your average buy price ($)?", default=0.0)

    return ticker, {"shares": shares, "avg_price": avg_price}


def run_with_spinner(ticker: str, holdings: dict) -> dict:
    """Run analysis with a progress spinner."""
    status_msg = ["Starting analysis..."]

    def on_status(msg):
        status_msg[0] = msg

    console.print()

    with Live(console=console, refresh_per_second=8) as live:
        def update_status(msg):
            status_msg[0] = msg
            live.update(Text(f"  >> {msg}", style="bold yellow"))

        results = run_analysis(ticker, holdings, on_status=update_status)

    return results


def main():
    """Main interactive loop."""
    print_banner()

    while True:
        try:
            ticker, holdings = get_user_input()

            console.print()
            console.rule(f"[bold cyan]Analyzing {ticker}...[/bold cyan]")

            try:
                results = run_with_spinner(ticker, holdings)
                print_report(results, holdings)
            except ValueError as e:
                console.print(f"\n[bold red]Error:[/bold red] {e}\n")
            except Exception as e:
                console.print(f"\n[bold red]Error during analysis:[/bold red] {e}\n")
                console.print("[dim]Check your API keys in .env file and internet connection.[/dim]\n")

            # Ask to continue
            console.print()
            again = Prompt.ask(
                "[bold]Analyze another stock?[/bold]",
                choices=["y", "n"],
                default="y"
            )
            if again == "n":
                console.print("\n[bold cyan]Happy trading! Remember: always manage your risk.[/bold cyan]\n")
                break

            console.print()

        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]Goodbye! Trade safe.[/bold cyan]\n")
            break


if __name__ == "__main__":
    main()
