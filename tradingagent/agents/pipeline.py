"""Analysis pipeline - 13-agent deep analysis with debates and prediction chart.

Pipeline (mirrors professional quant firm structure):
  Phase 0: Data Collection + Indicator Engine
  Phase 1: Analyst Team (3 agents)
     [1] Technical Analyst (deep) | [2] News Analyst (quick) | [3] Fundamentals (quick)
  Phase 2: Research Debate (3 agents, multi-round)
     [4] Bull Researcher (deep) -> [5] Bear Researcher (deep) -> Bull rebuts -> Bear counters
     [6] Research Manager judges full debate (deep)
  Phase 3: Trade Proposal (1 agent)
     [7] Trader converts verdict to concrete proposal (quick)
  Phase 4: Risk Stress-Test (3-way debate)
     [8] Aggressive Risk (quick) -> [9] Conservative Risk (quick) -> [10] Neutral mediator (quick)
  Phase 5: Final Decision (1 agent)
     [11] Portfolio Manager synthesizes everything (deep)
  Phase 6: Chart Generation
     Price prediction chart with forecast cone

Total: ~15 LLM calls | Target runtime: 4-7 minutes
"""

from tradingagent.data.market_data import fetch_stock_data
from tradingagent.data.indicators import compute_all_indicators
from tradingagent.charts.price_chart import generate_chart

from .technical_analyst import analyze_technicals
from .news_analyst import analyze_news
from .fundamentals_analyst import analyze_fundamentals
from .bull_researcher import research_bull_case, rebut_bear_case
from .bear_researcher import research_bear_case, rebut_bull_case
from .research_manager import judge_debate
from .trader import create_trade_proposal
from .risk_aggressive import argue as argue_aggressive
from .risk_conservative import argue as argue_conservative
from .risk_neutral import argue as argue_neutral
from .portfolio_manager import final_decision


def run_analysis(ticker: str, holdings: dict, on_status=None) -> dict:
    """Run the full 13-agent deep analysis pipeline."""
    def status(msg):
        if on_status:
            on_status(msg)

    # ══════════════════════════════════════════════════════════════════════════
    # Phase 0: Data Collection
    # ══════════════════════════════════════════════════════════════════════════
    status("Phase 0: Fetching market data (price, options, insider, VIX)...")
    data = fetch_stock_data(ticker)

    if data["current_price"] == 0:
        raise ValueError(f"Could not find valid data for ticker '{ticker}'.")

    status("Phase 0: Computing indicators (RSI, MACD, ATR, Stochastic, ADX, Fibonacci)...")
    indicators = compute_all_indicators(data)

    # ══════════════════════════════════════════════════════════════════════════
    # Phase 1: Analyst Team
    # ══════════════════════════════════════════════════════════════════════════
    status("Phase 1 [1/11]: Technical Analyst reviewing charts... (deep)")
    technical_report = analyze_technicals(data, indicators)

    status("Phase 1 [2/11]: News Analyst scanning headlines...")
    news_report = analyze_news(data)

    status("Phase 1 [3/11]: Fundamentals Analyst evaluating valuation...")
    fundamentals_report = analyze_fundamentals(data)

    # ══════════════════════════════════════════════════════════════════════════
    # Phase 2: Research Debate (multi-round)
    # ══════════════════════════════════════════════════════════════════════════
    status("Phase 2 [4/11]: Bull Researcher opening argument... (deep)")
    bull_case = research_bull_case(data, indicators, technical_report, news_report, fundamentals_report)

    status("Phase 2 [5/11]: Bear Researcher counterargument... (deep)")
    bear_case = research_bear_case(data, indicators, technical_report, news_report, fundamentals_report)

    # Round 2: Rebuttals
    status("Phase 2 [debate]: Bull rebuts bear's points... (deep)")
    bull_rebuttal = rebut_bear_case(data, bull_case, bear_case)

    status("Phase 2 [debate]: Bear counters bull's rebuttal... (deep)")
    bear_counter = rebut_bull_case(data, bear_case, bull_rebuttal)

    # Build full debate transcript
    full_debate = (
        f"=== BULL OPENING ===\n{bull_case}\n\n"
        f"=== BEAR OPENING ===\n{bear_case}\n\n"
        f"=== BULL REBUTTAL ===\n{bull_rebuttal}\n\n"
        f"=== BEAR COUNTER ===\n{bear_counter}"
    )

    status("Phase 2 [6/11]: Research Manager judging debate... (deep)")
    research_verdict = judge_debate(data, full_debate, "")

    # ══════════════════════════════════════════════════════════════════════════
    # Phase 3: Trade Proposal
    # ══════════════════════════════════════════════════════════════════════════
    status("Phase 3 [7/11]: Trader creating concrete proposal...")
    trade_proposal = create_trade_proposal(data, indicators, research_verdict)

    # ══════════════════════════════════════════════════════════════════════════
    # Phase 4: Risk Stress-Test (3-way debate)
    # ══════════════════════════════════════════════════════════════════════════
    status("Phase 4 [8/11]: Aggressive Risk Analyst arguing...")
    risk_agg = argue_aggressive(data, trade_proposal)

    status("Phase 4 [9/11]: Conservative Risk Analyst arguing...")
    risk_con = argue_conservative(data, trade_proposal, risk_agg)

    status("Phase 4 [10/11]: Neutral Risk Analyst mediating...")
    risk_neu = argue_neutral(data, trade_proposal, risk_agg, risk_con)

    # ══════════════════════════════════════════════════════════════════════════
    # Phase 5: Final Decision
    # ══════════════════════════════════════════════════════════════════════════
    status("Phase 5 [11/11]: Portfolio Manager making FINAL decision... (deep)")
    decision_report = final_decision(
        data, indicators, holdings,
        technical_report, news_report, fundamentals_report,
        research_verdict, trade_proposal,
        risk_agg, risk_con, risk_neu,
    )

    # ══════════════════════════════════════════════════════════════════════════
    # Phase 6: Chart Generation
    # ══════════════════════════════════════════════════════════════════════════
    status("Phase 6: Generating prediction chart...")
    chart_path = None
    try:
        chart_path = generate_chart(data, indicators, decision_report)
    except Exception as e:
        print(f"[WARN] Chart generation failed: {e}")

    status("Analysis complete!")

    return {
        "data": data,
        "indicators": indicators,
        "technical_report": technical_report,
        "news_report": news_report,
        "fundamentals_report": fundamentals_report,
        "bull_case": bull_case,
        "bear_case": bear_case,
        "bull_rebuttal": bull_rebuttal,
        "bear_counter": bear_counter,
        "research_verdict": research_verdict,
        "trade_proposal": trade_proposal,
        "risk_aggressive": risk_agg,
        "risk_conservative": risk_con,
        "risk_neutral": risk_neu,
        "decision_report": decision_report,
        "chart_path": chart_path,
    }
