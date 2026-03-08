from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RSI
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]

# EMA
def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean().iloc[-1]

# MACD
def calculate_macd(data):
    ema12 = data.ewm(span=12, adjust=False).mean()
    ema26 = data.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    return macd.iloc[-1]

@app.get("/")
def home():
    return {"status": "API Running"}

@app.get("/analyze/{symbol}")
def analyze(symbol: str):

    ticker = yf.Ticker(symbol.upper() + ".IS")
    data = ticker.history(period="6mo")

    if data.empty:
        return {"error": "Veri bulunamadı"}

    close = data["Close"]

    rsi = calculate_rsi(close)
    ema20 = calculate_ema(close, 20)
    ema50 = calculate_ema(close, 50)
    macd = calculate_macd(close)

    # Skor Sistemi
    score = 50

    if rsi < 30:
        score += 20
    elif rsi > 70:
        score -= 20

    if ema20 > ema50:
        score += 15
    else:
        score -= 15

    if macd > 0:
        score += 15
    else:
        score -= 15

    score = max(0, min(100, score))

    # Sinyal
    if score >= 75:
        signal = "GÜÇLÜ AL 🟢"
    elif score <= 35:
        signal = "GÜÇLÜ SAT 🔴"
    else:
        signal = "BEKLE 🟡"

    return {
        "symbol": symbol.upper(),
        "rsi": round(float(rsi),2),
        "ema20": round(float(ema20),2),
        "ema50": round(float(ema50),2),
        "macd": round(float(macd),4),
        "score": score,
        "signal": signal
    }
