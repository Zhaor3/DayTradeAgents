<div align="center">

# DayTradeAgents

### Multi-Agent LLM Day Trading Framework

*Inspired by real-world trading firms — AI agents that debate, challenge, and stress-test every trade before you take it.*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude-D4A574?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![yfinance](https://img.shields.io/badge/Data-Yahoo%20Finance-720e9e?style=for-the-badge)](https://finance.yahoo.com/)

<br/>

**11 AI Agents** | **Multi-Round Debates** | **15+ Technical Indicators** | **Price Prediction Charts**

Built on ideas from [TradingAgents](https://github.com/TauricResearch/TradingAgents) by Tauric Research

---

</div>

## Overview

DayTradeAgents is a multi-agent AI framework that mirrors how professional trading firms operate. Instead of a single AI giving you a buy/sell signal, **11 specialized agents** analyze the market, debate each other, stress-test the trade through a risk committee, and only then deliver a final decision.

Send `ta NVDA` to your Telegram bot and receive:

- A **price prediction chart** with candlesticks, indicator overlays, and an ATR-based forecast cone
- A **trade dashboard** with BUY/SELL/HOLD decision, entry/target/stop-loss prices, position sizing, and risk assessment
- **Two timeframe strategies**: short-term (1-5 days) and long-term (1-4 weeks)

<br/>

<div align="center">

```
                        ┌─────────────────────────┐
                        │     MARKET DATA          │
                        │  Price + Options + VIX   │
                        │  Insider + Earnings      │
                        └────────────┬────────────┘
                                     │
                        ┌────────────▼────────────┐
                        │    INDICATOR ENGINE      │
                        │  15+ Technical Signals   │
                        │  Signal Alignment Score  │
                        └────────────┬────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
  ┌─────▼──────┐             ┌──────▼──────┐             ┌───────▼──────┐
  │  Technical │             │    News     │             │ Fundamentals │
  │  Analyst   │             │   Analyst   │             │   Analyst    │
  │   (deep)   │             │   (quick)   │             │   (quick)    │
  └─────┬──────┘             └──────┬──────┘             └───────┬──────┘
        └────────────────────────────┼────────────────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │       RESEARCH DEBATE           │
                    │                                 │
                    │  ┌──────┐    Round 1   ┌──────┐ │
                    │  │ BULL ├────────────►│ BEAR │ │
                    │  │      │◄────────────┤      │ │
                    │  └──┬───┘    Round 2   └──┬───┘ │
                    │     │    ┌──────────┐    │     │
                    │     └───►│ RESEARCH ├◄───┘     │
                    │          │ MANAGER  │          │
                    │          └────┬─────┘          │
                    └───────────────┼────────────────┘
                                    │
                        ┌───────────▼──────────┐
                        │       TRADER         │
                        │  Concrete proposal:  │
                        │  Entry / Target /    │
                        │  Stop / Size         │
                        └───────────┬──────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │       RISK STRESS-TEST         │
                    │                                │
                    │  ┌────────────┐ ┌────────────┐ │
                    │  │ AGGRESSIVE │ │CONSERVATIVE│ │
                    │  │  "Take it" │ │ "Too risky"│ │
                    │  └──────┬─────┘ └─────┬──────┘ │
                    │         └──────┬──────┘        │
                    │          ┌─────▼─────┐         │
                    │          │  NEUTRAL   │         │
                    │          │ "Balance"  │         │
                    │          └────────────┘         │
                    └───────────────┬────────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │      PORTFOLIO MANAGER         │
                    │                                │
                    │  Final Decision + Strategies   │
                    │  BUY / OVERWEIGHT / HOLD /     │
                    │  UNDERWEIGHT / SELL             │
                    └───────────────┬────────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │    CHART + REPORT OUTPUT       │
                    │    Prediction cone + Dashboard │
                    │    ──────► Telegram            │
                    └───────────────────────────────┘
```

</div>

---

## Key Features

<table>
<tr>
<td width="50%">

### Multi-Agent Debate Architecture
11 specialized agents collaborate through structured debates. Bull and bear researchers argue in multiple rounds, each directly rebutting the other's points. A research manager judges the surviving arguments.

### 3-Way Risk Stress-Test
Every trade proposal is stress-tested by three risk personas: aggressive (champions opportunity), conservative (highlights danger), and neutral (finds balance). The portfolio manager synthesizes the debate.

### Signal Alignment Score
A composite score from -100 to +100 computed from all indicators before agents begin analysis. This objective anchor reduces the LLM's tendency to cherry-pick signals that confirm the first narrative it encounters.

</td>
<td width="50%">

### 15+ Technical Indicators
All computed locally from free Yahoo Finance data:
RSI, MACD, Bollinger Bands, ATR, Stochastic, ADX, OBV, Fibonacci, VWAP, ROC, RSI Divergence, EMA Crossovers, and more.

### Price Prediction Chart
Candlestick chart with indicator overlays and an ATR-based forecast cone. Support/resistance zones, Fibonacci levels, and decision badge — sent as an image to Telegram.

### Position-Aware Analysis
Tell the bot your current holdings and it factors your P&L into the decision. Holding at a loss? It considers whether to cut or hold. Sitting on gains? It recommends trailing stops.

</td>
</tr>
</table>

---

## Pipeline Detail

### Phase 0: Data Collection
| Source | Data | Purpose |
|--------|------|---------|
| Yahoo Finance | OHLCV (intraday + daily) | Price action & charting |
| Yahoo Finance | Options chain | Put/call ratio (sentiment) |
| Yahoo Finance | Insider transactions | Smart money flow |
| Yahoo Finance | Earnings calendar | Risk flag for upcoming events |
| Yahoo Finance | Company info | P/E, market cap, sector |
| `^VIX` | Volatility index | Market fear gauge |
| `SPY` | S&P 500 1-day change | Broad market context |

### Phase 1: Analyst Team (3 Agents)

| Agent | Model Tier | Role |
|-------|-----------|------|
| **Technical Analyst** | Deep | Interprets RSI, MACD, Bollinger, ATR, Stochastic, ADX, OBV, Fibonacci, VWAP, support/resistance, EMA crossovers, RSI divergence |
| **News Analyst** | Quick | Scans recent headlines, assesses sentiment, identifies catalysts and risks |
| **Fundamentals Analyst** | Quick | Evaluates valuation (P/E, market cap), financial health, growth vs value |

### Phase 2: Research Debate (Multi-Round)

| Step | Agent | What Happens |
|------|-------|-------------|
| 1 | **Bull Researcher** (deep) | Makes the strongest case for buying |
| 2 | **Bear Researcher** (deep) | Makes the strongest case for selling |
| 3 | **Bull Rebuttal** (deep) | Directly addresses bear's points |
| 4 | **Bear Counter** (deep) | Directly addresses bull's rebuttal |
| 5 | **Research Manager** (deep) | Reads full transcript, identifies surviving arguments, delivers verdict |

### Phase 3: Trade Proposal

The **Trader** agent converts the research verdict into a concrete proposal: entry price, target, stop-loss, position size, and timeframe. Uses ATR for volatility-adjusted stop placement.

### Phase 4: Risk Stress-Test (3-Way Debate)

| Agent | Persona | Argues For |
|-------|---------|------------|
| **Aggressive** | Risk-taker | Upside justifies the risk, size up, act now |
| **Conservative** | Capital protector | Hidden risks, size down, wait for confirmation |
| **Neutral** | Mediator | Where each side is right/wrong, balanced approach |

### Phase 5: Portfolio Manager (Final Decision)

Synthesizes all 10 prior agents into the **final decision** with a 5-level rating scale:

```
BUY ──── OVERWEIGHT ──── HOLD ──── UNDERWEIGHT ──── SELL
```

Includes short-term (1-5 day) and long-term (1-4 week) strategies with specific entry, target, stop-loss, risk/reward ratio, and position sizing.

---

## Comparison with Original TradingAgents

<table>
<tr><th>Feature</th><th>TradingAgents (Original)</th><th>DayTradeAgents (This Project)</th></tr>
<tr><td><b>Focus</b></td><td>General investment analysis</td><td>Day trading (1-5 day + 1-4 week)</td></tr>
<tr><td><b>Delivery</b></td><td>CLI / LangGraph</td><td>Telegram bot + CLI</td></tr>
<tr><td><b>Framework</b></td><td>LangGraph + Redis + LangChain</td><td>Lightweight (direct API calls)</td></tr>
<tr><td><b>Dependencies</b></td><td>20+ packages</td><td>8 packages</td></tr>
<tr><td><b>Setup</b></td><td>Complex (Redis, multiple configs)</td><td>One script (<code>setup_ubuntu.sh</code>)</td></tr>
<tr><td><b>Position tracking</b></td><td>No</td><td>Yes — <code>ta NVDA 50 120.5</code></td></tr>
<tr><td><b>Indicators</b></td><td>Via external APIs</td><td>15+ built-in (ATR, Stochastic, ADX, OBV, Fibonacci, Signal Score)</td></tr>
<tr><td><b>Data sources</b></td><td>Price + News</td><td>+ Options + Insider + Earnings + VIX + SPY context</td></tr>
<tr><td><b>Signal Score</b></td><td>No</td><td>Composite -100 to +100 pre-analysis</td></tr>
<tr><td><b>Prediction chart</b></td><td>No</td><td>Candlestick + ATR forecast cone</td></tr>
<tr><td><b>Rating scale</b></td><td>BUY / HOLD / SELL</td><td>5-level: BUY / OVERWEIGHT / HOLD / UNDERWEIGHT / SELL</td></tr>
<tr><td><b>Risk debate</b></td><td>3-way (LangGraph)</td><td>3-way (lightweight sequential)</td></tr>
<tr><td><b>Lines of code</b></td><td>~5,000+</td><td>~2,200</td></tr>
</table>

---

## Quick Start

### Prerequisites
- Python 3.10+
- OpenAI or Anthropic API key
- Telegram bot token (from [@BotFather](https://t.me/BotFather))

### 1. Clone & Configure

```bash
git clone https://github.com/Zhaor3/DayTradeAgents.git
cd DayTradeAgents
cp .env.example .env
```

Edit `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL_QUICK=gpt-5-mini
LLM_MODEL_DEEP=gpt-5.2

TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

> Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot) on Telegram.

### 2. Install & Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python telegram_bot.py
```

### 3. Use on Telegram

```
ta NVDA              → Analyze (no position)
ta NVDA 50 120.5     → Analyze holding 50 shares at $120.50 avg
/status              → Check bot is alive
/help                → Show commands
```

---

## Ubuntu Server Deploy

One-command setup with systemd auto-start:

```bash
git clone https://github.com/Zhaor3/DayTradeAgents.git ~/DayTradeAgents
cd ~/DayTradeAgents
chmod +x setup_ubuntu.sh && ./setup_ubuntu.sh
```

Then:

```bash
nano ~/DayTradeAgents/.env              # Add your API keys
sudo systemctl start daytradeagents     # Start the bot
sudo systemctl status daytradeagents    # Check status
tail -f ~/DayTradeAgents/bot.log        # Live logs
```

---

## Project Structure

```
DayTradeAgents/
├── main.py                            # Interactive CLI
├── telegram_bot.py                    # Telegram bot (production)
├── config.py                          # Settings from .env
├── setup_ubuntu.sh                    # One-click Ubuntu deploy
├── requirements.txt
│
├── tradingagent/
│   ├── agents/
│   │   ├── llm_client.py             # OpenAI / Anthropic abstraction
│   │   ├── technical_analyst.py      # Phase 1 ─ Chart analysis
│   │   ├── news_analyst.py           # Phase 1 ─ Sentiment
│   │   ├── fundamentals_analyst.py   # Phase 1 ─ Valuation
│   │   ├── bull_researcher.py        # Phase 2 ─ Buy case + rebuttal
│   │   ├── bear_researcher.py        # Phase 2 ─ Sell case + counter
│   │   ├── research_manager.py       # Phase 2 ─ Judges debate
│   │   ├── trader.py                 # Phase 3 ─ Trade proposal
│   │   ├── risk_aggressive.py        # Phase 4 ─ Opportunity
│   │   ├── risk_conservative.py      # Phase 4 ─ Danger
│   │   ├── risk_neutral.py           # Phase 4 ─ Balance
│   │   ├── portfolio_manager.py      # Phase 5 ─ Final decision
│   │   └── pipeline.py               # Orchestrator
│   │
│   ├── data/
│   │   ├── market_data.py            # yfinance + options + insider
│   │   └── indicators.py             # 15+ technical indicators
│   │
│   └── charts/
│       └── price_chart.py            # Prediction chart generator
```

---

## Technical Indicators

<table>
<tr><th>Indicator</th><th>Signal Type</th><th>What It Measures</th></tr>
<tr><td>RSI (14)</td><td>Momentum</td><td>Overbought / oversold conditions</td></tr>
<tr><td>MACD</td><td>Trend</td><td>Trend direction and momentum shifts</td></tr>
<tr><td>Bollinger Bands</td><td>Volatility</td><td>Price envelope and squeeze detection</td></tr>
<tr><td>ATR (14)</td><td>Volatility</td><td>Average range for stop-loss placement</td></tr>
<tr><td>Stochastic %K/%D</td><td>Momentum</td><td>Fast overbought/oversold (complements RSI)</td></tr>
<tr><td>ADX (14)</td><td>Trend Strength</td><td>Whether a trend is tradeable (>25) or ranging</td></tr>
<tr><td>OBV</td><td>Volume</td><td>Volume-confirmed price moves</td></tr>
<tr><td>Fibonacci Retracement</td><td>Support/Resistance</td><td>Key levels at 38.2%, 50%, 61.8%</td></tr>
<tr><td>VWAP</td><td>Fair Value</td><td>Institutional volume-weighted average</td></tr>
<tr><td>ROC (12)</td><td>Momentum</td><td>Rate of price acceleration</td></tr>
<tr><td>RSI Divergence</td><td>Reversal</td><td>Price/RSI disagreement (high-accuracy signal)</td></tr>
<tr><td>EMA 9/21 Cross</td><td>Trend</td><td>Golden cross / death cross detection</td></tr>
<tr><td>Signal Alignment</td><td>Composite</td><td>-100 to +100 aggregate score</td></tr>
</table>

---

## LLM Configuration

Two-tier model system for cost optimization:

| Tier | Default Model | Used By |
|------|--------------|---------|
| **Deep** | `gpt-5.2` | Technical analyst, bull/bear research, research manager, portfolio manager |
| **Quick** | `gpt-5-mini` | News, fundamentals, trader, risk debate, report formatting |

Supports **OpenAI** and **Anthropic** — set `LLM_PROVIDER` in `.env`.

---

## Credits & Acknowledgments

This project was inspired by and built upon the ideas from:

- **[TradingAgents](https://github.com/TauricResearch/TradingAgents)** by [Tauric Research](https://tradingagents-ai.github.io/) — the multi-agent debate architecture for financial analysis. Their work on bull/bear researcher debates, risk management committees, and portfolio manager synthesis informed the core design of this project.
- **[Yahoo Finance](https://finance.yahoo.com/)** via [yfinance](https://github.com/ranaroussi/yfinance) — free market data

---

## Disclaimer

> This is an AI-generated analysis tool for **informational and educational purposes only**. It is **not financial advice**. Always do your own research before making trading decisions. Trading involves significant risk of loss. Past performance of any analysis system does not guarantee future results.

---

<div align="center">

**MIT License** | Made with AI

</div>
