"""Technical Analyst Agent - analyzes price action and indicators."""

from .llm_client import call_llm

SYSTEM_PROMPT = """You are an expert day-trading technical analyst. You analyze price data,
technical indicators, and chart patterns to provide actionable trading insights.

Your analysis must be CONCISE and ACTIONABLE. Focus on:
1. Trend direction (bullish, bearish, neutral) for both short and long term
2. Key support and resistance levels
3. Momentum signals (RSI, MACD)
4. Volume confirmation
5. Entry/exit price zones

Keep your response structured and under 300 words. Use plain language a regular trader can understand."""


def analyze_technicals(data: dict, indicators: dict) -> str:
    """Run technical analysis on the stock data."""
    user_prompt = f"""Analyze this stock for day trading opportunities:

STOCK: {data['ticker']} ({data['company_name']})
CURRENT PRICE: ${data['current_price']}
OPEN: ${data['open_price']} | HIGH: ${data['day_high']} | LOW: ${data['day_low']}
PREV CLOSE: ${data['previous_close']}
VOLUME: {data['volume']:,} (Avg: {data['avg_volume']:,})
52W HIGH: ${data['week_52_high']} | 52W LOW: ${data['week_52_low']}

TECHNICAL INDICATORS:
- RSI(14): {indicators.get('rsi_14', 'N/A')}
- RSI Intraday: {indicators.get('rsi_intraday', 'N/A')}
- MACD Line: {indicators.get('macd_line', 'N/A')} | Signal: {indicators.get('macd_signal', 'N/A')} | Histogram: {indicators.get('macd_histogram', 'N/A')}
- MACD Intraday: {indicators.get('macd_intraday', 'N/A')} | Signal: {indicators.get('macd_signal_intraday', 'N/A')}
- EMA(9): {indicators.get('ema_9', 'N/A')} | EMA(21): {indicators.get('ema_21', 'N/A')}
- SMA(10): {indicators.get('sma_10', 'N/A')} | SMA(20): {indicators.get('sma_20', 'N/A')}
- SMA(50): {indicators.get('sma_50', 'N/A')} | SMA(200): {indicators.get('sma_200', 'N/A')}
- Bollinger Upper: {indicators.get('bb_upper', 'N/A')} | Middle: {indicators.get('bb_middle', 'N/A')} | Lower: {indicators.get('bb_lower', 'N/A')}
- VWAP: {indicators.get('vwap', 'N/A')}
- Volume Ratio (vs 20d avg): {indicators.get('volume_ratio', 'N/A')}x

PRICE CHANGES:
- 1-Day: {indicators.get('change_1d', 'N/A')}%
- 5-Day: {indicators.get('change_5d', 'N/A')}%
- From 52W High: {indicators.get('pct_from_52w_high', 'N/A')}%
- From 52W Low: {indicators.get('pct_from_52w_low', 'N/A')}%

SUPPORT LEVELS (short-term): {indicators.get('support_levels', [])}
RESISTANCE LEVELS (short-term): {indicators.get('resistance_levels', [])}
SUPPORT LEVELS (long-term): {indicators.get('support_levels_long', [])}
RESISTANCE LEVELS (long-term): {indicators.get('resistance_levels_long', [])}

Provide your technical analysis covering:
1. TREND: Current short-term and long-term trend direction
2. MOMENTUM: What RSI, MACD, and volume are telling us
3. KEY LEVELS: Most important support/resistance to watch
4. SIGNALS: Any bullish or bearish signals you see"""

    return call_llm(SYSTEM_PROMPT, user_prompt, deep=True)
