from flask import Flask, jsonify
import yfinance as yf

app = Flask(__name__)

@app.route("/")
def home():
    return """<html><head><title>NIFTY 50 Alert</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{font-family:Arial;background:#111;color:white;text-align:center;padding:30px}.box{max-width:500px;margin:auto;padding:25px;border:1px solid #444;border-radius:15px}.price{font-size:36px;font-weight:bold;margin:15px}.item{font-size:20px;margin:12px}button{padding:12px 20px;border:0;border-radius:8px;font-size:16px}</style>
</head><body><div class="box"><h1>NIFTY 50 Alert</h1><div id="data">Loading...</div><button onclick="loadData()">Refresh</button></div>
<script>
async function loadData(){document.getElementById('data').innerHTML='Loading...';try{const r=await fetch('/api/nifty');const d=await r.json();if(d.error)throw new Error(d.error);document.getElementById('data').innerHTML=`<div class="price">₹${d.price}</div><div class="item">Support: ₹${d.support}</div><div class="item">Resistance: ₹${d.resistance}</div><div class="item">Updated: ${d.time}</div>`}catch(e){document.getElementById('data').innerHTML='Data error: '+e.message}}loadData();
</script></body></html>"""

@app.route("/api/nifty")
def nifty():
    try:
        data = yf.download("^NSEI", period="5d", interval="15m", progress=False, auto_adjust=False)
        if data.empty:
            return jsonify({"error":"NIFTY data not available"}), 503
        close = data["Close"].dropna()
        if hasattr(close, "columns"):
            close = close.iloc[:,0]
        recent = close.tail(20)
        return jsonify({
            "price": round(float(close.iloc[-1]),2),
            "support": round(float(recent.min()),2),
            "resistance": round(float(recent.max()),2),
            "time": str(close.index[-1])
        })
    except Exception as e:
        return jsonify({"error":str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
