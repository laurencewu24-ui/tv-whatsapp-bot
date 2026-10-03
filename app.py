import os, threading
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "ReOTrkm1XJLbOU3dCXXH2ckZ9hR8AcZC")
WHAPI_URL = "https://gate.whapi.cloud/messages/text"
TARGET_PHONE = os.getenv("TARGET_PHONE", "886922931135")
RVOL_THRESHOLD = float(os.getenv("RVOL_THRESHOLD", "1.8"))

def send_whatsapp_async(text):
    def do_send():
        try:
            headers = {"Authorization": f"Bearer {WHAPI_TOKEN}", "Content-Type": "application/json"}
            requests.post(WHAPI_URL, json={"to": TARGET_PHONE, "body": text}, headers=headers, timeout=15)
        except Exception as e:
            print(f"Whapi error: {e}")
    threading.Thread(target=do_send, daemon=True).start()

@app.route("/")
def home():
    return "TV Bot V4 Fast Response Running"

@app.route("/webhook/tv", methods=["POST"])
def webhook_tv():
    data = request.get_json(force=True, silent=True) or {}
    
    symbol = data.get("symbol", "UNKNOWN")
    close = data.get("close", 0)
    rvol = data.get("RVOL", 0)
    support = data.get("support", "-")
    resistance = data.get("resistance", "-")
    direction = data.get("方向", "-")
    interval = str(data.get("interval", "-"))
    time_str = data.get("time", "-")
    change_pct = data.get("漲跌幅", "")

    try:
        rvol_f = float(str(rvol).replace("x",""))
    except:
        rvol_f = 0

    tf_map = {"1":"1分","3":"3分","5":"5分","15":"15分","30":"30分","60":"1小時","120":"2小時","240":"4小時","D":"日線"}
    tf_show = tf_map.get(interval, interval)
    
    market = "🪙 虛擬幣" if "USDT" in symbol.upper() else "🇹🇼 台股" if ".TW" in symbol.upper() or symbol.isdigit() else "🇺🇸 美股"
    burst = "🔥爆量確認" if rvol_f >= RVOL_THRESHOLD else "⚠️"
    emoji = "🚀" if "突破" in direction else "📉"

    msg = f"""{emoji} TV訊號 [{symbol}] {tf_show}
市場: {market}
方向: {direction} {burst}
價格: {close} ({change_pct}%)
RVOL: {rvol}x
支撐: {support} / 壓力: {resistance}
週期: {tf_show} ({interval})
時間: {time_str}
"""
    # 馬上回傳給TradingView，不讓它timeout
    send_whatsapp_async(msg)
    return jsonify({"ok": True, "received": symbol}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
