"""Shared pytest fixtures for TradingAgentV2 tests."""

import sys
import os
import pickle

import pytest
import pandas as pd
import numpy as np

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def sample_data():
    """Load saved AAPL historical data fixture.

    If fixture file doesn't exist, generates synthetic data on the fly.
    """
    pkl_path = os.path.join(FIXTURE_DIR, "aapl_data.pkl")
    if os.path.exists(pkl_path):
        with open(pkl_path, "rb") as f:
            return pickle.load(f)

    # Fallback: generate synthetic data for testing
    return _generate_synthetic_data()


def _generate_synthetic_data():
    """Generate synthetic but realistic stock data for testing without yfinance."""
    np.random.seed(42)
    n_long = 126  # ~6 months of trading days
    n_short = 21  # ~1 month

    # Generate a realistic price series starting at $170, trending up to ~$190
    base_price = 170.0
    daily_returns = np.random.normal(0.001, 0.015, n_long)
    prices = base_price * np.cumprod(1 + daily_returns)

    dates_long = pd.bdate_range(end="2024-01-30", periods=n_long, tz="US/Eastern")

    daily_long = pd.DataFrame({
        "Open": prices * (1 + np.random.normal(0, 0.003, n_long)),
        "High": prices * (1 + np.abs(np.random.normal(0.005, 0.005, n_long))),
        "Low": prices * (1 - np.abs(np.random.normal(0.005, 0.005, n_long))),
        "Close": prices,
        "Volume": np.random.randint(30_000_000, 80_000_000, n_long),
    }, index=dates_long)
    daily_long.index.name = "Date"

    daily_short = daily_long.tail(n_short).copy()

    # Intraday: 5 days x 26 bars per day
    intraday_rows = []
    for day_idx in range(-5, 0):
        day = daily_short.iloc[day_idx]
        base_time = daily_short.index[day_idx].replace(hour=9, minute=30)
        for i in range(26):
            t = base_time + pd.Timedelta(minutes=15 * i)
            frac = i / 25
            price = day["Open"] + (day["Close"] - day["Open"]) * frac
            noise = np.random.normal(0, 0.3)
            intraday_rows.append({
                "Datetime": t,
                "Open": round(price + noise, 2),
                "High": round(price + abs(noise) + 0.3, 2),
                "Low": round(price - abs(noise) - 0.3, 2),
                "Close": round(price - noise * 0.5, 2),
                "Volume": int(day["Volume"] / 26 + np.random.randint(-5000, 5000)),
            })
    intraday = pd.DataFrame(intraday_rows).set_index("Datetime")

    last = daily_short.iloc[-1]
    prev = daily_short.iloc[-2]

    return {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "current_price": round(float(last["Close"]), 2),
        "previous_close": round(float(prev["Close"]), 2),
        "open_price": round(float(last["Open"]), 2),
        "day_high": round(float(last["High"]), 2),
        "day_low": round(float(last["Low"]), 2),
        "volume": int(last["Volume"]),
        "avg_volume": int(daily_short["Volume"].mean()),
        "market_cap": 2890000000000,
        "pe_ratio": 29.5,
        "week_52_high": round(float(daily_long["High"].max()), 2),
        "week_52_low": round(float(daily_long["Low"].min()), 2),
        "beta": 1.28,
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "intraday": intraday,
        "daily_short": daily_short,
        "daily_long": daily_long,
        "news": [
            {"title": "Apple Vision Pro Pre-Orders Open", "publisher": "Bloomberg",
             "date": "2024-01-15", "summary": "Apple opens pre-orders for Vision Pro."},
            {"title": "iPhone Sales Slow in China", "publisher": "WSJ",
             "date": "2024-01-10", "summary": "Huawei cutting into Apple market share."},
        ],
        "insider_buys": 2,
        "insider_sells": 5,
        "days_to_earnings": 12,
        "put_call_ratio": 0.85,
        "vix": 13.5,
        "spy_change_1d": 0.35,
    }


# Canned LLM responses for mocking the pipeline
MOCK_LLM_RESPONSES = {
    "technical": """TREND: AAPL is in a short-term downtrend after failing to hold $192 support.
Long-term trend remains bullish above the 200-day SMA.

MOMENTUM: RSI at 42 is neutral but declining. MACD histogram is negative and widening,
suggesting increasing bearish momentum. Volume is below average at 0.85x.

KEY LEVELS: Immediate support at $188.50 (recent low). Resistance at $192.50 (broken support).
Major support at $185 (50-day SMA). Overhead resistance at $195.

SIGNALS: Bearish - price below VWAP, declining RSI, negative MACD crossover.
One positive: RSI not yet oversold, leaving room for a bounce.""",

    "news": """SENTIMENT: Mixed to slightly bearish.

CATALYSTS: Vision Pro pre-orders show innovation pipeline is active (mild positive).
Record services revenue demonstrates business diversification.

RISKS: iPhone sales slowdown in China is the dominant concern. Huawei competition
is a structural headwind. China represents ~19% of Apple revenue.

IMPACT: Near-term negative pressure from China concerns outweighs Vision Pro excitement.
Services growth provides a floor. Net sentiment: SLIGHTLY BEARISH for next 1-2 weeks.""",

    "fundamentals": """VALUATION: P/E of 29.5x is above historical average (~25x) but justified by services growth.
Market cap of $2.89T makes it the world's most valuable company.

FINANCIAL HEALTH: Strong balance sheet with $162B cash. Free cash flow of $110B/year.
Dividend yield ~0.5%, share buybacks provide additional shareholder returns.

CATALYST: Vision Pro launch could drive sentiment. Services margin expansion is the real story.

TRADING IMPLICATION: At current valuation, limited upside unless services growth accelerates.
Any China deterioration could push P/E compression. Fair value range: $180-$200.""",

    "bull": """BULL CASE FOR AAPL:

1. Services revenue hitting records with 70%+ margins vs 36% for products
2. Vision Pro creates entirely new revenue stream and platform ecosystem
3. $110B annual free cash flow funds massive buybacks reducing share count
4. AI integration into iOS/macOS ecosystem creates sticky user base
5. Near oversold RSI suggests bounce from $188 support zone

ENTRY: $188-189 on pullback
TARGET 1: $195 (prior resistance)
TARGET 2: $200 (round number psychological level)
CONVICTION: Moderate - fundamentals strong but valuation stretched""",

    "bear": """BEAR CASE FOR AAPL:

1. China iPhone sales declining while Huawei gains share - structural risk
2. P/E of 29.5x leaves no margin of safety at current levels
3. Vision Pro at $3,499 will be niche product, not a mass-market catalyst
4. MACD negative crossover with declining momentum
5. Price below VWAP and trending below key moving averages

DOWNSIDE TARGET 1: $185 (50-day SMA)
DOWNSIDE TARGET 2: $178 (200-day SMA)
CONVICTION: Moderate - China headwinds real but services growth provides floor""",

    "bull_rebuttal": """Rebutting bear concerns:
1. China sales are cyclical, not structural - Apple retained premium positioning
2. P/E premium is justified by ecosystem lock-in and services margin expansion
3. Vision Pro is a platform play, not just a product - developer ecosystem matters
4. Technical weakness is short-term; longer-term trend remains firmly bullish
The bear overstates China risk while undervaluing the services transformation.""",

    "bear_counter": """Countering bull's rebuttal:
1. 'Cyclical not structural' is wishful thinking - Huawei's comeback is real
2. Services growth is already priced in at 29.5x - where's the upside surprise?
3. Vision Pro developer adoption is unproven at this price point
4. 'Long-term bullish' doesn't help day traders - near-term momentum is bearish
The bull case relies on future narratives while ignoring present deterioration.""",

    "verdict": """RESEARCH VERDICT:

SURVIVING BULL POINTS:
- Services revenue transformation is real and underappreciated
- Free cash flow and buybacks provide strong support floor

SURVIVING BEAR POINTS:
- China revenue risk is genuine and near-term
- Valuation leaves limited upside at current levels

CONCESSIONS: Both sides agree $185 is critical support. Both acknowledge Vision Pro impact is uncertain.

VERDICT: SLIGHTLY BEARISH
CONFIDENCE: Medium
KEY CONDITION: Hold $185 support or verdict flips to strongly bearish
RECOMMENDED BIAS SCORE: -15 (mild bearish lean)""",

    "trade": """ACTION: HOLD (watch for entry)
ENTRY: $185-186 (wait for pullback to 50-day SMA)
TARGET 1: $192 (5% upside)
TARGET 2: $198 (7% upside)
STOP LOSS: $182 (below key support, ~1.5x ATR)
POSITION SIZE: 3-5% of portfolio
TIMEFRAME: 5-10 trading days
RATIONALE: Wait for better entry at support. Risk/reward unfavorable at current $189 level.""",

    "risk_aggressive": """The trade proposal is too conservative. AAPL at $189 is already near support.

UPSIDE ARGUMENT:
- Services growth + buybacks = structural floor at $185
- Vision Pro pre-orders could surprise to the upside
- RSI approaching oversold = high probability bounce zone
- Risk/reward from $189 to $195 is 3:1 with $187 stop

RECOMMENDATION: Enter 50% position now at $189, add remaining 50% at $186.
Position size: 5-7% of portfolio. This pullback is a gift for long-term holders.""",

    "risk_conservative": """The aggressive view ignores key dangers:

DOWNSIDE RISKS:
- China revenue deterioration could accelerate
- If $185 breaks, next support is $178 (200-day SMA) = 5% further downside
- Earnings in 12 days adds binary event risk
- VIX at 13.5 means complacency - vol expansion likely

RECOMMENDATION: Stay flat until post-earnings clarity. If must trade,
max 2% position size with hard stop at $183. The risk/reward does NOT justify
aggressive positioning ahead of earnings.""",

    "risk_neutral": """MEDIATING BOTH VIEWS:

The aggressive analyst correctly identifies the support bounce opportunity.
The conservative analyst rightly flags earnings risk and China headwinds.

BALANCED RECOMMENDATION:
- Enter SMALL position (2-3% of portfolio) at $188-189
- Set stop at $184 (below 50-day SMA, tight but logical)
- Take profits at $193-194 (prior resistance)
- Do NOT add to position before earnings
- Risk per trade: ~$5/share = $500 per 100 shares
- If stopped out, reassess after earnings""",

    "decision": """===== FINAL DECISION =====
Rating: HOLD
Confidence: Medium
Reasoning: AAPL presents a mixed picture with strong fundamentals but near-term headwinds from China and stretched valuation. Wait for better entry near $185 support or post-earnings clarity.

===== SHORT-TERM PLAY (1-5 Days) =====
Direction: Neutral to Bearish
Entry: $185.00
Target: $192.00 (3.8% gain)
Stop Loss: $182.00 (1.6% risk)
Risk/Reward: 1:2.3
Timeframe: 3-5 days
What To Do: Wait for pullback to $185 50-day SMA support. Do not chase at current levels.

===== LONG-TERM PLAY (1-4 Weeks) =====
Direction: Bullish
Entry: $185.00
Target: $200.00 (8.1% gain)
Stop Loss: $178.00 (3.8% risk)
Risk/Reward: 1:2.1
Timeframe: 2-4 weeks
What To Do: Accumulate on weakness toward $185. Services growth thesis intact for medium term.

===== RISK MANAGEMENT =====
Risk Level: Medium
Position Size: 3% of portfolio
Max Loss: $700 per 100 shares
Earnings Risk: WARNING - earnings in ~12 days, binary event risk
Key Danger: Break below $185 invalidates the bull thesis
Exit Rules: Hard stop at $182 short-term, $178 long-term. Exit if China data worsens.

===== TEAM SUMMARY =====
Signal Score: -15/100 - Bearish
Bull Case: Services growth + buybacks provide structural floor - Strength: Moderate
Bear Case: China headwinds + stretched valuation cap upside - Strength: Moderate
Research Verdict: Slightly bearish, wait for better entry
Risk Debate Winner: Conservative / Balanced
Key Disagreement: Timing - aggressive wants to buy now, conservative wants to wait for earnings

===== WHAT CHANGES THIS RATING =====
Upgrade If: Price holds $185 support + positive earnings surprise + China stabilization
Downgrade If: Break below $185 + earnings miss + further China deterioration""",
}
