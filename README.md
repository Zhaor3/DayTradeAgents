# TradingAgentV2

**AI-powered day trading assistant** with multi-agent debate architecture, delivered via Telegram bot.

Built on the ideas from [TradingAgents by Tauric Research](https://github.com/TauricResearch/TradingAgents), re-engineered for practical day trading with a streamlined codebase, deeper analysis pipeline, and real-time Telegram delivery.

---

## What It Does

Send `ta NVDA` to your Telegram bot and get back:

1. **A price prediction chart** with candlesticks, indicators, and ATR-based forecast cone
2. **A trade dashboard** with BUY / SELL / HOLD decision, confidence level, entry/target/stop-loss prices, and risk assessment

The system runs **11 AI agents** through a structured debate process before making a decision - the same kind of adversarial analysis used by professional quant firms.

<details>
<summary>Example Telegram output</summary>

```
TRADE DASHBOARD — NVDA
2026-04-08

Rating: BUY | Confidence: Medium

SHORT-TERM PLAY (1-5 Days)
- Entry: $112.50
- Target: $118.00 (4.9% gain)
- Stop Loss: $109.00 (3.1% risk)
- Risk/Reward: 1:1.6

LONG-TERM PLAY (1-4 Weeks)
- Entry: $113.00
- Target: $125.00
- Stop Loss: $107.00

RISK: Medium | Position: 5-8% of portfolio
Bull Case: Strong - oversold RSI + bullish divergence
Bear Case: Moderate - below all major MAs
```
</details>

---

## How It Works

### 6-Phase Pipeline (11 Agents, ~15 LLM Calls, 4-7 min)

```
Phase 0: DATA COLLECTION
         Yahoo Finance -> Price, Options, Insider, VIX, Earnings Calendar
         Indicator Engine -> RSI, MACD, ATR, Stochastic, ADX, OBV,
                            Fibonacci, Bollinger, VWAP, Signal Score

Phase 1: ANALYST TEAM (3 agents)
         [1] Technical Analyst (deep model)
         [2] News Analyst
         [3] Fundamentals Analyst

Phase 2: RESEARCH DEBATE (3 agents, multi-round)
         [4] Bull Researcher argues for buying
         [5] Bear Researcher argues for selling
              -> Bull rebuts Bear's points
              -> Bear counters Bull's rebuttal
         [6] Research Manager judges the full debate

Phase 3: TRADE PROPOSAL (1 agent)
         [7] Trader converts verdict into concrete entry/target/stop

Phase 4: RISK STRESS-TEST (3-way debate)
         [8]  Aggressive Risk Analyst - champions the opportunity
         [9]  Conservative Risk Analyst - highlights hidden dangers
         [10] Neutral Risk Analyst - mediates, finds balanced approach

Phase 5: FINAL DECISION (1 agent)
         [11] Portfolio Manager synthesizes everything
              -> 5-level rating: BUY / OVERWEIGHT / HOLD / UNDERWEIGHT / SELL
              -> Short-term strategy (1-5 days) with entry/target/stop
              -> Long-term strategy (1-4 weeks) with entry/target/stop
              -> Risk assessment with position sizing

Phase 6: CHART GENERATION
         Candlestick chart + indicator overlays + ATR prediction cone
```

### Architecture Diagram

```
                    ┌─────────────────────┐
                    │   Yahoo Finance     │
                    │  Price / Options /  │
                    │  Insider / VIX      │
                    └────────┬────────────┘
                             │
                    ┌────────▼────────────┐
                    │  Indicator Engine   │
                    │  15+ indicators     │
                    │  Signal Score       │
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼──────┐
        │ Technical │ │   News    │ │Fundamentals│
        │  Analyst  │ │  Analyst  │ │  Analyst   │
        └─────┬─────┘ └─────┬─────┘ └─────┬──────┘
              └──────────────┼──────────────┘
                             │
              ┌──────────────▼──────────────┐
              │      RESEARCH DEBATE        │
              │  Bull ←→ Bear (2 rounds)    │
              │  Research Manager judges     │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼────────────┐
                    │      Trader         │
                    │  Concrete proposal  │
                    └────────┬────────────┘
                             │
              ┌──────────────▼──────────────┐
              │      RISK DEBATE            │
              │  Aggressive ←→ Conservative │
              │  Neutral mediates           │
              └──────────────┬──────────────┘
                             │
                    ┌────────▼────────────┐
                    │  Portfolio Manager  │
                    │  FINAL DECISION     │
                    └────────┬────────────┘
                             │
                    ┌────────▼────────────┐
                    │   Chart + Report    │
                    │   -> Telegram       │
                    └─────────────────────┘
```

---

## vs. Original TradingAgents

This project was inspired by [TradingAgents](https://github.com/TauricResearch/TradingAgents) and shares the multi-agent debate philosophy. Here's what's different:

| Feature | TradingAgents (Original) | TradingAgentV2 (This) |
|---------|-------------------------|----------------------|
| **Focus** | General investment analysis | Day trading (1-5 day + 1-4 week) |
| **Delivery** | CLI / LangGraph | Telegram bot + CLI |
| **Framework** | LangGraph + Redis + LangChain | Lightweight (direct OpenAI/Anthropic API) |
| **Dependencies** | 20+ packages | 8 packages |
| **Setup** | Complex (Redis, multiple API keys) | One script (`setup_ubuntu.sh`) |
| **Position tracking** | No | Yes (`ta NVDA 50 120.5`) |
| **Indicators** | Via Alpha Vantage / yfinance | 15+ built-in (ATR, Stochastic, ADX, OBV, Fibonacci, Signal Score) |
| **Data sources** | Price + News | Price + News + Options + Insider + Earnings + VIX |
| **Signal Score** | No | Composite -100 to +100 pre-analysis score |
| **Prediction chart** | No | Candlestick + ATR forecast cone |
| **Multi-round debate** | Yes (LangGraph state machine) | Yes (sequential with full transcript) |
| **Risk debate** | 3-way (Aggressive/Conservative/Neutral) | 3-way (same approach, simpler code) |
| **Rating scale** | BUY/HOLD/SELL | BUY/OVERWEIGHT/HOLD/UNDERWEIGHT/SELL |
| **Memory system** | BM25-based reflection | Not yet (planned) |
| **Lines of code** | ~5,000+ | ~2,200 |

### Key Improvements
- **Practical day trading focus** - entry/target/stop with specific dollar prices and timeframes
- **Position-aware** - tells you to HOLD, SELL, or add based on your current P&L
- **15+ technical indicators** computed locally (no external API needed)
- **Market context** - VIX level, S&P 500 direction, put/call ratio, insider activity, earnings proximity
- **Signal Alignment Score** - objective composite score before agents start analyzing (reduces LLM narrative bias)
- **Price prediction chart** - visual forecast with ATR-based confidence cone
- **One-command deploy** - `setup_ubuntu.sh` handles everything

---

## Quick Start

### Prerequisites
- Python 3.10+
- An OpenAI or Anthropic API key
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))

### 1. Clone and configure

```bash
git clone https://github.com/Zhaor3/TradingAgentV2.git
cd TradingAgentV2
cp .env.example .env
```

Edit `.env` with your keys:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL_QUICK=gpt-5-mini
LLM_MODEL_DEEP=gpt-5.2

TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

> **Get your chat ID:** Message [@userinfobot](https://t.me/userinfobot) on Telegram.

### 2. Install and run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python telegram_bot.py
```

### 3. Use on Telegram

```
ta NVDA              - Analyze (no position)
ta NVDA 50 120.5     - Analyze holding 50 shares at $120.50 avg
/status              - Check bot is alive
/help                - Show commands
```

---

## Ubuntu Server Deploy (One Command)

```bash
git clone https://github.com/Zhaor3/TradingAgentV2.git ~/TradingAgentV2
cd ~/TradingAgentV2
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh
```

The setup script:
- Installs Python 3 + venv
- Creates virtual environment and installs deps
- Sets up a **systemd service** for auto-start on boot
- Creates the service at `/etc/systemd/system/tradingagentv2.service`

After setup:

```bash
# Edit your API keys
nano ~/TradingAgentV2/.env

# Start the bot as a service
sudo systemctl start tradingagentv2

# Check status
sudo systemctl status tradingagentv2

# View live logs
tail -f ~/TradingAgentV2/bot.log

# Stop / restart
sudo systemctl stop tradingagentv2
sudo systemctl restart tradingagentv2
```

---

## Project Structure

```
TradingAgentV2/
├── main.py                    # Interactive CLI (local testing)
├── telegram_bot.py            # Telegram bot (production)
├── config.py                  # Settings from .env
├── setup_ubuntu.sh            # One-click Ubuntu deployment
├── requirements.txt           # Python dependencies
├── .env.example               # API key template
│
├── tradingagent/
│   ├── agents/
│   │   ├── llm_client.py             # OpenAI / Anthropic abstraction
│   │   ├── technical_analyst.py      # Phase 1: Chart analysis (deep)
│   │   ├── news_analyst.py           # Phase 1: Headline sentiment
│   │   ├── fundamentals_analyst.py   # Phase 1: Valuation analysis
│   │   ├── bull_researcher.py        # Phase 2: Bull case + rebuttal
│   │   ├── bear_researcher.py        # Phase 2: Bear case + counter
│   │   ├── research_manager.py       # Phase 2: Judges debate
│   │   ├── trader.py                 # Phase 3: Concrete trade proposal
│   │   ├── risk_aggressive.py        # Phase 4: Champions opportunity
│   │   ├── risk_conservative.py      # Phase 4: Highlights danger
│   │   ├── risk_neutral.py           # Phase 4: Mediates
│   │   ├── portfolio_manager.py      # Phase 5: Final decision
│   │   └── pipeline.py               # Orchestrates all phases
│   │
│   ├── data/
│   │   ├── market_data.py            # yfinance data + options + insider
│   │   └── indicators.py             # 15+ technical indicators
│   │
│   ├── charts/
│   │   └── price_chart.py            # Prediction chart generator
│   │
│   └── report.py                     # Rich CLI report formatter
```

---

## Technical Indicators

All computed locally from yfinance data (no external API needed):

| Indicator | What It Measures |
|-----------|-----------------|
| RSI (14) | Overbought / oversold momentum |
| MACD | Trend direction and strength |
| Bollinger Bands | Volatility envelope |
| ATR (14) | Average volatility (used for stops) |
| Stochastic %K/%D | Fast overbought/oversold |
| ADX (14) | Trend strength (not direction) |
| OBV | Volume-confirmed price moves |
| Fibonacci Retracement | Key S/R levels (38.2%, 50%, 61.8%) |
| VWAP | Institutional fair value |
| ROC (12) | Momentum rate of change |
| RSI Divergence | Reversal detection |
| EMA 9/21 Cross | Golden/death cross signals |
| Signal Alignment Score | Composite -100 to +100 |

---

## LLM Models

The system uses two model tiers:

| Tier | Default | Used For |
|------|---------|----------|
| **Deep** | `gpt-5.2` | Technical analysis, bull/bear research, research manager, risk advisor, portfolio manager |
| **Quick** | `gpt-5-mini` | News, fundamentals, trader proposal, risk debate, report formatting |

Supports **OpenAI** and **Anthropic** (Claude). Set `LLM_PROVIDER` in `.env`.

---

## Credits

- Inspired by [TradingAgents](https://github.com/TauricResearch/TradingAgents) by [Tauric Research](https://github.com/TauricResearch) - the multi-agent debate architecture for financial analysis
- Market data from [Yahoo Finance](https://finance.yahoo.com/) via [yfinance](https://github.com/ranaroussi/yfinance)

## Disclaimer

This is an AI-generated analysis tool for **informational and educational purposes only**. It is **not financial advice**. Always do your own research before making any trading decisions. Past performance of this or any analysis system does not guarantee future results. Trading involves significant risk of loss.

## License

MIT
