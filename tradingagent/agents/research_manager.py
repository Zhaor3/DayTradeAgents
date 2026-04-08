"""Research Manager Agent - judges the full multi-round bull vs bear debate."""

from .llm_client import call_llm

SYSTEM_PROMPT = """You are the Research Manager. You just observed a FULL multi-round debate
between the Bull Researcher (wants to BUY) and Bear Researcher (wants to SELL/AVOID).

Each side made opening arguments AND directly rebutted each other's points.

Your job:
1. Identify which arguments survived the rebuttals
2. Note which points each side CONCEDED
3. Weigh the surviving arguments
4. Make a clear VERDICT

Be decisive. Under 400 words."""


def judge_debate(data: dict, full_debate: str, extra_context: str) -> str:
    """Judge the full multi-round debate."""
    user_prompt = f"""Judge this bull vs bear debate for {data['ticker']} at ${data['current_price']}:

{full_debate}

Deliver your VERDICT:
1. SURVIVING BULL POINTS: Arguments that withstood the bear's rebuttal
2. SURVIVING BEAR POINTS: Arguments that withstood the bull's rebuttal
3. CONCESSIONS: What each side admitted the other was right about
4. VERDICT: BULLISH / BEARISH / NEUTRAL
5. CONFIDENCE: High / Medium / Low
6. KEY CONDITION: The ONE thing that would flip your verdict
7. RECOMMENDED BIAS: How heavily to lean into this direction (1-10 scale)"""

    return call_llm(SYSTEM_PROMPT, user_prompt, deep=True)
