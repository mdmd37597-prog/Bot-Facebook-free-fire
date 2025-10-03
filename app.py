from flask import Flask, request
import requests

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAnpHaKS0ZAsBPsC16IJvU4odCutNSj2PzbECwzWlPpksfWIZCVhGhrvUaLLDHa1cT5hZCZAs74eKjfwZBzAEdRLFl1PzRsDRPeFJoONA7831L0AEk1NrkbBufdZCFZCVSsh3rgIQ3msAdgEg1q0KUg4ZC7pUiYrmnFgYZBOLixKWYRecf8MzOb8EAGoNwdjGogRdYelPU3phBwZDZD"
VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"

# ===== Verify webhook =====
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


# ===== Handle webhook events =====
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
            data = r.json()

            if not data:
                return send_message(sender_id, "⚠️ الخدمة تحت صيانة.")

            likes_before = data.get("Likes Before", 0)
            likes_after = data.get("Likes After", 0)
            likes_added = data.get("Likes Added", 0)
            name = data.get("PlayerNickname", data.get("Name", "Unknown"))

            if int(likes_added) == 0:
                return send_message(sender_id, "✅ تم استهلاك رصيد اليوم. قوم بمشاركة البوت وعد غداً.")

            reply = (
                f"- Name: {name}\n"
                f"- Likes Before: {likes_before}\n"
                f"- Likes After: {likes_after}\n"
                f"- Likes Added: {likes_added}"
            )
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
            
