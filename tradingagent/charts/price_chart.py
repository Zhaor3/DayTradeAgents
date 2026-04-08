"""Generate price prediction chart with technical overlays and forecast cone."""

import tempfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
from datetime import timedelta


def generate_chart(data: dict, indicators: dict, decision_text: str) -> str:
    """Generate a price chart with prediction cone and save as PNG.

    Returns the path to the generated PNG file.
    """
    df = data["daily_short"].copy()
    if len(df) < 5:
        return None

    df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # Parse decision for coloring
    decision = "HOLD"
    for line in decision_text.split("\n"):
        line_lower = line.lower().strip()
        if "rating:" in line_lower or "action:" in line_lower:
            if "buy" in line_lower or "overweight" in line_lower:
                decision = "BUY"
            elif "sell" in line_lower or "underweight" in line_lower:
                decision = "SELL"
            break

    colors = {"BUY": "#00C853", "SELL": "#FF1744", "HOLD": "#FFD600"}
    decision_color = colors.get(decision, colors["HOLD"])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), height_ratios=[3, 1],
                                    gridspec_kw={"hspace": 0.05})
    fig.patch.set_facecolor("#1a1a2e")

    # ── Price Chart (top) ──
    ax1.set_facecolor("#16213e")

    # Candlesticks
    for i in range(len(df)):
        o, c = df["Open"].iloc[i], df["Close"].iloc[i]
        h, l = df["High"].iloc[i], df["Low"].iloc[i]
        color = "#00C853" if c >= o else "#FF1744"
        ax1.plot([df.index[i], df.index[i]], [l, h], color=color, linewidth=0.8)
        ax1.plot([df.index[i], df.index[i]], [min(o, c), max(o, c)], color=color, linewidth=3.5)

    # Moving averages
    close = df["Close"]
    if len(close) >= 9:
        ema9 = close.ewm(span=9, adjust=False).mean()
        ax1.plot(df.index, ema9, color="#00BCD4", linewidth=1, alpha=0.8, label="EMA 9")
    if len(close) >= 20:
        sma20 = close.rolling(20).mean()
        ax1.plot(df.index, sma20, color="#FF9800", linewidth=1, alpha=0.8, label="SMA 20")

    # Bollinger Bands
    bb_u = indicators.get("bb_upper")
    bb_l = indicators.get("bb_lower")
    if bb_u and bb_l and len(close) >= 20:
        sma = close.rolling(20).mean()
        std = close.rolling(20).std()
        upper = sma + 2 * std
        lower = sma - 2 * std
        ax1.fill_between(df.index, lower, upper, alpha=0.08, color="#7C4DFF")
        ax1.plot(df.index, upper, color="#7C4DFF", linewidth=0.5, alpha=0.5)
        ax1.plot(df.index, lower, color="#7C4DFF", linewidth=0.5, alpha=0.5)

    # VWAP line
    vwap = indicators.get("vwap")
    if vwap:
        ax1.axhline(y=vwap, color="#E040FB", linewidth=0.8, linestyle="--", alpha=0.6, label=f"VWAP ${vwap}")

    # Support / Resistance zones
    for s in indicators.get("support_levels", []):
        ax1.axhline(y=s, color="#00C853", linewidth=0.6, linestyle=":", alpha=0.4)
    for r in indicators.get("resistance_levels", []):
        ax1.axhline(y=r, color="#FF1744", linewidth=0.6, linestyle=":", alpha=0.4)

    # ── Prediction Cone ──
    atr = indicators.get("atr_14")
    if atr and atr > 0:
        last_date = df.index[-1]
        last_price = close.iloc[-1]

        # Daily trend (linear regression slope of last 10 days)
        recent = close.tail(10).values
        x = np.arange(len(recent))
        slope = np.polyfit(x, recent, 1)[0] if len(recent) >= 2 else 0

        # Project 7 trading days forward
        forecast_days = 7
        future_dates = pd.bdate_range(start=last_date + timedelta(days=1), periods=forecast_days)

        center = np.array([last_price + slope * (i + 1) for i in range(forecast_days)])
        upper_bound = center + atr * np.sqrt(np.arange(1, forecast_days + 1)) * 1.5
        lower_bound = center - atr * np.sqrt(np.arange(1, forecast_days + 1)) * 1.5

        # Draw cone
        ax1.fill_between(future_dates, lower_bound, upper_bound,
                         alpha=0.15, color=decision_color, label="Prediction range")
        ax1.plot(future_dates, center, color=decision_color, linewidth=1.5,
                 linestyle="--", alpha=0.7, label="Projected trend")

        # Connect last candle to cone
        ax1.plot([last_date, future_dates[0]], [last_price, center[0]],
                 color=decision_color, linewidth=1.5, linestyle="--", alpha=0.7)

    # Fibonacci levels (subtle)
    fib = indicators.get("fibonacci", {})
    for key, val in fib.items():
        if key in ("fib_382", "fib_500", "fib_618"):
            ax1.axhline(y=val, color="#FFA726", linewidth=0.4, linestyle="-.", alpha=0.3)

    # ── Decision Badge ──
    current_p = data["current_price"]
    signal_score = indicators.get("signal_score", 0)
    badge_text = f"  {decision}  |  Score: {signal_score}/100  |  ${current_p:.2f}  "
    ax1.text(0.02, 0.96, badge_text, transform=ax1.transAxes,
             fontsize=12, fontweight="bold", color="white",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=decision_color, alpha=0.85),
             verticalalignment="top")

    ax1.set_ylabel("Price ($)", color="white", fontsize=10)
    ax1.tick_params(colors="white", labelsize=8)
    ax1.legend(loc="upper right", fontsize=7, facecolor="#16213e", edgecolor="#333",
               labelcolor="white")
    ax1.set_title(f"{data['ticker']} - {data['company_name']}", color="white",
                  fontsize=14, fontweight="bold", pad=10)
    ax1.grid(True, alpha=0.1, color="white")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.setp(ax1.get_xticklabels(), visible=False)

    # ── Volume Chart (bottom) ──
    ax2.set_facecolor("#16213e")
    vol_colors = ["#00C853" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#FF1744"
                  for i in range(len(df))]
    ax2.bar(df.index, df["Volume"], color=vol_colors, alpha=0.6, width=0.8)

    # Average volume line
    if len(df) >= 20:
        avg_vol = df["Volume"].rolling(20).mean()
        ax2.plot(df.index, avg_vol, color="#FF9800", linewidth=0.8, alpha=0.6, label="Avg Vol")

    ax2.set_ylabel("Volume", color="white", fontsize=10)
    ax2.tick_params(colors="white", labelsize=8)
    ax2.grid(True, alpha=0.1, color="white")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax2.tick_params(axis="x", rotation=30)

    # ── Info box (bottom right) ──
    info_lines = []
    rsi = indicators.get("rsi_14")
    if rsi:
        info_lines.append(f"RSI: {rsi}")
    macd_h = indicators.get("macd_histogram")
    if macd_h:
        info_lines.append(f"MACD: {'Bullish' if macd_h > 0 else 'Bearish'}")
    if atr:
        info_lines.append(f"ATR: ${atr}")
    adx = indicators.get("adx")
    if adx:
        info_lines.append(f"ADX: {adx}")

    info_text = "\n".join(info_lines)
    ax1.text(0.98, 0.04, info_text, transform=ax1.transAxes, fontsize=8,
             color="white", alpha=0.7, verticalalignment="bottom",
             horizontalalignment="right", fontfamily="monospace",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#16213e", alpha=0.8, edgecolor="#333"))

    plt.tight_layout()

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix=f"{data['ticker']}_")
    fig.savefig(tmp.name, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    return tmp.name
