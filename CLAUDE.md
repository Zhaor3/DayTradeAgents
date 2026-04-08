# DayTradeAgents

AI-powered day trading assistant that runs as a Telegram bot on Ubuntu.

## What This Project Does

Multi-agent analysis pipeline for day trading:
1. **Technical Analyst** - RSI, MACD, Bollinger Bands, moving averages, VWAP, support/resistance, volume
2. **News Analyst** - Scans recent headlines, assesses sentiment
3. **Strategist** - Combines everything into BUY/SELL/HOLD decision with two timeframes

Output includes:
- Decision: BUY / SELL / HOLD with confidence
- Short-term strategy (1-5 days): entry, target, stop-loss
- Long-term strategy (1-4 weeks): entry, target, stop-loss
- Risk assessment and position sizing

## Project Structure

```
DayTradeAgents/
├── main.py                  # Local interactive CLI
├── telegram_bot.py          # Telegram bot (runs on Ubuntu server)
├── config.py                # Settings from .env
├── setup_ubuntu.sh          # One-click Ubuntu deployment
├── .env                     # API keys (never commit)
├── requirements.txt         # Python deps
├── tradingagent/
│   ├── agents/
│   │   ├── llm_client.py          # OpenAI / Anthropic abstraction
│   │   ├── technical_analyst.py   # Technical analysis agent
│   │   ├── news_analyst.py        # News sentiment agent
│   │   ├── strategist.py          # Decision maker agent
│   │   └── pipeline.py            # Orchestrator
│   ├── data/
│   │   ├── market_data.py         # yfinance data fetcher
│   │   └── indicators.py          # RSI, MACD, BB, etc.
│   └── report.py                  # Rich CLI report formatter
```

## Tech Stack

- Python 3.10+
- yfinance (market data)
- OpenAI / Anthropic (LLM analysis)
- Telegram Bot API (delivery)
- Rich (CLI formatting)
- systemd (Ubuntu service)

## Key Commands

```bash
# Local test
python main.py

# Telegram bot
python telegram_bot.py

# Ubuntu service
sudo systemctl start daytradeagents
sudo systemctl status daytradeagents
tail -f ~/DayTradeAgents/bot.log
```

## Telegram Bot Commands

```
ta NVDA              - Analyze with no position
ta NVDA 50 120.5     - Analyze holding 50 shares at $120.50 avg
/status              - Check bot is alive
/help                - Show commands
```

## Important

- Never commit .env (contains API keys)
- The bot only responds to the TELEGRAM_CHAT_ID in .env (security)
- Analysis takes ~30-60 seconds per stock
- yfinance is free but has rate limits - don't spam requests
