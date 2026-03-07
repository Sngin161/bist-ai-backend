from fastapi import FastAPI
import yfinance as yf
import pandas as pd

app = FastAPI()

# -------------------------
# RSI HESAPLAMA FONKSİYONU
# -------------------------
def calculate_rsi(close_prices, period=14):

    if len(close_prices) < period + 1:
        return None

    delta = close_prices.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


# -------------------------
# ANA SAYFA TEST
# -------------------------
@app.get("/")
def home():
    return {"status": "API is running"}


# -------------------------
# ANALİZ ENDPOINT
# -------------------------
@app.get("/analyze/{symbol}")
def analyze(symbol: str):

    try:
        # BIST için .IS ekliyoruz
        ticker = yf.Ticker(symbol + ".IS")
        data = ticker.history(period="3mo")

        if data.empty:
            return {"error": "Veri bulunamadı"}

        rsi = calculate_rsi(data["Close"])

        if rsi is None:
            return {"error": "Yeterli veri yok"}

        return {
            "symbol": symbol.upper(),
            "rsi": round(float(rsi), 2)
        }

    except Exception as e:
        return {"error": str(e)}
