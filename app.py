from flask import Flask, render_template_string
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

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

@app.route("/")
def home():

    data = yf.download(
        "^NSEI",
        period="1d",
        interval="5m",
        progress=False,
        auto_adjust=False
    )

    if data.empty:
        return "Market data unavailable. Please refresh."

    close = data["Close"].dropna()

    price = float(close.iloc[-1])

    previous = close.iloc[:-1].tail(20)

    if previous.empty:
        support = price
        resistance = price
    else:
        support = float(previous.min())
        resistance = float(previous.max())

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
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
