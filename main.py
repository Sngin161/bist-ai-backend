from fastapi import FastAPI
import yfinance as yf
import pandas as pd

app = FastAPI()

def calculate_rsi(data, period=14):
    delta = data.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]

@app.get("/analyze/{symbol}")
def analyze(symbol: str):

    data = yf.download(symbol + ".IS", period="3mo", interval="1d")

    if data.empty:
        return {"error": "Veri bulunamadı"}

    rsi = calculate_rsi(data["Close"])

    return {
        "symbol": symbol,
        "rsi": round(float(rsi), 2)
    }
