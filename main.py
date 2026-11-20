from flask import Flask, jsonify, render_template_string
import yfinance as yf
import pandas as pd
import threading
import time

app = Flask(__name__)

SYMBOLS = ["XAUUSD=X", "GBPUSD=X", "EURUSD=X"]
TIMEFRAME = "5m"

HTML = """
<h1>KATLO AI FOREX TRADING BOT</h1>
<h3>Powered by Ghost Edge | Xebo Trades</h3>
<p>Strategy: EMA 50 + EMA 200</p>
<p>Mode: DEMO SIGNALS ONLY</p>
<div id="signals">Loading market signals...</div>
<script>
async function scan() {
 const r = await fetch('/signals');
 const d = await r.json();
 document.getElementById('signals').innerHTML =
 d.map(x => `<p><b>${x.symbol}</b>: ${x.signal}
 | Price: ${x.price}</p>`).join('');
}
scan();
setInterval(scan, 30000);
</script>
"""

def scan_market(symbol):
    try:
        data = yf.download(
            symbol, period="5d", interval=TIMEFRAME,
            progress=False, auto_adjust=True
        )

        if data.empty or len(data) < 200:
            return {"symbol": symbol, "signal": "WAIT",
                    "price": "Unavailable"}

        close = data["Close"].squeeze()
        ema50 = close.ewm(span=50, adjust=False).mean()
        ema200 = close.ewm(span=200, adjust=False).mean()

        price = float(close.iloc[-1])

        if ema50.iloc[-1] > ema200.iloc[-1] and price > ema50.iloc[-1]:
            signal = "BUY"
        elif ema50.iloc[-1] < ema200.iloc[-1] and price < ema50.iloc[-1]:
            signal = "SELL"
        else:
            signal = "WAIT"

        return {
            "symbol": symbol,
            "signal": signal,
            "price": round(price, 5)
        }

    except Exception:
        return {"symbol": symbol, "signal": "WAIT",
                "price": "Data error"}

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/signals")
def signals():
    return jsonify([scan_market(s) for s in SYMBOLS])

@app.route("/health")
def health():
    return jsonify({"status": "running", "bot": "KATLO AI"})

if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=int(__import__("os").environ.get("PORT", 10000)))
