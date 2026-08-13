from flask import Flask, render_template_string
import yfinance as yf
from datetime import datetime
import time

app = Flask(__name__)

# Cache
cached_data = {
    "price": None,
    "support": None,
    "resistance": None,
    "updated": None
}

last_fetch = 0
CACHE_SECONDS = 300


HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="60">
    <title>NIFTY 50 Alert</title>

    <style>
        body {
            background: #111;
            color: white;
            font-family: Arial;
            text-align: center;
            padding: 30px;
        }

        .box {
            max-width: 500px;
            margin: auto;
            padding: 30px;
            border: 1px solid #555;
            border-radius: 20px;
        }

        .price {
            font-size: 42px;
            font-weight: bold;
            margin: 20px 0;
        }

        .alert {
            font-size: 25px;
            font-weight: bold;
            margin: 20px;
        }

        .buy {
            color: #00ff88;
        }

        .sell {
            color: #ff4444;
        }

        .wait {
            color: #ffd43b;
        }

        button {
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 10px;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>NIFTY 50 Alert</h1>

    <div class="price">₹{{ price }}</div>

    <p>Support: ₹{{ support }}</p>
    <p>Resistance: ₹{{ resistance }}</p>

    <div class="alert {{ alert_class }}">
        {{ alert }}
    </div>

    <p>Updated: {{ time }}</p>

    <button onclick="location.reload()">Refresh</button>

</div>

</body>
</html>
"""


def get_market_data():

    global last_fetch, cached_data

    now = time.time()

    # 5 minute cache
    if cached_data["price"] is not None and now - last_fetch < CACHE_SECONDS:
        return cached_data

    try:

        data = yf.download(
            "^NSEI",
            period="1d",
            interval="5m",
            progress=False,
            auto_adjust=False,
            threads=False
        )

        if data.empty:
            raise Exception("No market data")

        close = data["Close"]

        # Handle MultiIndex returned by yfinance
        if hasattr(close, "columns"):
            close = close.iloc[:, 0]

        close = close.dropna()

        if close.empty:
            raise Exception("No closing prices")

        price = float(close.iloc[-1])

        previous = close.iloc[:-1].tail(20)

        if previous.empty:
            support = price
            resistance = price
        else:
            support = float(previous.min())
            resistance = float(previous.max())

        cached_data = {
            "price": price,
            "support": support,
            "resistance": resistance,
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        last_fetch = now

        return cached_data

    except Exception as e:

        print("Market data error:", e)

        # Use old data if available
        if cached_data["price"] is not None:
            return cached_data

        return None


@app.route("/")
def home():

    market = get_market_data()

    if market is None:
        return """
        <h2 style="text-align:center;margin-top:50px;">
        Market data temporarily unavailable.
        <br><br>
        Please refresh after a few seconds.
        </h2>
        """

    price = market["price"]
    support = market["support"]
    resistance = market["resistance"]

    if price > resistance:
        alert = "🟢 BUY ALERT"
        alert_class = "buy"

    elif price < support:
        alert = "🔴 SELL ALERT"
        alert_class = "sell"

    else:
        alert = "🟡 WAIT"
        alert_class = "wait"

    return render_template_string(
        HTML,
        price=round(price, 2),
        support=round(support, 2),
        resistance=round(resistance, 2),
        alert=alert,
        alert_class=alert_class,
        time=market["updated"]
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
