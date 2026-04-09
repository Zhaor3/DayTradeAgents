"""Integration tests for the full analysis pipeline.

Mocks the LLM and market data to test the entire flow end-to-end.
"""

import pytest
from unittest.mock import patch, MagicMock

from tradingagent.agents.pipeline import run_analysis
from tradingagent.data.indicators import compute_all_indicators
from tests.conftest import MOCK_LLM_RESPONSES


def _mock_call_llm(system_prompt: str, user_prompt: str, deep: bool = False) -> str:
    """Return canned LLM responses based on system prompt content."""
    sp = system_prompt.lower()

    if "technical analyst" in sp:
        return MOCK_LLM_RESPONSES["technical"]
    elif "news" in sp and "sentiment" in sp:
        return MOCK_LLM_RESPONSES["news"]
    elif "fundamentals" in sp:
        return MOCK_LLM_RESPONSES["fundamentals"]
    elif "bull" in sp and "researcher" in sp:
        # Check user prompt for rebuttal context
        if "bear" in user_prompt.lower() and "rebuttal" in user_prompt.lower():
            return MOCK_LLM_RESPONSES["bull_rebuttal"]
        return MOCK_LLM_RESPONSES["bull"]
    elif "bear" in sp and "researcher" in sp:
        if "bull" in user_prompt.lower() and "rebuttal" in user_prompt.lower():
            return MOCK_LLM_RESPONSES["bear_counter"]
        return MOCK_LLM_RESPONSES["bear"]
    elif "research manager" in sp or "judge" in sp:
        return MOCK_LLM_RESPONSES["verdict"]
    elif "trader" in sp and "proposal" in sp:
        return MOCK_LLM_RESPONSES["trade"]
    elif "aggressive" in sp:
        return MOCK_LLM_RESPONSES["risk_aggressive"]
    elif "conservative" in sp:
        return MOCK_LLM_RESPONSES["risk_conservative"]
    elif "neutral" in sp and "risk" in sp:
        return MOCK_LLM_RESPONSES["risk_neutral"]
    elif "portfolio manager" in sp:
        return MOCK_LLM_RESPONSES["decision"]
    else:
        # Default fallback
        return MOCK_LLM_RESPONSES["decision"]


class TestFullPipeline:
    """Test the complete analysis pipeline with mocked LLM and data."""

    @patch("tradingagent.agents.pipeline.fetch_stock_data")
    @patch("tradingagent.agents.pipeline.generate_chart")
    @patch("tradingagent.agents.technical_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.news_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.fundamentals_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.bull_researcher.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.bear_researcher.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.research_manager.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.trader.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_aggressive.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_conservative.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_neutral.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.portfolio_manager.call_llm", side_effect=_mock_call_llm)
    def test_pipeline_returns_all_keys(
        self, mock_pm, mock_rn, mock_rc, mock_ra, mock_tr,
        mock_rm, mock_bear, mock_bull, mock_fund, mock_news, mock_tech,
        mock_chart, mock_fetch, sample_data
    ):
        """Pipeline should return dict with all expected report keys."""
        mock_fetch.return_value = sample_data
        mock_chart.return_value = "/tmp/test_chart.png"

        statuses = []
        results = run_analysis("AAPL", {"shares": 0, "avg_price": 0}, on_status=statuses.append)

        expected_keys = [
            "data", "indicators",
            "technical_report", "news_report", "fundamentals_report",
            "bull_case", "bear_case", "bull_rebuttal", "bear_counter",
            "research_verdict", "trade_proposal",
            "risk_aggressive", "risk_conservative", "risk_neutral",
            "decision_report", "chart_path",
        ]
        for key in expected_keys:
            assert key in results, f"Missing key in results: {key}"

    @patch("tradingagent.agents.pipeline.fetch_stock_data")
    @patch("tradingagent.agents.pipeline.generate_chart")
    @patch("tradingagent.agents.technical_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.news_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.fundamentals_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.bull_researcher.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.bear_researcher.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.research_manager.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.trader.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_aggressive.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_conservative.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_neutral.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.portfolio_manager.call_llm", side_effect=_mock_call_llm)
    def test_pipeline_reports_are_strings(
        self, mock_pm, mock_rn, mock_rc, mock_ra, mock_tr,
        mock_rm, mock_bear, mock_bull, mock_fund, mock_news, mock_tech,
        mock_chart, mock_fetch, sample_data
    ):
        """All report fields should be non-empty strings."""
        mock_fetch.return_value = sample_data
        mock_chart.return_value = "/tmp/test_chart.png"

        results = run_analysis("AAPL", {"shares": 0, "avg_price": 0})

        report_keys = [
            "technical_report", "news_report", "fundamentals_report",
            "bull_case", "bear_case", "bull_rebuttal", "bear_counter",
            "research_verdict", "trade_proposal",
            "risk_aggressive", "risk_conservative", "risk_neutral",
            "decision_report",
        ]
        for key in report_keys:
            assert isinstance(results[key], str), f"{key} should be a string"
            assert len(results[key]) > 50, f"{key} seems too short: {len(results[key])} chars"

    @patch("tradingagent.agents.pipeline.fetch_stock_data")
    @patch("tradingagent.agents.pipeline.generate_chart")
    @patch("tradingagent.agents.technical_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.news_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.fundamentals_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.bull_researcher.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.bear_researcher.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.research_manager.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.trader.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_aggressive.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_conservative.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_neutral.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.portfolio_manager.call_llm", side_effect=_mock_call_llm)
    def test_pipeline_with_holdings(
        self, mock_pm, mock_rn, mock_rc, mock_ra, mock_tr,
        mock_rm, mock_bear, mock_bull, mock_fund, mock_news, mock_tech,
        mock_chart, mock_fetch, sample_data
    ):
        """Pipeline should work when user holds shares."""
        mock_fetch.return_value = sample_data
        mock_chart.return_value = "/tmp/test_chart.png"

        holdings = {"shares": 100, "avg_price": 175.00}
        results = run_analysis("AAPL", holdings)

        assert "decision_report" in results
        assert len(results["decision_report"]) > 100

    @patch("tradingagent.agents.pipeline.fetch_stock_data")
    def test_pipeline_rejects_invalid_ticker(self, mock_fetch):
        """Pipeline should raise ValueError for zero-price ticker."""
        mock_fetch.return_value = {
            "ticker": "FAKE",
            "current_price": 0,
        }
        with pytest.raises(ValueError, match="Could not find valid data"):
            run_analysis("FAKE", {"shares": 0, "avg_price": 0})

    @patch("tradingagent.agents.pipeline.fetch_stock_data")
    @patch("tradingagent.agents.pipeline.generate_chart")
    @patch("tradingagent.agents.technical_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.news_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.fundamentals_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.bull_researcher.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.bear_researcher.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.research_manager.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.trader.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_aggressive.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_conservative.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_neutral.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.portfolio_manager.call_llm", side_effect=_mock_call_llm)
    def test_pipeline_status_callbacks(
        self, mock_pm, mock_rn, mock_rc, mock_ra, mock_tr,
        mock_rm, mock_bear, mock_bull, mock_fund, mock_news, mock_tech,
        mock_chart, mock_fetch, sample_data
    ):
        """Pipeline should emit status callbacks for each phase."""
        mock_fetch.return_value = sample_data
        mock_chart.return_value = "/tmp/test_chart.png"

        statuses = []
        run_analysis("AAPL", {"shares": 0, "avg_price": 0}, on_status=statuses.append)

        assert len(statuses) >= 10, f"Expected 10+ status updates, got {len(statuses)}"
        assert any("Phase 0" in s for s in statuses)
        assert any("Phase 1" in s for s in statuses)
        assert any("Phase 2" in s for s in statuses)
        assert any("Phase 5" in s for s in statuses)
        assert any("complete" in s.lower() for s in statuses)

    @patch("tradingagent.agents.pipeline.fetch_stock_data")
    @patch("tradingagent.agents.pipeline.generate_chart", side_effect=Exception("chart error"))
    @patch("tradingagent.agents.technical_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.news_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.fundamentals_analyst.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.bull_researcher.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.bear_researcher.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.research_manager.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.trader.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_aggressive.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_conservative.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.risk_neutral.call_llm", side_effect=_mock_call_llm)
    @patch("tradingagent.agents.portfolio_manager.call_llm", side_effect=_mock_call_llm)
    def test_pipeline_survives_chart_failure(
        self, mock_pm, mock_rn, mock_rc, mock_ra, mock_tr,
        mock_rm, mock_bear, mock_bull, mock_fund, mock_news, mock_tech,
        mock_chart, mock_fetch, sample_data
    ):
        """Pipeline should still return results even if chart generation fails."""
        mock_fetch.return_value = sample_data

        results = run_analysis("AAPL", {"shares": 0, "avg_price": 0})

        assert results["chart_path"] is None
        assert results["decision_report"] is not None


class TestDecisionFormat:
    """Verify the decision report has the expected structure."""

    def test_decision_has_rating(self):
        """Decision report should contain a rating."""
        decision = MOCK_LLM_RESPONSES["decision"]
        assert "Rating:" in decision
        has_valid_rating = any(r in decision for r in ["BUY", "SELL", "HOLD", "OVERWEIGHT", "UNDERWEIGHT"])
        assert has_valid_rating, "Decision should contain a valid rating"

    def test_decision_has_sections(self):
        """Decision report should have all required sections."""
        decision = MOCK_LLM_RESPONSES["decision"]
        required_sections = [
            "FINAL DECISION",
            "SHORT-TERM PLAY",
            "LONG-TERM PLAY",
            "RISK MANAGEMENT",
            "TEAM SUMMARY",
        ]
        for section in required_sections:
            assert section in decision, f"Missing section: {section}"

    def test_decision_has_prices(self):
        """Decision should include entry, target, and stop loss prices."""
        decision = MOCK_LLM_RESPONSES["decision"]
        assert "Entry:" in decision
        assert "Target:" in decision
        assert "Stop Loss:" in decision
