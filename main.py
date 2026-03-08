from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import os
from openai import OpenAI

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

@app.get("/analyze/{symbol}")
def analyze(symbol: str):

    ticker = yf.Ticker(symbol.upper() + ".IS")
    data = ticker.history(period="6mo")

    if data.empty:
        return {"error": "Veri bulunamadı"}

    close = data["Close"]
    rsi = calculate_rsi(close)

    # AI Prompt
    prompt = f"""
    Sen profesyonel bir borsa analistisin.
    Hisse: {symbol.upper()}
    RSI: {round(float(rsi),2)}

    Bu veriye göre kısa, net ve profesyonel bir analiz yaz.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Finans analisti gibi cevap ver."},
                {"role": "user", "content": prompt}
            ]
        )

        ai_comment = response.choices[0].message.content

    except Exception as e:
        return {"error": f"AI Hatası: {str(e)}"}

    return {
        "symbol": symbol.upper(),
        "rsi": round(float(rsi),2),
        "ai_analysis": ai_comment
    }
