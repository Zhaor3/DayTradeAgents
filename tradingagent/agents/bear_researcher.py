"""Bear Researcher Agent - argues against buying, responds to bull's points."""

from .llm_client import call_llm

SYSTEM_PROMPT_INITIAL = """You are a cautious bear researcher. Make the STRONGEST case for
why this stock should be SOLD or AVOIDED right now. Use data, not fear. Be specific with
price levels showing downside risk. Under 400 words."""

SYSTEM_PROMPT_REBUTTAL = """You are a cautious bear researcher. The bull researcher just
rebutted your sell thesis. Read their argument carefully and COUNTER their points.
Strengthen your bear case with data. Concede where they're right but explain why the
risk is still too high. Under 300 words."""


def research_bear_case(data: dict, indicators: dict, technical_report: str,
                       news_report: str, fundamentals_report: str) -> str:
    """Build the initial bear case."""
    user_prompt = f"""Make the BEAR CASE against {data['ticker']} at ${data['current_price']}:

KEY DATA:
- RSI: {indicators.get('rsi_14', 'N/A')} | MACD Hist: {indicators.get('macd_histogram', 'N/A')}
- Signal Score: {indicators.get('signal_score', 'N/A')} ({indicators.get('signal_label', 'N/A')})
- Stochastic %K: {indicators.get('stochastic_k', 'N/A')} | ADX: {indicators.get('adx', 'N/A')}
- ATR: {indicators.get('atr_14', 'N/A')} | Volume Ratio: {indicators.get('volume_ratio', 'N/A')}x
- RSI Divergence: {indicators.get('rsi_divergence', 'N/A')} | EMA Cross: {indicators.get('ema_cross', 'N/A')}
- Support: {indicators.get('support_levels', [])} | Resistance: {indicators.get('resistance_levels', [])}
- Fibonacci: {indicators.get('fibonacci', 'N/A')}
- Insider Buys: {data.get('insider_buys', 0)} | Sells: {data.get('insider_sells', 0)}
- Days to Earnings: {data.get('days_to_earnings', 'N/A')}
- Put/Call Ratio: {data.get('put_call_ratio', 'N/A')}
- VIX: {data.get('vix', 'N/A')} | SPY 1D: {data.get('spy_change_1d', 'N/A')}%

TECHNICAL: {technical_report[:800]}
NEWS: {news_report[:500]}
FUNDAMENTALS: {fundamentals_report[:500]}

Present: WHY SELL/AVOID, DANGER ZONE, DOWNSIDE TARGETS, KEY RISKS, WHY BULLS ARE WRONG"""

    return call_llm(SYSTEM_PROMPT_INITIAL, user_prompt, deep=True)


def rebut_bull_case(data: dict, bear_case: str, bull_rebuttal: str) -> str:
    """Counter the bull's rebuttal."""
    user_prompt = f"""Stock: {data['ticker']} at ${data['current_price']}

YOUR ORIGINAL BEAR CASE:
{bear_case}

BULL'S REBUTTAL:
{bull_rebuttal}

Counter the bull's strongest points. Strengthen your bear case."""

    return call_llm(SYSTEM_PROMPT_REBUTTAL, user_prompt, deep=True)
