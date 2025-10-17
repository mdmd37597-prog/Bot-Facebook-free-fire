from flask import Flask, request
import requests
import re

app = Flask(__name__)

VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"
PAGE_ACCESS_TOKEN = "EAAnpHaKS0ZAsBPsC16IJvU4odCutNSj2PzbECwzWlPpksfWIZCVhGhrvUaLLDHa1cT5hZCZAs74eKjfwZBzAEdRLFl1PzRsDRPeFJoONA7831L0AEk1NrkbBufdZCFZCVSsh3rgIQ3msAdgEg1q0KUg4ZC7pUiYrmnFgYZBOLixKWYRecf8MzOb8EAGoNwdjGogRdYelPU3phBwZDZD"

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Forbidden", 403
    return "Error", 400


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data["object"] == "page":
        for entry in data["entry"]:
            event = entry["messaging"][0]
            sender_id = event["sender"]["id"]

            if "message" in event and "text" in event["message"]:
                message_text = event["message"]["text"].strip()
                handle_message(sender_id, message_text)

        return "EVENT_RECEIVED", 200

    return "Not Found", 404


def handle_message(sender_id, message_text):
    # نتأكد واش النص فيه فقط أرقام (ID)
    if re.match(r"^\d{6,20}$", message_text):  # ممكن تعدل الطول حسب الـ ID
        user_id = message_text
        url = f"http://217.154.239.23:13984/info={user_id}"

        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            info = data.get("captainBasicInfo", {})
            nickname = info.get("nickname", "غير معروف")
            level = info.get("level", "غير معروف")
            liked = info.get("liked", "0")
            ranking_points = info.get("rankingPoints", "0")
            season = info.get("seasonId", "غير معروف")

            reply = (
                f"✅ تم جلب معلومات الحساب:\n"
                f"📝 الاسم: {nickname}\n"
                f"🎮 المستوى: {level}\n"
                f"❤️ عدد الإعجابات: {liked}\n"
                f"🏆 نقاط الترتيب: {ranking_points}\n"
                f"📅 الموسم: {season}\n\n"
                f"🔸 مطور البوت: AB WJDAN"
            )

            send_message(sender_id, reply)

        except Exception as e:
            print("API Error:", e)
            send_message(sender_id, "⚠️ وقعات مشكلة فـ الخدمة أو الـ ID غير صحيح.")
    else:
        send_message(sender_id, "🔹 مرحبا! من أجل جلب معلومات الحساب، فقط أرسل ID ديال الحساب (بدون أمر).")


def send_message(sender_id, text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": text}
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Send Error:", e)


if __name__ == "__main__":
    app.run(port=3000, debug=True)
        "recipient": {"id": sender_id},
        "message": {"text": text}
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Send Error:", e)


if __name__ == "__main__":
    app.run(port=3000, debug=True)
            
