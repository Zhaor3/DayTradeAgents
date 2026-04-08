"""Conservative Risk Analyst - protects capital, highlights hidden dangers."""

from .llm_client import call_llm

SYSTEM_PROMPT = """You are the Conservative Risk Analyst. You protect capital above all else.
Your role in the risk debate is to argue that:
- Hidden risks the aggressive analyst is ignoring
- Position size should be smaller than proposed
- Stop-losses might not protect against gaps or black swans
- Opportunity cost of being wrong outweighs potential gains

You don't always say "don't trade" but you push for caution and smaller size.
Directly address the other analysts' points when rebutting. Under 250 words."""


def argue(data: dict, trade_proposal: str, other_arguments: str = "") -> str:
    """Make the conservative case against the trade's risk."""
    context = f"TRADE PROPOSAL:\n{trade_proposal}"
    if other_arguments:
        context += f"\n\nOTHER RISK ANALYSTS SAID:\n{other_arguments}"

    user_prompt = f"""{data['ticker']} at ${data['current_price']}
VIX: {data.get('vix', 'N/A')} | Days to Earnings: {data.get('days_to_earnings', 'N/A')}
Put/Call: {data.get('put_call_ratio', 'N/A')} | Beta: {data.get('beta', 'N/A')}

{context}

Argue for caution. What risks are being underestimated?"""

    return call_llm(SYSTEM_PROMPT, user_prompt, deep=False)
