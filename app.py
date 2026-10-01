from flask import Flask, request
import requests

app = Flask(__name__)

# === 已填好你的資訊 ===
WHAPI_TOKEN = "ReOTrkm1XJLbOU3dCXXH2ckZ9hR8AcZC"
YOUR_NUMBER = "886922931135"  # +886 922 931 135
API_URL = "https://gate.whapi.cloud/"

def send_whatsapp(tv_data):
    url = f"{API_URL}messages/text"
    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        rvol = float(tv_data.get("RVOL", 0))
    except:
        rvol = 0
    symbol = tv_data.get("symbol", "BTCUSDT")
    close_p = tv_data.get("close", 0)
    support = tv_data.get("support", 0)
    resistance = tv_data.get("resistance", 0)
    direction = tv_data.get("方向", "")
    interval = tv_data.get("interval", "D")

    burst = "🔥爆量確認" if rvol >= 1.8 else "⚠️量縮跌破"

    body = f"""🚨 *TV訊號觸發* [{symbol}] {interval}
*方向:* {direction} {burst}
*價格:* {close_p}
*RVOL:* {rvol}x (門檻1.8x)
*支撐:* {support}
*壓力:* {resistance}
*時間:* {tv_data.get('time','')}
> 跌破82500.1訊號
"""

    payload = {
        "to": YOUR_NUMBER,
        "body": body
    }

    r = requests.post(url, headers=headers, json=payload)
    print("Whapi response:", r.status_code, r.text)
    return r.text

@app.route("/webhook/tv", methods=["POST"])
def tv_webhook():
    data = request.get_json(force=True)
    print("收到TV:", data)

    # 只發 RVOL >=1.8 的，避免洗版
    try:
        if float(data.get("RVOL", 0)) < 1.8:
            print("RVOL不足1.8，跳過")
            return "skip low rvol", 200
    except:
        pass

    send_whatsapp(data)
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return "TV to WhatsApp Bot is Running. POST to /webhook/tv"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
