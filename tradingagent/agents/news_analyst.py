"""News Analyst Agent - analyzes recent news for trading sentiment."""

from .llm_client import call_llm

SYSTEM_PROMPT = """You are a financial news analyst specializing in day trading. You assess how
recent news affects a stock's short-term price movement.

Your analysis must be CONCISE. Focus on:
1. Overall sentiment (bullish, bearish, neutral)
2. Catalysts that could move the price in the next few days
3. Any risks from news events
4. How news might affect trading volume

Keep your response under 200 words. Use plain language."""


def analyze_news(data: dict) -> str:
    """Analyze recent news for trading sentiment."""
    news_text = ""
    if data["news"]:
        for i, item in enumerate(data["news"][:8], 1):
            news_text += f"{i}. [{item.get('publisher', 'Unknown')}] {item.get('title', 'No title')}\n"
            if item.get("summary"):
                news_text += f"   {item['summary'][:150]}\n"
    else:
        news_text = "No recent news available."

    user_prompt = f"""Analyze the news sentiment for day trading:

STOCK: {data['ticker']} ({data['company_name']})
SECTOR: {data['sector']} | INDUSTRY: {data['industry']}
CURRENT PRICE: ${data['current_price']}

RECENT NEWS:
{news_text}

Provide:
1. SENTIMENT: Overall news sentiment (Bullish / Bearish / Neutral)
2. KEY CATALYSTS: What news could move the price in the next 1-5 days
3. RISKS: Any negative news or upcoming risks
4. IMPACT: Expected impact on trading (high/medium/low)"""

    return call_llm(SYSTEM_PROMPT, user_prompt)
