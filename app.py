import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "ReOTrkm1XJLbOU3dCXXH2ckZ9hR8AcZC")
WHAPI_URL = "https://gate.whapi.cloud/messages/text"
TARGET_PHONE = os.getenv("TARGET_PHONE", "886922931135")
RVOL_THRESHOLD = float(os.getenv("RVOL_THRESHOLD", "1.8"))

def send_whatsapp(text):
    headers = {"Authorization": f"Bearer {WHAPI_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": TARGET_PHONE, "body": text}
    try:
        r = requests.post(WHAPI_URL, json=payload, headers=headers, timeout=15)
        print(f"Whapi {r.status_code}: {r.text[:500]}")
        return r.status_code in [200,201]
    except Exception as e:
        print(f"Whapi error: {e}")
        return False

@app.route("/")
def home():
    return "TV Bot V3 Running"

@app.route("/webhook/tv", methods=["POST"])
def webhook_tv():
    data = request.get_json(force=True, silent=True) or {}
    print(f"TV payload: {data}")

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

    tf_map = {"1":"1分","3":"3分","5":"5分","15":"15分","30":"30分","60":"1小時","120":"2小時","240":"4小時","D":"日線","W":"週線","M":"月線"}
    tf_show = tf_map.get(interval, interval)

    sym_upper = str(symbol).upper()
    if "USDT" in sym_upper or "BTC" in sym_upper or "ETH" in sym_upper:
        market = "🪙 虛擬幣"
    elif ".TW" in sym_upper or (sym_upper.isdigit() and len(sym_upper)<=6):
        market = "🇹🇼 台股"
    else:
        market = "🇺🇸 美股"

    burst = "🔥爆量確認" if rvol_f >= RVOL_THRESHOLD else "⚠️量縮"
    emoji = "🚀" if "突破" in direction else "📉" if "跌破" in direction else "🚨"
    change_str = f"\n漲跌: {change_pct}%" if change_pct != "" else ""

    msg = f"""{emoji} TV訊號 [{symbol}] {tf_show}
市場: {market}
方向: {direction} {burst}
價格: {close}{change_str}
RVOL: {rvol}x (門檻 {RVOL_THRESHOLD}x)
支撐: {support} / 壓力: {resistance}
週期: {tf_show} ({interval})
時間: {time_str}
"""

    ok = send_whatsapp(msg)
    return jsonify({"ok": ok}), 200 if ok else 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
