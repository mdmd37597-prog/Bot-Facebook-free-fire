from flask import Flask, request
import requests
import re

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAnpHaKS0ZAsBPsC16IJvU4odCutNSj2PzbECwzWlPpksfWIZCVhGhrvUaLLDHa1cT5hZCZAs74eKjfwZBzAEdRLFl1PzRsDRPeFJoONA7831L0AEk1NrkbBufdZCFZCVSsh3rgIQ3msAdgEg1q0KUg4ZC7pUiYrmnFgYZBOLixKWYRecf8MzOb8EAGoNwdjGogRdYelPU3phBwZDZD"
VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"

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
                message_text = event["message"]["text"]
                handle_message(sender_id, message_text)

        return "EVENT_RECEIVED", 200

    return "Not Found", 404


def handle_message(sender_id, message_text):
    if message_text.startswith("/like"):
        parts = message_text.split(" ")
        if len(parts) < 2:
            return send_message(sender_id, "❌ المرجو إدخال ID صحيح. مثال: /like 2161073557")

        user_id = parts[1]
        url = f"https://api-likes-alli-ff.vercel.app/like?uid={user_id}"

        try:
            r = requests.get(url, timeout=10)
            api_response = r.text.strip()

            if not api_response:
                return send_message(sender_id, "⚠️ الخدمة تحت صيانة.")

            # استخراج المعلومات باستعمال regex
            uid = re.search(r"UID:\s*(\d+)", api_response)
            name = re.search(r"Name:\s*(.+)", api_response)
            likes_before = re.search(r"Likes Before:\s*(\d+)", api_response)
            likes_after = re.search(r"Likes After:\s*(\d+)", api_response)
            likes_added = re.search(r"Likes Added:\s*(\d+)", api_response)

            uid = uid.group(1) if uid else "غير معروف"
            name = name.group(1) if name else "غير معروف"
            likes_before = likes_before.group(1) if likes_before else "0"
            likes_after = likes_after.group(1) if likes_after else "0"
            likes_added = likes_added.group(1) if likes_added else "0"

            # تنسيق الرد الجديد
            reply = (
                "[✓] تم إرسال بنجاح ✅\n"
                f"- لأيدي : {uid} 💎\n"
                f"-  {name}: اسم الحساب 🍑\n"
                f"- عدد ليكات القديمة : {likes_before}\n"
                f"- عدد ليكات الحالية : {likes_after} ✊🏻\n"
                f"- عدد ليكات المضافة : {likes_added} 💀\n"
                "مطور البوت : https://www.instagram.com/mohamed.abwjdan"
            )

            # إذا مكيزيدش ليكات
            if likes_added == "0":
                reply = "✅ تم استهلاك رصيد اليوم. قوم بمشاركة البوت وعد غداً."

            send_message(sender_id, reply)

        except Exception as e:
            print("API Error:", e)
            send_message(sender_id, "⚠️ الخدمة تحت صيانة.")
    else:
        send_message(sender_id, "🔹 مرحبا! استعمل الأمر /like <id>")


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
                
