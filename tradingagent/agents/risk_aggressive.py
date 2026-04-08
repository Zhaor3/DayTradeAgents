"""Aggressive Risk Analyst - champions opportunity, challenges caution."""

from .llm_client import call_llm

SYSTEM_PROMPT = """You are the Aggressive Risk Analyst. You believe in calculated risk-taking
and champion high-reward opportunities. Your role in the risk debate is to argue that:
- The proposed trade's upside justifies the risk
- Conservative concerns are overblown
- Position size should be meaningful (not a tiny test position)
- Volatility is opportunity, not just danger

You still respect stop-losses, but you push for action over paralysis.
Directly address the other analysts' points when rebutting. Under 250 words."""


def argue(data: dict, trade_proposal: str, other_arguments: str = "") -> str:
    """Make the aggressive case for the trade."""
    context = f"TRADE PROPOSAL:\n{trade_proposal}"
    if other_arguments:
        context += f"\n\nOTHER RISK ANALYSTS SAID:\n{other_arguments}"

    user_prompt = f"""{data['ticker']} at ${data['current_price']}
VIX: {data.get('vix', 'N/A')} | Days to Earnings: {data.get('days_to_earnings', 'N/A')}
Put/Call: {data.get('put_call_ratio', 'N/A')}

{context}

Argue for taking this trade with conviction. Why is the risk worth it?"""

    return call_llm(SYSTEM_PROMPT, user_prompt, deep=False)
