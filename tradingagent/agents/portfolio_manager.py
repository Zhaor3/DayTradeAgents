"""Portfolio Manager Agent - synthesizes everything into the FINAL decision."""

from .llm_client import call_llm

SYSTEM_PROMPT = """You are the Portfolio Manager. You make the FINAL trading decision after
reviewing ALL team analysis: analysts, bull/bear debate, trader proposal, and the
three-way risk debate.

You MUST output in EXACTLY this format:

===== FINAL DECISION =====
Rating: [BUY / OVERWEIGHT / HOLD / UNDERWEIGHT / SELL]
Confidence: [High / Medium / Low]
Reasoning: [2-3 sentences]

===== SHORT-TERM PLAY (1-5 Days) =====
Direction: [Bullish / Bearish / Neutral]
Entry: $[price]
Target: $[price] ([X]% gain)
Stop Loss: $[price] ([X]% risk)
Risk/Reward: [ratio, e.g. 1:2.5]
Timeframe: [e.g. "2-3 days"]
What To Do: [2-3 sentences]

===== LONG-TERM PLAY (1-4 Weeks) =====
Direction: [Bullish / Bearish / Neutral]
Entry: $[price]
Target: $[price]
Stop Loss: $[price]
Risk/Reward: [ratio]
Timeframe: [e.g. "2-3 weeks"]
What To Do: [2-3 sentences]

===== RISK MANAGEMENT =====
Risk Level: [Low / Medium / High / Extreme]
Position Size: [specific % of portfolio]
Max Loss: $[amount] per 100 shares
Earnings Risk: [warning if earnings are near]
Key Danger: [1 sentence]
Exit Rules: [when to get out no matter what]

===== TEAM SUMMARY =====
Signal Score: [X/100] - [label]
Bull Case: [1 line summary] - Strength: [Strong/Moderate/Weak]
Bear Case: [1 line summary] - Strength: [Strong/Moderate/Weak]
Research Verdict: [1 line]
Risk Debate Winner: [Aggressive / Conservative / Balanced]
Key Disagreement: [what the team couldn't agree on]

===== WHAT CHANGES THIS RATING =====
Upgrade If: [conditions]
Downgrade If: [conditions]"""


def final_decision(data: dict, indicators: dict, holdings: dict,
                   technical_report: str, news_report: str, fundamentals_report: str,
                   research_verdict: str, trade_proposal: str,
                   risk_aggressive: str, risk_conservative: str, risk_neutral: str) -> str:
    """Make the absolute final decision using all inputs."""

    holding_info = ""
    if holdings["shares"] > 0:
        cost = holdings["avg_price"] * holdings["shares"]
        val = data["current_price"] * holdings["shares"]
        pnl = val - cost
        pnl_pct = (pnl / cost * 100) if cost > 0 else 0
        holding_info = f"HOLDING: {holdings['shares']} shares at ${holdings['avg_price']:.2f} | P&L: ${pnl:,.2f} ({pnl_pct:+.1f}%)"
    else:
        holding_info = "HOLDING: No position"

    user_prompt = f"""Make your FINAL decision for {data['ticker']} at ${data['current_price']}

{holding_info}

SIGNAL SCORE: {indicators.get('signal_score', 'N/A')}/100 ({indicators.get('signal_label', 'N/A')})
ATR: {indicators.get('atr_14', 'N/A')} | RSI: {indicators.get('rsi_14', 'N/A')} | ADX: {indicators.get('adx', 'N/A')}
VIX: {data.get('vix', 'N/A')} | Earnings in: {data.get('days_to_earnings', 'N/A')} days
Support: {indicators.get('support_levels', [])} | Resistance: {indicators.get('resistance_levels', [])}

=== TECHNICAL ANALYSIS ===
{technical_report[:600]}

=== NEWS ===
{news_report[:400]}

=== FUNDAMENTALS ===
{fundamentals_report[:400]}

=== RESEARCH MANAGER VERDICT ===
{research_verdict[:600]}

=== TRADER PROPOSAL ===
{trade_proposal}

=== AGGRESSIVE RISK ANALYST ===
{risk_aggressive[:400]}

=== CONSERVATIVE RISK ANALYST ===
{risk_conservative[:400]}

=== NEUTRAL RISK ANALYST ===
{risk_neutral[:400]}

Deliver your FINAL decision in the exact format specified."""

    return call_llm(SYSTEM_PROMPT, user_prompt, deep=True)
