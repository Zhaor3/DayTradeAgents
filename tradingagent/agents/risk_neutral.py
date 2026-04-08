"""Neutral Risk Analyst - mediates between aggressive and conservative."""

from .llm_client import call_llm

SYSTEM_PROMPT = """You are the Neutral Risk Analyst. You mediate between the aggressive and
conservative analysts. Your role is to:
- Identify where each side is right and wrong
- Find the balanced middle ground
- Suggest practical risk management (position sizing, scaling in/out)
- Highlight what BOTH sides are missing

You are pragmatic, not emotional. Under 250 words."""


def argue(data: dict, trade_proposal: str, aggressive_arg: str, conservative_arg: str) -> str:
    """Mediate between aggressive and conservative views."""
    user_prompt = f"""{data['ticker']} at ${data['current_price']}
VIX: {data.get('vix', 'N/A')} | Days to Earnings: {data.get('days_to_earnings', 'N/A')}

TRADE PROPOSAL:
{trade_proposal}

AGGRESSIVE ANALYST SAYS:
{aggressive_arg}

CONSERVATIVE ANALYST SAYS:
{conservative_arg}

Mediate. Where is each side right? What's the balanced approach?"""

    return call_llm(SYSTEM_PROMPT, user_prompt, deep=False)
