from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import os

app = FastAPI()

# -------------------------
# CORS AYARI (GitHub için zorunlu)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # İstersen sonra güvenli domain yapabiliriz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# RSI HESAPLAMA
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
# ANA TEST ENDPOINT
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
        ticker = yf.Ticker(symbol.upper() + ".IS")
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
