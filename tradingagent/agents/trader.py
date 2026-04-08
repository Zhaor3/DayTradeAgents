"""Trader Agent - converts research verdict into a concrete trade proposal."""

from .llm_client import call_llm

SYSTEM_PROMPT = """You are an experienced day trader. You take the Research Manager's verdict
and convert it into a CONCRETE trade proposal with specific numbers.

You must output in this format:

TRADE PROPOSAL:
Action: [BUY / SELL / HOLD]
Entry: $[price]
Target 1: $[price] (partial take-profit)
Target 2: $[price] (full exit)
Stop Loss: $[price]
Position Size: [% of portfolio]
Timeframe: [e.g. "2-3 days"]
Rationale: [2-3 sentences]

Be precise with prices. Use ATR for stop-loss placement. Under 250 words."""


def create_trade_proposal(data: dict, indicators: dict, research_verdict: str) -> str:
    """Create a concrete trade proposal from research verdict."""
    user_prompt = f"""Create a specific trade proposal for {data['ticker']}:

PRICE: ${data['current_price']}
ATR(14): {indicators.get('atr_14', 'N/A')}
Support: {indicators.get('support_levels', [])}
Resistance: {indicators.get('resistance_levels', [])}
Fibonacci: {indicators.get('fibonacci', 'N/A')}
VWAP: ${indicators.get('vwap', 'N/A')}
Signal Score: {indicators.get('signal_score', 'N/A')} ({indicators.get('signal_label', 'N/A')})

RESEARCH VERDICT:
{research_verdict}

Convert this into a precise trade proposal with exact entry, targets, and stop-loss."""

    return call_llm(SYSTEM_PROMPT, user_prompt, deep=False)
