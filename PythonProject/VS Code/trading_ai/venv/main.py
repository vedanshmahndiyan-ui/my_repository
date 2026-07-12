from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- INDICATORS ----------------

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices):
    ema12 = prices.ewm(span=12, adjust=False).mean()
    ema26 = prices.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

# ---------------- CANDLE PATTERNS ----------------

def detect_candlestick_pattern(df):
    if len(df) < 2:
        return "No Pattern", "Not enough data"

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Values
    o1, c1 = prev["Open"], prev["Close"]
    o2, c2 = last["Open"], last["Close"]
    h2, l2 = last["High"], last["Low"]

    body = abs(c2 - o2)
    range_ = h2 - l2

    # 🔥 Bullish Engulfing
    if c1 < o1 and c2 > o2 and c2 > o1 and o2 < c1:
        return "Bullish Engulfing", "Strong BUY signal"

    # 🔥 Bearish Engulfing
    if c1 > o1 and c2 < o2 and c2 < o1 and o2 > c1:
        return "Bearish Engulfing", "Strong SELL signal"

    # 🔥 Doji
    if body < (range_ * 0.1):
        return "Doji", "Market indecision"

    # 🔥 Hammer
    if (c2 > o2) and ((o2 - l2) > 2 * body):
        return "Hammer", "Potential BUY reversal"

    return "No Clear Pattern", "Wait"

# ---------------- PATTERN ENGINE ----------------

def detect_pattern(rsi, ma20, ma50, trend, macd, macd_signal, signal):

    if rsi < 30 and macd > macd_signal:
        return "Bullish Reversal", "BUY on confirmation"

    if rsi > 70 and macd < macd_signal:
        return "Bearish Reversal", "SELL or book profits"

    if ma20 > ma50 and trend == "UPTREND":
        if signal == "BUY":
            return "Strong Uptrend", "BUY / Hold"
        else:
            return "Weak Uptrend", "Wait"

    if ma20 < ma50 and trend == "DOWNTREND":
        if signal == "SELL":
            return "Strong Downtrend", "SELL"
        else:
            return "Weak Downtrend", "Avoid buying"

    return "Sideways Market", "Wait for breakout"

# ---------------- API ----------------

@app.get("/analyze/{symbol}")
def analyze(symbol: str):
    try:
        if "." not in symbol:
            symbol = symbol.upper() + ".NS"

        data = yf.download(symbol, period="3mo")

        if data.empty:
            return {"error": "Invalid stock"}

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        close = data["Close"]

        # Indicators
        data["RSI"] = calculate_rsi(close)
        data["MA20"] = close.rolling(20).mean()
        data["MA50"] = close.rolling(50).mean()

        macd, signal = calculate_macd(close)
        data["MACD"] = macd
        data["MACD_SIGNAL"] = signal

        indicator_data = data.dropna()

        latest = indicator_data.iloc[-1]

        price = float(latest["Close"])
        rsi = float(latest["RSI"])
        ma20 = float(latest["MA20"])
        ma50 = float(latest["MA50"])
        macd_val = float(latest["MACD"])
        macd_signal = float(latest["MACD_SIGNAL"])

        trend = "UPTREND" if ma20 > ma50 else "DOWNTREND"

        # SIGNAL
        score = 0
        score += 1 if rsi < 30 else -1 if rsi > 70 else 0
        score += 1 if ma20 > ma50 else -1
        score += 1 if macd_val > macd_signal else -1

        if score >= 2:
            signal_text = "BUY"
        elif score <= -2:
            signal_text = "SELL"
        else:
            signal_text = "HOLD"

        confidence = min(abs(score) * 25, 100)

        # Pattern logic
        pattern, pattern_action = detect_pattern(
            rsi, ma20, ma50, trend, macd_val, macd_signal, signal_text
        )

        # 🔥 NEW: Candlestick pattern
        candle_pattern, candle_action = detect_candlestick_pattern(data)

        # Chart data
        history = [
            {
                "time": str(index.date()),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"])
            }
            for index, row in data.iterrows()
        ]

        macd_history = [
            {
                "time": str(index.date()),
                "macd": float(row["MACD"]) if not pd.isna(row["MACD"]) else 0,
                "signal": float(row["MACD_SIGNAL"]) if not pd.isna(row["MACD_SIGNAL"]) else 0
            }
            for index, row in data.iterrows()
        ]

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "trend": trend,
            "rsi": round(rsi, 2),
            "ma20": round(ma20, 2),
            "ma50": round(ma50, 2),
            "macd": round(macd_val, 2),
            "macd_signal": round(macd_signal, 2),
            "signal": signal_text,
            "confidence": confidence,
            "pattern": pattern,
            "pattern_action": pattern_action,
            "candle_pattern": candle_pattern,
            "candle_action": candle_action,
            "history": history,
            "macd_history": macd_history
        }

    except Exception as e:
        return {"error": str(e)}
