"""Bull Researcher Agent - argues for buying, responds to bear's counterpoints."""

from .llm_client import call_llm

SYSTEM_PROMPT_INITIAL = """You are an aggressive bull researcher. Make the STRONGEST case for
why this stock should be BOUGHT right now. Use data, not hopium. Be specific with price
levels and targets. Under 400 words."""

SYSTEM_PROMPT_REBUTTAL = """You are an aggressive bull researcher. The bear researcher just
argued against your buy thesis. Read their argument carefully and REBUT their strongest
points. Defend your bull case with data. Concede where they're right but explain why the
buy case still holds. Under 300 words."""


def research_bull_case(data: dict, indicators: dict, technical_report: str,
                       news_report: str, fundamentals_report: str) -> str:
    """Build the initial bull case."""
    user_prompt = f"""Make the BULL CASE for buying {data['ticker']} at ${data['current_price']}:

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

Present: WHY BUY, ENTRY ZONE, TARGETS, CATALYST, WHY BEARS ARE WRONG"""

    return call_llm(SYSTEM_PROMPT_INITIAL, user_prompt, deep=True)


def rebut_bear_case(data: dict, bull_case: str, bear_case: str) -> str:
    """Rebut the bear's arguments."""
    user_prompt = f"""Stock: {data['ticker']} at ${data['current_price']}

YOUR ORIGINAL BULL CASE:
{bull_case}

BEAR'S COUNTERARGUMENT:
{bear_case}

Rebut the bear's strongest points. Defend your buy case."""

    return call_llm(SYSTEM_PROMPT_REBUTTAL, user_prompt, deep=True)
