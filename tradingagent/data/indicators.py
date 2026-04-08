"""Technical indicators for day trading analysis - comprehensive suite."""

import pandas as pd
import numpy as np


# ── Core Indicators ──────────────────────────────────────────────────────────

def calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calc_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calc_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = sma + std_dev * std
    lower = sma - std_dev * std
    return upper, sma, lower


def calc_vwap(df: pd.DataFrame) -> pd.Series:
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    cum_tp_vol = (typical_price * df["Volume"]).cumsum()
    cum_vol = df["Volume"].cumsum()
    return cum_tp_vol / cum_vol


# ── New Indicators ───────────────────────────────────────────────────────────

def calc_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range - measures volatility."""
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()


def calc_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3):
    """Stochastic Oscillator %K and %D."""
    lowest_low = df["Low"].rolling(window=k_period).min()
    highest_high = df["High"].rolling(window=k_period).max()
    k = 100 * (df["Close"] - lowest_low) / (highest_high - lowest_low)
    d = k.rolling(window=d_period).mean()
    return k, d


def calc_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average Directional Index - measures trend strength (not direction)."""
    plus_dm = df["High"].diff()
    minus_dm = -df["Low"].diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    atr = calc_atr(df, period)
    plus_di = 100 * (plus_dm.ewm(alpha=1/period, min_periods=period).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(alpha=1/period, min_periods=period).mean() / atr)

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.ewm(alpha=1/period, min_periods=period).mean()
    return adx


def calc_obv(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume - confirms price moves with volume."""
    direction = np.sign(df["Close"].diff())
    return (direction * df["Volume"]).cumsum()


def calc_fibonacci_levels(df: pd.DataFrame, lookback: int = 60) -> dict:
    """Fibonacci retracement levels from recent swing high/low."""
    recent = df.tail(lookback)
    swing_high = recent["High"].max()
    swing_low = recent["Low"].min()
    diff = swing_high - swing_low

    return {
        "fib_0": round(swing_low, 2),
        "fib_236": round(swing_low + 0.236 * diff, 2),
        "fib_382": round(swing_low + 0.382 * diff, 2),
        "fib_500": round(swing_low + 0.500 * diff, 2),
        "fib_618": round(swing_low + 0.618 * diff, 2),
        "fib_786": round(swing_low + 0.786 * diff, 2),
        "fib_1": round(swing_high, 2),
    }


def calc_roc(series: pd.Series, period: int = 12) -> pd.Series:
    """Rate of Change - momentum indicator."""
    return ((series - series.shift(period)) / series.shift(period)) * 100


def detect_rsi_divergence(df: pd.DataFrame, rsi: pd.Series, lookback: int = 20) -> str:
    """Detect bullish/bearish RSI divergence."""
    if len(df) < lookback or len(rsi) < lookback:
        return "none"

    recent_price = df["Close"].tail(lookback)
    recent_rsi = rsi.tail(lookback)

    mid = lookback // 2

    # Bearish divergence: price higher high, RSI lower high
    if (recent_price.iloc[-1] > recent_price.iloc[mid] and
            recent_rsi.iloc[-1] < recent_rsi.iloc[mid]):
        return "bearish"

    # Bullish divergence: price lower low, RSI higher low
    if (recent_price.iloc[-1] < recent_price.iloc[mid] and
            recent_rsi.iloc[-1] > recent_rsi.iloc[mid]):
        return "bullish"

    return "none"


def detect_ema_cross(df: pd.DataFrame) -> str:
    """Detect EMA 9/21 crossover signal."""
    if len(df) < 22:
        return "none"
    close = df["Close"]
    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()

    if ema9.iloc[-1] > ema21.iloc[-1] and ema9.iloc[-2] <= ema21.iloc[-2]:
        return "golden_cross"
    elif ema9.iloc[-1] < ema21.iloc[-1] and ema9.iloc[-2] >= ema21.iloc[-2]:
        return "death_cross"
    elif ema9.iloc[-1] > ema21.iloc[-1]:
        return "bullish"
    else:
        return "bearish"


# ── Support / Resistance ─────────────────────────────────────────────────────

def calc_support_resistance(df: pd.DataFrame, window: int = 20):
    if len(df) < window:
        return [], []

    recent = df.tail(window)
    highs = recent["High"]
    lows = recent["Low"]

    resistance_levels = []
    support_levels = []

    for i in range(2, len(recent) - 2):
        if (highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i-2] and
                highs.iloc[i] > highs.iloc[i+1] and highs.iloc[i] > highs.iloc[i+2]):
            resistance_levels.append(round(highs.iloc[i], 2))
        if (lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i-2] and
                lows.iloc[i] < lows.iloc[i+1] and lows.iloc[i] < lows.iloc[i+2]):
            support_levels.append(round(lows.iloc[i], 2))

    return _cluster_levels(support_levels), _cluster_levels(resistance_levels)


def _cluster_levels(levels, threshold=0.01):
    if not levels:
        return levels
    levels = sorted(levels)
    clustered = [levels[0]]
    for lvl in levels[1:]:
        if abs(lvl - clustered[-1]) / clustered[-1] < threshold:
            clustered[-1] = round((clustered[-1] + lvl) / 2, 2)
        else:
            clustered.append(lvl)
    return clustered


# ── Signal Alignment Score ───────────────────────────────────────────────────

def calc_signal_alignment(indicators: dict) -> dict:
    """Calculate a composite signal alignment score from -100 (bearish) to +100 (bullish).
    Also returns individual signal breakdowns."""
    signals = []
    breakdown = {}

    # RSI
    rsi = indicators.get("rsi_14")
    if rsi is not None:
        if rsi < 30:
            signals.append(("RSI oversold", +2))
            breakdown["RSI"] = "Oversold (bullish)"
        elif rsi < 40:
            signals.append(("RSI low", +1))
            breakdown["RSI"] = "Low (slightly bullish)"
        elif rsi > 70:
            signals.append(("RSI overbought", -2))
            breakdown["RSI"] = "Overbought (bearish)"
        elif rsi > 60:
            signals.append(("RSI high", -1))
            breakdown["RSI"] = "High (slightly bearish)"
        else:
            signals.append(("RSI neutral", 0))
            breakdown["RSI"] = "Neutral"

    # MACD
    hist = indicators.get("macd_histogram")
    if hist is not None:
        if hist > 0:
            signals.append(("MACD bullish", +2))
            breakdown["MACD"] = "Bullish"
        else:
            signals.append(("MACD bearish", -2))
            breakdown["MACD"] = "Bearish"

    # Price vs VWAP
    vwap = indicators.get("vwap")
    price = indicators.get("_current_price", 0)
    if vwap and price:
        if price > vwap:
            signals.append(("Above VWAP", +1))
            breakdown["VWAP"] = "Above (bullish)"
        else:
            signals.append(("Below VWAP", -1))
            breakdown["VWAP"] = "Below (bearish)"

    # EMA cross
    ema_cross = indicators.get("ema_cross")
    if ema_cross == "golden_cross":
        signals.append(("EMA golden cross", +3))
        breakdown["EMA Cross"] = "Golden cross (strong bullish)"
    elif ema_cross == "death_cross":
        signals.append(("EMA death cross", -3))
        breakdown["EMA Cross"] = "Death cross (strong bearish)"
    elif ema_cross == "bullish":
        signals.append(("EMA bullish", +1))
        breakdown["EMA Cross"] = "Bullish alignment"
    elif ema_cross == "bearish":
        signals.append(("EMA bearish", -1))
        breakdown["EMA Cross"] = "Bearish alignment"

    # Stochastic
    stoch_k = indicators.get("stochastic_k")
    if stoch_k is not None:
        if stoch_k < 20:
            signals.append(("Stoch oversold", +2))
            breakdown["Stochastic"] = "Oversold (bullish)"
        elif stoch_k > 80:
            signals.append(("Stoch overbought", -2))
            breakdown["Stochastic"] = "Overbought (bearish)"
        else:
            signals.append(("Stoch neutral", 0))
            breakdown["Stochastic"] = "Neutral"

    # ADX (trend strength, not direction)
    adx = indicators.get("adx")
    if adx is not None:
        if adx > 25:
            breakdown["ADX"] = f"Strong trend ({adx:.0f})"
        else:
            breakdown["ADX"] = f"Weak/no trend ({adx:.0f})"

    # Volume
    vol_ratio = indicators.get("volume_ratio")
    if vol_ratio is not None:
        if vol_ratio > 1.5:
            signals.append(("High volume", +1))
            breakdown["Volume"] = "High (confirms move)"
        elif vol_ratio < 0.5:
            signals.append(("Low volume", -1))
            breakdown["Volume"] = "Low (weak conviction)"
        else:
            breakdown["Volume"] = "Normal"

    # RSI divergence
    div = indicators.get("rsi_divergence")
    if div == "bullish":
        signals.append(("Bullish RSI divergence", +3))
        breakdown["RSI Divergence"] = "Bullish (strong reversal signal)"
    elif div == "bearish":
        signals.append(("Bearish RSI divergence", -3))
        breakdown["RSI Divergence"] = "Bearish (strong reversal signal)"

    # Calculate composite score
    if not signals:
        return {"score": 0, "label": "No data", "breakdown": breakdown, "signals": signals}

    total = sum(s[1] for s in signals)
    max_possible = sum(abs(s[1]) for s in signals)
    score = int((total / max_possible) * 100) if max_possible > 0 else 0

    if score > 40:
        label = "Strong Bullish"
    elif score > 15:
        label = "Bullish"
    elif score > -15:
        label = "Neutral"
    elif score > -40:
        label = "Bearish"
    else:
        label = "Strong Bearish"

    return {"score": score, "label": label, "breakdown": breakdown, "signals": signals}


# ── Master Compute Function ──────────────────────────────────────────────────

def compute_all_indicators(data: dict) -> dict:
    """Compute all technical indicators from market data."""
    results = {}

    # --- Short-term (daily, ~30 days) ---
    df_short = data["daily_short"]
    if len(df_short) >= 5:
        close = df_short["Close"]

        # Moving averages
        results["sma_10"] = round(close.rolling(10).mean().iloc[-1], 2) if len(close) >= 10 else None
        results["sma_20"] = round(close.rolling(20).mean().iloc[-1], 2) if len(close) >= 20 else None
        results["ema_9"] = round(close.ewm(span=9, adjust=False).mean().iloc[-1], 2)
        results["ema_21"] = round(close.ewm(span=21, adjust=False).mean().iloc[-1], 2) if len(close) >= 21 else None

        # RSI
        rsi = calc_rsi(close)
        results["rsi_14"] = round(rsi.iloc[-1], 1) if not pd.isna(rsi.iloc[-1]) else None

        # MACD
        macd_line, signal_line, histogram = calc_macd(close)
        results["macd_line"] = round(macd_line.iloc[-1], 4) if not pd.isna(macd_line.iloc[-1]) else None
        results["macd_signal"] = round(signal_line.iloc[-1], 4) if not pd.isna(signal_line.iloc[-1]) else None
        results["macd_histogram"] = round(histogram.iloc[-1], 4) if not pd.isna(histogram.iloc[-1]) else None

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = calc_bollinger_bands(close)
        results["bb_upper"] = round(bb_upper.iloc[-1], 2) if not pd.isna(bb_upper.iloc[-1]) else None
        results["bb_middle"] = round(bb_middle.iloc[-1], 2) if not pd.isna(bb_middle.iloc[-1]) else None
        results["bb_lower"] = round(bb_lower.iloc[-1], 2) if not pd.isna(bb_lower.iloc[-1]) else None

        # ATR
        atr = calc_atr(df_short)
        results["atr_14"] = round(atr.iloc[-1], 2) if not pd.isna(atr.iloc[-1]) else None

        # Stochastic
        stoch_k, stoch_d = calc_stochastic(df_short)
        results["stochastic_k"] = round(stoch_k.iloc[-1], 1) if not pd.isna(stoch_k.iloc[-1]) else None
        results["stochastic_d"] = round(stoch_d.iloc[-1], 1) if not pd.isna(stoch_d.iloc[-1]) else None

        # ADX
        adx = calc_adx(df_short)
        results["adx"] = round(adx.iloc[-1], 1) if not pd.isna(adx.iloc[-1]) else None

        # OBV
        obv = calc_obv(df_short)
        results["obv_current"] = int(obv.iloc[-1]) if not pd.isna(obv.iloc[-1]) else None
        if len(obv) >= 5 and not pd.isna(obv.iloc[-1]) and not pd.isna(obv.iloc[-5]):
            results["obv_change_5d"] = int(obv.iloc[-1] - obv.iloc[-5])
        else:
            results["obv_change_5d"] = None

        # ROC
        roc = calc_roc(close, period=12)
        results["roc_12"] = round(roc.iloc[-1], 2) if not pd.isna(roc.iloc[-1]) else None

        # RSI Divergence
        results["rsi_divergence"] = detect_rsi_divergence(df_short, rsi)

        # EMA Cross
        results["ema_cross"] = detect_ema_cross(df_short)

        # Fibonacci Levels
        results["fibonacci"] = calc_fibonacci_levels(df_short)

        # Volume analysis
        avg_vol_20 = df_short["Volume"].rolling(20).mean().iloc[-1] if len(df_short) >= 20 else df_short["Volume"].mean()
        current_vol = df_short["Volume"].iloc[-1]
        if not pd.isna(avg_vol_20) and not pd.isna(current_vol) and avg_vol_20 > 0:
            results["volume_ratio"] = round(current_vol / avg_vol_20, 2)
        else:
            results["volume_ratio"] = None

        # Price changes
        results["change_1d"] = round((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100, 2) if len(close) >= 2 else None
        results["change_5d"] = round((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100, 2) if len(close) >= 5 else None

        # Support / Resistance
        support, resistance = calc_support_resistance(df_short)
        results["support_levels"] = support
        results["resistance_levels"] = resistance

    # --- Long-term (daily, ~6 months) ---
    df_long = data["daily_long"]
    if len(df_long) >= 20:
        close_long = df_long["Close"]

        results["sma_50"] = round(close_long.rolling(50).mean().iloc[-1], 2) if len(close_long) >= 50 else None
        results["sma_200"] = round(close_long.rolling(200).mean().iloc[-1], 2) if len(close_long) >= 200 else None

        rsi_long = calc_rsi(close_long)
        results["rsi_14_long"] = round(rsi_long.iloc[-1], 1) if not pd.isna(rsi_long.iloc[-1]) else None

        results["pct_from_52w_high"] = round((data["current_price"] - data["week_52_high"]) / data["week_52_high"] * 100, 1) if data["week_52_high"] > 0 else None
        results["pct_from_52w_low"] = round((data["current_price"] - data["week_52_low"]) / data["week_52_low"] * 100, 1) if data["week_52_low"] > 0 else None

        support_lt, resistance_lt = calc_support_resistance(df_long, window=40)
        results["support_levels_long"] = support_lt
        results["resistance_levels_long"] = resistance_lt

        # Long-term Fibonacci
        results["fibonacci_long"] = calc_fibonacci_levels(df_long, lookback=120)

    # --- Intraday ---
    df_intra = data["intraday"]
    if len(df_intra) >= 10:
        close_intra = df_intra["Close"]

        rsi_intra = calc_rsi(close_intra, period=14)
        results["rsi_intraday"] = round(rsi_intra.iloc[-1], 1) if not pd.isna(rsi_intra.iloc[-1]) else None

        vwap = calc_vwap(df_intra)
        results["vwap"] = round(vwap.iloc[-1], 2) if not pd.isna(vwap.iloc[-1]) else None

        macd_i, sig_i, hist_i = calc_macd(close_intra)
        results["macd_intraday"] = round(macd_i.iloc[-1], 4) if not pd.isna(macd_i.iloc[-1]) else None
        results["macd_signal_intraday"] = round(sig_i.iloc[-1], 4) if not pd.isna(sig_i.iloc[-1]) else None

    # --- Signal Alignment Score ---
    results["_current_price"] = data["current_price"]
    alignment = calc_signal_alignment(results)
    results["signal_score"] = alignment["score"]
    results["signal_label"] = alignment["label"]
    results["signal_breakdown"] = alignment["breakdown"]

    return results
