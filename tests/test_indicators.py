"""Unit tests for technical indicator calculations.

Tests that indicators produce valid, reasonable values using historical data.
"""

import pytest
import pandas as pd
import numpy as np

from tradingagent.data.indicators import (
    calc_rsi,
    calc_macd,
    calc_bollinger_bands,
    calc_vwap,
    calc_atr,
    calc_stochastic,
    calc_adx,
    calc_obv,
    calc_fibonacci_levels,
    calc_roc,
    detect_rsi_divergence,
    detect_ema_cross,
    calc_support_resistance,
    calc_signal_alignment,
    compute_all_indicators,
)


class TestRSI:
    def test_rsi_range(self, sample_data):
        """RSI should always be between 0 and 100."""
        close = sample_data["daily_short"]["Close"]
        rsi = calc_rsi(close)
        valid = rsi.dropna()
        assert len(valid) > 0, "RSI should produce values"
        assert valid.min() >= 0, f"RSI below 0: {valid.min()}"
        assert valid.max() <= 100, f"RSI above 100: {valid.max()}"

    def test_rsi_oversold_on_downtrend(self):
        """RSI should be low when prices are consistently falling."""
        prices = pd.Series([100 - i * 2 for i in range(30)])  # steady decline
        rsi = calc_rsi(prices, period=14)
        last_rsi = rsi.iloc[-1]
        assert last_rsi < 30, f"RSI should be oversold on downtrend, got {last_rsi}"

    def test_rsi_overbought_on_uptrend(self):
        """RSI should be high when prices are consistently rising."""
        prices = pd.Series([100 + i * 2 for i in range(30)])  # steady rise
        rsi = calc_rsi(prices, period=14)
        last_rsi = rsi.iloc[-1]
        assert last_rsi > 70, f"RSI should be overbought on uptrend, got {last_rsi}"


class TestMACD:
    def test_macd_components(self, sample_data):
        """MACD should return three series of equal length."""
        close = sample_data["daily_long"]["Close"]
        macd_line, signal_line, histogram = calc_macd(close)
        assert len(macd_line) == len(close)
        assert len(signal_line) == len(close)
        assert len(histogram) == len(close)

    def test_histogram_is_difference(self, sample_data):
        """Histogram should equal MACD line minus signal line."""
        close = sample_data["daily_long"]["Close"]
        macd_line, signal_line, histogram = calc_macd(close)
        diff = macd_line - signal_line
        np.testing.assert_array_almost_equal(
            histogram.dropna().values, diff.dropna().values, decimal=10
        )

    def test_macd_positive_on_uptrend(self):
        """MACD line should be positive during sustained uptrend."""
        prices = pd.Series([100 + i * 0.5 for i in range(50)])
        macd_line, _, _ = calc_macd(prices)
        assert macd_line.iloc[-1] > 0, "MACD should be positive in uptrend"


class TestBollingerBands:
    def test_band_ordering(self, sample_data):
        """Upper band > middle > lower band always."""
        close = sample_data["daily_short"]["Close"]
        upper, middle, lower = calc_bollinger_bands(close)
        valid_idx = upper.dropna().index
        assert (upper[valid_idx] >= middle[valid_idx]).all(), "Upper should be >= middle"
        assert (middle[valid_idx] >= lower[valid_idx]).all(), "Middle should be >= lower"

    def test_middle_is_sma(self, sample_data):
        """Middle band should be the 20-period SMA."""
        close = sample_data["daily_short"]["Close"]
        _, middle, _ = calc_bollinger_bands(close, period=20)
        sma20 = close.rolling(20).mean()
        valid = middle.dropna()
        np.testing.assert_array_almost_equal(
            valid.values, sma20.dropna().values, decimal=10
        )


class TestVWAP:
    def test_vwap_reasonable(self, sample_data):
        """VWAP should be within the day's high-low range (approximately)."""
        df = sample_data["intraday"]
        vwap = calc_vwap(df)
        last_vwap = vwap.iloc[-1]
        # VWAP should be within a reasonable range of recent prices
        recent_low = df["Low"].tail(26).min()
        recent_high = df["High"].tail(26).max()
        assert recent_low * 0.95 <= last_vwap <= recent_high * 1.05, \
            f"VWAP {last_vwap} outside expected range [{recent_low}, {recent_high}]"


class TestATR:
    def test_atr_positive(self, sample_data):
        """ATR should always be positive."""
        df = sample_data["daily_short"]
        atr = calc_atr(df)
        valid = atr.dropna()
        assert len(valid) > 0, "ATR should produce values"
        assert (valid > 0).all(), "ATR should always be positive"

    def test_atr_reasonable_magnitude(self, sample_data):
        """ATR should be a reasonable fraction of the stock price."""
        df = sample_data["daily_short"]
        atr = calc_atr(df)
        last_atr = atr.iloc[-1]
        last_price = df["Close"].iloc[-1]
        pct = last_atr / last_price * 100
        assert 0.1 < pct < 20, f"ATR is {pct:.1f}% of price - seems unreasonable"


class TestStochastic:
    def test_stochastic_range(self, sample_data):
        """Stochastic %K and %D should be between 0 and 100."""
        df = sample_data["daily_short"]
        k, d = calc_stochastic(df)
        valid_k = k.dropna()
        valid_d = d.dropna()
        assert valid_k.min() >= 0 and valid_k.max() <= 100, f"Stoch K out of range"
        assert valid_d.min() >= 0 and valid_d.max() <= 100, f"Stoch D out of range"


class TestADX:
    def test_adx_positive(self, sample_data):
        """ADX should be positive."""
        df = sample_data["daily_long"]  # ADX needs more data (14-period smoothing)
        adx = calc_adx(df)
        valid = adx.dropna()
        assert len(valid) > 0
        assert (valid >= 0).all(), "ADX should be non-negative"


class TestOBV:
    def test_obv_length(self, sample_data):
        """OBV should have same length as input."""
        df = sample_data["daily_short"]
        obv = calc_obv(df)
        assert len(obv) == len(df)


class TestFibonacci:
    def test_fibonacci_levels_ordered(self, sample_data):
        """Fibonacci levels should be in ascending order."""
        df = sample_data["daily_short"]
        fib = calc_fibonacci_levels(df)
        levels = [fib["fib_0"], fib["fib_236"], fib["fib_382"],
                  fib["fib_500"], fib["fib_618"], fib["fib_786"], fib["fib_1"]]
        assert levels == sorted(levels), f"Fibonacci levels not ascending: {levels}"

    def test_fibonacci_between_high_low(self, sample_data):
        """All fib levels should be between the swing low and swing high."""
        df = sample_data["daily_short"]
        fib = calc_fibonacci_levels(df)
        assert fib["fib_0"] <= fib["fib_500"] <= fib["fib_1"]


class TestROC:
    def test_roc_zero_on_flat(self):
        """ROC should be 0 when price hasn't changed."""
        prices = pd.Series([100.0] * 20)
        roc = calc_roc(prices, period=12)
        assert roc.iloc[-1] == 0.0


class TestRSIDivergence:
    def test_returns_valid_string(self, sample_data):
        """Should return one of: bullish, bearish, none."""
        df = sample_data["daily_short"]
        rsi = calc_rsi(df["Close"])
        result = detect_rsi_divergence(df, rsi)
        assert result in ("bullish", "bearish", "none")


class TestEMACross:
    def test_returns_valid_string(self, sample_data):
        """Should return one of: golden_cross, death_cross, bullish, bearish, none."""
        df = sample_data["daily_long"]
        result = detect_ema_cross(df)
        assert result in ("golden_cross", "death_cross", "bullish", "bearish", "none")


class TestSupportResistance:
    def test_returns_lists(self, sample_data):
        """Should return two lists."""
        df = sample_data["daily_short"]
        support, resistance = calc_support_resistance(df)
        assert isinstance(support, list)
        assert isinstance(resistance, list)


class TestSignalAlignment:
    def test_score_range(self):
        """Score should be between -100 and +100."""
        indicators = {
            "rsi_14": 45.0,
            "macd_histogram": 0.5,
            "vwap": 190.0,
            "_current_price": 192.0,
            "ema_cross": "bullish",
            "stochastic_k": 55.0,
            "volume_ratio": 1.1,
            "rsi_divergence": "none",
        }
        result = calc_signal_alignment(indicators)
        assert -100 <= result["score"] <= 100
        assert result["label"] in ("Strong Bullish", "Bullish", "Neutral", "Bearish", "Strong Bearish")
        assert isinstance(result["breakdown"], dict)

    def test_bullish_signals(self):
        """Strongly bullish indicators should give positive score."""
        indicators = {
            "rsi_14": 25.0,  # oversold
            "macd_histogram": 1.0,  # bullish
            "vwap": 180.0,
            "_current_price": 190.0,  # above VWAP
            "ema_cross": "golden_cross",
            "stochastic_k": 15.0,  # oversold
            "volume_ratio": 2.0,  # high volume
            "rsi_divergence": "bullish",
        }
        result = calc_signal_alignment(indicators)
        assert result["score"] > 0, f"Expected positive score, got {result['score']}"

    def test_bearish_signals(self):
        """Strongly bearish indicators should give negative score."""
        indicators = {
            "rsi_14": 75.0,  # overbought
            "macd_histogram": -1.0,  # bearish
            "vwap": 200.0,
            "_current_price": 190.0,  # below VWAP
            "ema_cross": "death_cross",
            "stochastic_k": 85.0,  # overbought
            "volume_ratio": 0.3,  # low volume
            "rsi_divergence": "bearish",
        }
        result = calc_signal_alignment(indicators)
        assert result["score"] < 0, f"Expected negative score, got {result['score']}"


class TestComputeAllIndicators:
    def test_returns_all_keys(self, sample_data):
        """compute_all_indicators should return all expected indicator keys."""
        indicators = compute_all_indicators(sample_data)

        expected_keys = [
            "rsi_14", "macd_line", "macd_signal", "macd_histogram",
            "bb_upper", "bb_middle", "bb_lower",
            "atr_14", "stochastic_k", "stochastic_d", "adx",
            "obv_current", "roc_12",
            "rsi_divergence", "ema_cross", "fibonacci",
            "volume_ratio", "change_1d", "change_5d",
            "support_levels", "resistance_levels",
            "signal_score", "signal_label", "signal_breakdown",
        ]

        for key in expected_keys:
            assert key in indicators, f"Missing indicator: {key}"

    def test_rsi_in_range(self, sample_data):
        """RSI from compute_all_indicators should be 0-100."""
        indicators = compute_all_indicators(sample_data)
        rsi = indicators["rsi_14"]
        if rsi is not None:
            assert 0 <= rsi <= 100, f"RSI out of range: {rsi}"

    def test_bollinger_ordering(self, sample_data):
        """Bollinger bands should maintain upper > middle > lower."""
        indicators = compute_all_indicators(sample_data)
        if all(indicators.get(k) is not None for k in ("bb_upper", "bb_middle", "bb_lower")):
            assert indicators["bb_upper"] >= indicators["bb_middle"] >= indicators["bb_lower"]

    def test_signal_score_present(self, sample_data):
        """Signal alignment score should be computed."""
        indicators = compute_all_indicators(sample_data)
        assert "signal_score" in indicators
        assert "signal_label" in indicators
        assert -100 <= indicators["signal_score"] <= 100
