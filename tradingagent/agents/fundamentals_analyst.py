"""Fundamentals Analyst Agent - analyzes financial health and valuation."""

from .llm_client import call_llm

SYSTEM_PROMPT = """You are a senior fundamentals analyst specializing in day trading context.
You evaluate a company's financial health, valuation, and how fundamentals support or
undermine the current price action.

Focus on:
1. Valuation: Is the stock overvalued, undervalued, or fairly valued at current price?
2. Financial health: Revenue trends, profitability, debt levels
3. Growth vs value: Is this a momentum/growth name or a value play?
4. How fundamentals support or contradict the current technical picture
5. Any fundamental catalysts (earnings, guidance, sector rotation)

Keep your response structured and under 300 words."""


def analyze_fundamentals(data: dict) -> str:
    """Run fundamentals analysis."""
    user_prompt = f"""Analyze the fundamentals for day trading context:

STOCK: {data['ticker']} ({data['company_name']})
CURRENT PRICE: ${data['current_price']}
SECTOR: {data['sector']} | INDUSTRY: {data['industry']}

VALUATION:
- P/E Ratio: {data.get('pe_ratio', 'N/A')}
- Market Cap: ${data['market_cap']:,}
- Beta: {data.get('beta', 'N/A')}

PRICE CONTEXT:
- 52-Week High: ${data['week_52_high']}
- 52-Week Low: ${data['week_52_low']}
- Current vs 52W High: {((data['current_price'] - data['week_52_high']) / data['week_52_high'] * 100):.1f}%

VOLUME:
- Today: {data['volume']:,}
- Average: {data['avg_volume']:,}

Provide:
1. VALUATION VERDICT: Overvalued / Fairly Valued / Undervalued at current price
2. FINANCIAL HEALTH: Key strength or weakness
3. FUNDAMENTAL CATALYST: Any upcoming or recent catalyst
4. TRADING IMPLICATION: How fundamentals affect the short-term trade setup"""

    return call_llm(SYSTEM_PROMPT, user_prompt, deep=False)
