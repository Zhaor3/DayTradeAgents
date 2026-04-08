#!/usr/bin/env python3
"""
DayTradeAgents Telegram Bot
----------------------------
AI-powered day trading assistant on Telegram.

Commands:
  ta NVDA           - Run full day-trade analysis (no position)
  ta NVDA 50 120.5  - Analyze while holding 50 shares at $120.50 avg
  /status           - Check if bot is alive
  /help             - Show commands

Setup:
  1. Talk to @BotFather on Telegram, create bot, get token
  2. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env
  3. python telegram_bot.py

Run as service:
  sudo systemctl start daytradeagents
"""

import os
import sys
import re
import time
import datetime
import requests
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from config import CONFIG

# ── Telegram Config ────────────────────────────────────────────────────────────

BOT_TOKEN       = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
TELEGRAM_API    = f"https://api.telegram.org/bot{BOT_TOKEN}"

if not BOT_TOKEN:
    print("ERROR: Set TELEGRAM_BOT_TOKEN in .env file")
    sys.exit(1)
if not ALLOWED_CHAT_ID:
    print("ERROR: Set TELEGRAM_CHAT_ID in .env file")
    sys.exit(1)

# ── Telegram helpers ───────────────────────────────────────────────────────────

def send_msg(chat_id: int, text: str) -> None:
    """Send a Telegram message, splitting if too long."""
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        try:
            requests.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": chat_id, "text": chunk},
                timeout=10,
            )
        except Exception as e:
            print(f"[WARN] send failed: {e}")
        time.sleep(0.3)


def get_updates(offset: int) -> list:
    """Long-poll Telegram for new messages."""
    try:
        resp = requests.get(
            f"{TELEGRAM_API}/getUpdates",
            params={"timeout": 30, "offset": offset},
            timeout=40,
        )
        return resp.json().get("result", [])
    except Exception as e:
        print(f"[WARN] getUpdates error: {e}")
        return []


# ── Analysis runner ────────────────────────────────────────────────────────────

def send_photo(chat_id: int, photo_path: str, caption: str = "") -> None:
    """Send a photo to Telegram."""
    try:
        with open(photo_path, "rb") as f:
            requests.post(
                f"{TELEGRAM_API}/sendPhoto",
                data={"chat_id": chat_id, "caption": caption[:1024]},
                files={"photo": f},
                timeout=30,
            )
    except Exception as e:
        print(f"[WARN] sendPhoto failed: {e}")


def run_bot_analysis(ticker: str, shares: int, avg_price: float, chat_id: int) -> str:
    """Run the DayTradeAgents analysis pipeline and return formatted report."""

    holdings_str = f"holding {shares} shares at ${avg_price:.2f}" if shares > 0 else "no position"
    send_msg(chat_id,
        f"Analyzing {ticker} ({holdings_str})...\n"
        f"Running 11 AI agents + debate rounds (4-7 min).\n"
        f"Phases: Analysts -> Bull/Bear Debate -> Trader -> Risk Debate -> Portfolio Manager\n"
        f"I'll message you when done."
    )

    try:
        from tradingagent.agents.pipeline import run_analysis

        holdings = {"shares": shares, "avg_price": avg_price}

        def status_update(msg):
            print(f"  [{ticker}] {msg}")

        results = run_analysis(ticker, holdings, on_status=status_update)

    except ValueError as e:
        return f"ERROR: {e}"
    except Exception as e:
        return f"ERROR: Analysis failed - {e}\n\n{traceback.format_exc()[-400:]}"

    # Send chart first if available
    chart_path = results.get("chart_path")
    if chart_path:
        send_photo(chat_id, chart_path, f"{ticker} - Price Prediction Chart")

    # Build the Telegram report
    return format_telegram_report(ticker, shares, avg_price, results)


def format_telegram_report(ticker: str, shares: int, avg_price: float, results: dict) -> str:
    """Format analysis into a clean Telegram-friendly report using GPT rewrite."""
    data = results["data"]
    indicators = results["indicators"]

    # Build raw report sections
    raw_parts = []

    # Price snapshot
    change = data["current_price"] - data["previous_close"]
    change_pct = (change / data["previous_close"] * 100) if data["previous_close"] > 0 else 0
    raw_parts.append(
        f"=== PRICE SNAPSHOT ===\n"
        f"Ticker: {data['ticker']} ({data['company_name']})\n"
        f"Price: ${data['current_price']:.2f} ({'+' if change >= 0 else ''}{change:.2f} / {'+' if change_pct >= 0 else ''}{change_pct:.1f}%)\n"
        f"Day Range: ${data['day_low']:.2f} - ${data['day_high']:.2f}\n"
        f"52W Range: ${data['week_52_low']:.2f} - ${data['week_52_high']:.2f}\n"
        f"Volume: {data['volume']:,} (Avg: {data['avg_volume']:,})\n"
        f"Sector: {data['sector']}"
    )

    # Holdings P&L
    if shares > 0:
        cost = avg_price * shares
        current_val = data["current_price"] * shares
        pnl = current_val - cost
        pnl_pct = (pnl / cost * 100) if cost > 0 else 0
        raw_parts.append(
            f"=== YOUR POSITION ===\n"
            f"Shares: {shares} at ${avg_price:.2f} avg\n"
            f"Current Value: ${current_val:,.2f}\n"
            f"P&L: ${pnl:,.2f} ({'+' if pnl >= 0 else ''}{pnl_pct:.1f}%)"
        )

    # Key indicators (expanded)
    raw_parts.append(
        f"=== KEY INDICATORS ===\n"
        f"Signal Score: {indicators.get('signal_score', 'N/A')}/100 ({indicators.get('signal_label', 'N/A')})\n"
        f"RSI(14): {indicators.get('rsi_14', 'N/A')} | Stochastic %K: {indicators.get('stochastic_k', 'N/A')}\n"
        f"MACD Histogram: {indicators.get('macd_histogram', 'N/A')} | ADX: {indicators.get('adx', 'N/A')}\n"
        f"ATR(14): {indicators.get('atr_14', 'N/A')} | VWAP: {indicators.get('vwap', 'N/A')}\n"
        f"Volume Ratio: {indicators.get('volume_ratio', 'N/A')}x\n"
        f"RSI Divergence: {indicators.get('rsi_divergence', 'N/A')} | EMA Cross: {indicators.get('ema_cross', 'N/A')}\n"
        f"Support: {indicators.get('support_levels', [])}\n"
        f"Resistance: {indicators.get('resistance_levels', [])}\n"
        f"Insider Buys/Sells: {data.get('insider_buys', 0)}/{data.get('insider_sells', 0)}\n"
        f"Earnings in: {data.get('days_to_earnings', 'N/A')} days | Put/Call: {data.get('put_call_ratio', 'N/A')}\n"
        f"VIX: {data.get('vix', 'N/A')} | SPY 1D: {data.get('spy_change_1d', 'N/A')}%"
    )

    # All agent reports
    raw_parts.append(f"=== TECHNICAL ANALYSIS ===\n{results['technical_report']}")
    raw_parts.append(f"=== NEWS ANALYSIS ===\n{results['news_report']}")
    raw_parts.append(f"=== FUNDAMENTALS ===\n{results['fundamentals_report']}")
    raw_parts.append(f"=== RESEARCH DEBATE ===\nBull: {results['bull_case'][:500]}\nBear: {results['bear_case'][:500]}")
    raw_parts.append(f"=== RESEARCH VERDICT ===\n{results['research_verdict']}")
    raw_parts.append(f"=== TRADE PROPOSAL ===\n{results['trade_proposal']}")
    raw_parts.append(f"=== RISK DEBATE ===\nAggressive: {results['risk_aggressive'][:300]}\nConservative: {results['risk_conservative'][:300]}\nNeutral: {results['risk_neutral'][:300]}")
    raw_parts.append(f"=== PORTFOLIO MANAGER FINAL DECISION ===\n{results['decision_report']}")

    raw_report = "\n\n".join(raw_parts)

    # Try to rewrite with GPT for cleaner format
    return rewrite_for_telegram(ticker, raw_report)


REWRITE_PROMPT = """You are a trading report formatter for Telegram. Rewrite the raw analysis below into this exact clean format. Rules:
- Do NOT invent facts, numbers, or levels not in the original.
- Plain text only (no markdown headers, no #). Use ** for bold key levels.
- Keep it concise and actionable for a day trader.

Output this exact format:

-----------------------------------
TRADE DASHBOARD — {ticker}
{date}

ACTION: [BUY / SELL / HOLD]
Confidence: [High / Medium / Low]
Why: [1 sentence]

SHORT-TERM PLAY (1-5 Days)
- Direction: [Bullish / Bearish / Neutral]
- Entry: $[price]
- Target: $[price] ([X]% gain)
- Stop Loss: $[price] ([X]% risk)
- Timeframe: [e.g. "2-3 days"]
- What to do: [1-2 sentences]

LONG-TERM PLAY (1-4 Weeks)
- Direction: [Bullish / Bearish / Neutral]
- Entry: $[price]
- Target: $[price]
- Stop Loss: $[price]
- Timeframe: [e.g. "2-3 weeks"]
- What to do: [1-2 sentences]

KEY LEVELS
- Support: [prices]
- Resistance: [prices]
- VWAP: $[price]

RISK CHECK
- Risk Level: [Low / Medium / High]
- Position Size: [suggestion]
- Biggest Risk: [1 sentence]
- Exit if: [condition]

NEWS IMPACT
[1-2 sentences on news sentiment]

QUICK TAKE
- Bull case: [one line]
- Bear case: [one line]
- Best action now: [one line]
-----------------------------------

RAW REPORT:

{raw_report}"""


def rewrite_for_telegram(ticker: str, raw_report: str) -> str:
    """Use the configured LLM to rewrite into clean Telegram format."""
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    # Try OpenAI
    api_key = CONFIG.get("openai_api_key") or os.getenv("OPENAI_API_KEY", "")
    if api_key and CONFIG.get("llm_provider", "openai") == "openai":
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": CONFIG.get("model_quick", "gpt-5-mini"),
                    "messages": [{"role": "user", "content": REWRITE_PROMPT.format(
                        ticker=ticker, date=date_str, raw_report=raw_report[:10000]
                    )}],
                    "max_completion_tokens": 3000,
                },
                timeout=60,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            print(f"[WARN] OpenAI rewrite failed: {resp.status_code}")
        except Exception as e:
            print(f"[WARN] Rewrite failed: {e}")

    # Try Anthropic
    api_key = CONFIG.get("anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY", "")
    if api_key and CONFIG.get("llm_provider") == "anthropic":
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": CONFIG.get("model_quick", "claude-sonnet-4-20250514"),
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": REWRITE_PROMPT.format(
                        ticker=ticker, date=date_str, raw_report=raw_report[:10000]
                    )}],
                },
                timeout=60,
            )
            if resp.status_code == 200:
                return resp.json()["content"][0]["text"].strip()
            print(f"[WARN] Anthropic rewrite failed: {resp.status_code}")
        except Exception as e:
            print(f"[WARN] Rewrite failed: {e}")

    # Fallback: send the raw strategist decision directly
    return (
        f"TRADE DASHBOARD — {ticker}\n"
        f"Date: {date_str}\n"
        f"{'='*35}\n\n"
        f"{raw_report[-3500:]}"
    )


# ── Command parser ─────────────────────────────────────────────────────────────

def parse_command(text: str):
    """
    Parse commands:
      ta NVDA           -> (NVDA, 0, 0.0)
      ta NVDA 50 120.5  -> (NVDA, 50, 120.5)
    Returns (ticker, shares, avg_price) or None.
    """
    text = text.strip()

    # Match: ta TICKER [shares] [avg_price]
    pattern = r"^(?:ta|analyze)\s+([A-Za-z0-9.^-]+)(?:\s+(\d+)\s+([\d.]+))?$"
    m = re.match(pattern, text, re.IGNORECASE)
    if m:
        ticker = m.group(1).upper()
        shares = int(m.group(2)) if m.group(2) else 0
        avg_price = float(m.group(3)) if m.group(3) else 0.0
        return ticker, shares, avg_price
    return None


# ── Main bot loop ──────────────────────────────────────────────────────────────

def flush_old_messages() -> int:
    """Skip messages that arrived before bot started."""
    try:
        resp = requests.get(
            f"{TELEGRAM_API}/getUpdates",
            params={"timeout": 0, "offset": -1},
            timeout=10,
        )
        results = resp.json().get("result", [])
        if results:
            return results[-1]["update_id"] + 1
    except Exception as e:
        print(f"[WARN] flush error: {e}")
    return 0


def main():
    print("[INFO] DayTradeAgents Telegram Bot started.")
    print(f"[INFO] Listening for chat ID {ALLOWED_CHAT_ID}...")

    offset = flush_old_messages()
    print(f"[INFO] Flushed old messages. Starting from offset {offset}")

    send_msg(ALLOWED_CHAT_ID,
        "DayTradeAgents Bot is online!\n\n"
        "Commands:\n"
        "  ta NVDA - analyze (no position)\n"
        "  ta NVDA 50 120.5 - analyze holding 50 shares at $120.50\n"
        "  /status - check bot\n"
        "  /help - show commands"
    )

    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            msg = update.get("message", {})
            chat_id = msg.get("chat", {}).get("id")
            text = msg.get("text", "").strip()

            if not text or chat_id != ALLOWED_CHAT_ID:
                continue

            print(f"[MSG] {chat_id}: {text}")

            # Help
            if text.lower() in ("/start", "/help"):
                send_msg(chat_id,
                    "DayTradeAgents - Day Trading Assistant\n\n"
                    "Commands:\n"
                    "  ta NVDA - analyze stock (no position)\n"
                    "  ta NVDA 50 120.5 - analyze while holding 50 shares at $120.50 avg\n"
                    "  /status - check bot is alive\n"
                    "  /help - this message\n\n"
                    "The bot gives you:\n"
                    "  - BUY / SELL / HOLD decision\n"
                    "  - Short-term strategy (1-5 days)\n"
                    "  - Long-term strategy (1-4 weeks)\n"
                    "  - Entry, target, stop-loss prices\n"
                    "  - Risk assessment"
                )
                continue

            # Status
            if text.lower() == "/status":
                send_msg(chat_id, "Bot is running and ready.")
                continue

            # Analysis
            parsed = parse_command(text)
            if parsed:
                ticker, shares, avg_price = parsed
                try:
                    result = run_bot_analysis(ticker, shares, avg_price, chat_id)
                    send_msg(chat_id, result)
                except Exception as e:
                    send_msg(chat_id, f"ERROR: {e}\n\n{traceback.format_exc()[-400:]}")
            else:
                send_msg(chat_id,
                    f"Unknown command: {text}\n\n"
                    f"Try:\n"
                    f"  ta NVDA\n"
                    f"  ta NVDA 50 120.5"
                )

        time.sleep(1)


if __name__ == "__main__":
    main()
