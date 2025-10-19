import os
import re
import requests
from flask import Flask, request, jsonify

# Config from env
PAGE_ACCESS_TOKEN = "EAAnpHaKS0ZAsBPm4HMLst2CeyV8QIGRhZAH7vZAqHGLQKd84SrkgsRZBQATeJAkrIay50ZBEqHZB2WflsklDUGzqWo3SlSx9vLz4eRSffbVGhZAxtt7cYjkJTJg1TtUmt5ba3M6DjppWmZBGhjr2WGd4jigiCNE23MCZASpXFHBUoOaxtKrngCQGeFEX9KxDs62jhDUNXLMwRbwZDZD"
VERIFY_TOKEN = "YOUR_VERIFY_TOKENNNN"
if not PAGE_ACCESS_TOKEN:
    raise RuntimeError("Set PAGE_ACCESS_TOKEN environment variable")

app = Flask(__name__)

DFKZ_API = "https://api.dfkz.xo.je/apis/v3/download.php"

# بسيطة: كتجمع اللينك من النص
URL_REGEX = re.compile(
    r"(https?://[^\s]+)",
    flags=re.IGNORECASE
)

def call_dfkz(social_url):
    """ينادي على API ديال dfkz ويرجع JSON"""
    try:
        resp = requests.get(DFKZ_API, params={"url": social_url}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def send_text(psid, text):
    """يبعث رسالة نصية للمستعمل"""
    url = f"https://graph.facebook.com/v17.0/me/messages"
    payload = {
        "recipient": {"id": psid},
        "message": {"text": text}
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    r = requests.post(url, params=params, json=payload, timeout=20)
    return r.status_code, r.text

def send_video_by_url(psid, video_url, title=None):
    """
    يحاول يصيفط الفيديو مباشرة باستخدام attachment url
    (متطلب: URL خاص ومتوفر للـ Facebook ليحمّلوه من عنده)
    """
    url = f"https://graph.facebook.com/v17.0/me/messages"
    message = {
        "recipient": {"id": psid},
        "message": {
            "attachment": {
                "type": "video",
                "payload": {
                    "url": video_url,
                    "is_reusable": False
                }
            }
        }
    }
    if title:
        # نرسل العنوان قبيل الفيديو (اختياري)
        send_text(psid, title)
    params = {"access_token": PAGE_ACCESS_TOKEN}
    r = requests.post(url, params=params, json=message, timeout=30)
    return r.status_code, r.text

def upload_and_send_video(psid, video_url, filename="video.mp4", title=None):
    """
    احتياطي: يحمل الفيديو محليًّا وبعْدُ يرفع attachment فعليًا عبر
    /me/message_attachments ثم يبعت للمستخدم. (أكثر موثوقية إذا attachment_url مفشل)
    """
    # 1) نحمل الفيديو
    try:
        r = requests.get(video_url, stream=True, timeout=60)
        r.raise_for_status()
    except Exception as e:
        return False, f"download failed: {e}"

    # نحفظ مؤقتاً
    temp_path = f"/tmp/{filename}"
    with open(temp_path, "wb") as f:
        for chunk in r.iter_content(1024*1024):
            if chunk:
                f.write(chunk)

    # 2) نعمل upload للملف كـ attachment
    attach_url = f"https://graph.facebook.com/v17.0/me/message_attachments"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    files = {
        "filedata": (filename, open(temp_path, "rb"), "video/mp4")
    }
    data = {
        "message": '{"attachment":{"type":"video","payload":{}}}'
    }
    try:
        resp = requests.post(attach_url, params=params, files=files, data=data, timeout=60)
        resp.raise_for_status()
        attachment_id = resp.json().get("attachment_id")
    except Exception as e:
        return False, f"upload failed: {e}"

    # 3) نبعت للمستخدم بattachment_id
    send_url = f"https://graph.facebook.com/v17.0/me/messages"
    payload = {
        "recipient": {"id": psid},
        "message": {
            "attachment": {
                "type": "video",
                "payload": {"attachment_id": attachment_id}
            }
        }
    }
    resp2 = requests.post(send_url, params=params, json=payload, timeout=30)
    return resp2.status_code == 200, resp2.text

@app.route("/", methods=["GET"])
def index():
    return "FB Messenger Bot - dfkz video relay"

# Webhook verification (Facebook)
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification token mismatch", 403

# Webhook to receive messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data is None:
        return "No JSON", 400

    # Facebook may batch multiple entries
    for entry in data.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging.get("sender", {}).get("id")
            # رسالة نصية واردة
            if "message" in messaging and "text" in messaging["message"]:
                text = messaging["message"]["text"]
                # نبحث على رابط داخل النص
                m = URL_REGEX.search(text)
                if not m:
                    send_text(sender_id, " ✨عفاك صيفط lia رابط ديال المنشور (مثال: رابط تيك توك أو انستغرام).")
                    continue
                social_link = m.group(1)
                send_text(sender_id, "👾جاري معالجة الرابط...")

                # ناديو على dfkz
                dfkz_resp = call_dfkz(social_link)
                if dfkz_resp.get("error"):
                    send_text(sender_id, "مكينش نجاح فالاتصال بالـ API: " + dfkz_resp["error"])
                    continue

                # ناخدو أول رابط نوع video
                links = dfkz_resp.get("links", [])
                video_url = None
                for link in links:
                    if link.get("type") == "video":
                        video_url = link.get("url")
                        break

                if not video_url:
                    send_text(sender_id, "ما تم العثور على فيديو فهاد الرابط. حاول رابط آخر.")
                    continue

                # نجرب نبعت الفيديو باستعمال attachment_url
                status, resp_text = send_video_by_url(sender_id, video_url, title=dfkz_resp.get("title"))
                if status != 200:
                    # إذا فشل، نجرب upload
                    ok, info = upload_and_send_video(sender_id, video_url)
                    if ok:
                        send_text(sender_id, "تم إرسال الفيديو (upload fallback).")
                    else:
                        send_text(sender_id, "فشل إرسال الفيديو: " + str(info))
                else:
                    send_text(sender_id, "هاهو الفيديو ▶️")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    
