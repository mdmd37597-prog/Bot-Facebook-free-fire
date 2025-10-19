import os
import re
import requests
from flask import Flask, request

# إعداد الرموز
PAGE_ACCESS_TOKEN = "EAAnpHaKS0ZAsBPm4HMLst2CeyV8QIGRhZAH7vZAqHGLQKd84SrkgsRZBQATeJAkrIay50ZBEqHZB2WflsklDUGzqWo3SlSx9vLz4eRSffbVGhZAxtt7cYjkJTJg1TtUmt5ba3M6DjppWmZBGhjr2WGd4jigiCNE23MCZASpXFHBUoOaxtKrngCQGeFEX9KxDs62jhDUNXLMwRbwZDZD"
VERIFY_TOKEN = "YOUR_VERIFY_TOKENNNN"
PORT = int(os.getenv("PORT", 5000))

if not PAGE_ACCESS_TOKEN or "YOUR_PAGE_ACCESS_TOKEN" in PAGE_ACCESS_TOKEN:
    raise RuntimeError("Set PAGE_ACCESS_TOKEN environment variable")

app = Flask(__name__)

DFKZ_API = "https://api.dfkz.xo.je/apis/v3/download.php"
URL_REGEX = re.compile(r"(https?://[^\s]+)", flags=re.IGNORECASE)

# لائحة الرسائل اللي تعالجت باش مانعاودوش نردو عليها
processed_mids = set()
MAX_PROCESSED = 2000


def call_dfkz(social_url):
    """ينادي على API ديال dfkz"""
    try:
        r = requests.get(DFKZ_API, params={"url": social_url}, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def send_text(psid, text):
    """يبعث رسالة نصية"""
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {"recipient": {"id": psid}, "message": {"text": text}}
    requests.post(url, params=params, json=payload, timeout=15)


def send_video(psid, video_url, title=None):
    """يبعث الفيديو مباشرة من URL"""
    if title:
        send_text(psid, title)

    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": psid},
        "message": {
            "attachment": {
                "type": "video",
                "payload": {"url": video_url, "is_reusable": False},
            }
        },
    }
    requests.post(url, params=params, json=payload, timeout=30)


@app.route("/", methods=["GET"])
def home():
    return "Bot running ✅"


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification token mismatch", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return "No JSON", 400

    for entry in data.get("entry", []):
        for msg in entry.get("messaging", []):
            message = msg.get("message", {})

            # نتجاهل echo (الردود ديال البوت نفسه)
            if message.get("is_echo"):
                continue

            # نستخرج mid ونتأكد ماعالجناش نفس الرسالة من قبل
            mid = message.get("mid")
            if mid and mid in processed_mids:
                continue
            if mid:
                processed_mids.add(mid)
                if len(processed_mids) > MAX_PROCESSED:
                    processed_mids.clear()

            sender_id = msg.get("sender", {}).get("id")
            if not sender_id:
                continue

            text = message.get("text", "")
            match = URL_REGEX.search(text)
            if not match:
                send_text(sender_id, "🔗 صيفط رابط ديال الفيديو (من تيك توك أو إنستغرام).")
                continue

            social_url = match.group(1)
            send_text(sender_id, "⏳ جاري جلب الفيديو...")

            # نجيب البيانات من dfkz
            dfkz_data = call_dfkz(social_url)
            if "error" in dfkz_data:
                send_text(sender_id, f"❌ خطأ فـ API: {dfkz_data['error']}")
                continue

            links = dfkz_data.get("links", [])
            video_url = next((l["url"] for l in links if l.get("type") == "video"), None)

            if not video_url:
                send_text(sender_id, "❌ ما لقيتش فيديو فالرابط.")
                continue

            # نرسل الفيديو مرة وحدة فقط
            send_video(sender_id, video_url, title=dfkz_data.get("title"))
            send_text(sender_id, "✅ تم إرسال الفيديو.")
            print(f"✔ تم إرسال الفيديو للمستخدم {sender_id}")

    # نجاوب فيسبوك بسرعة باش مايعاودش الويب هوك
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
        
