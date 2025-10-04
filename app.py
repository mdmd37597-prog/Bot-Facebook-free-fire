import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAnpHaKS0ZAsBPsC16IJvU4odCutNSj2PzbECwzWlPpksfWIZCVhGhrvUaLLDHa1cT5hZCZAs74eKjfwZBzAEdRLFl1PzRsDRPeFJoONA7831L0AEk1NrkbBufdZCFZCVSsh3rgIQ3msAdgEg1q0KUg4ZC7pUiYrmnFgYZBOLixKWYRecf8MzOb8EAGoNwdjGogRdYelPU3phBwZDZD"

# ---------------------------
# Function to send messages
# ---------------------------
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, json=payload)

# ---------------------------
# Handle Like Command
# ---------------------------
def handle_like(uid, sender_id):
    try:
        api_url = f"https://api-likes-alli-ff.vercel.app/like?uid={uid}"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            uid = uid
            name = data.get("Name", "Unknown")
            likes_before = data.get("Likes Before", 0)
            likes_after = data.get("Likes After", 0)
            likes_added = data.get("Likes Added", 0)

            if likes_added == 0:
                reply = "⚠️ تم استهلاك رصيد اليوم، جرب غدا."
            else:
                reply = (
                    f"[✓] تم إرسال بنجاح ✅\n"
                    f"- لأيدي : {uid} 💎\n"
                    f"- اسم الحساب : {name} 🍑\n"
                    f"- عدد ليكات القديمة : {likes_before}\n"
                    f"- عدد ليكات الحالية : {likes_after} ✊🏻\n"
                    f"- عدد ليكات المضافة : {likes_added} 💀\n"
                    f"مطور البوت : AB WJDAN"
                )
        else:
            reply = "❌ الخدمة تحت صيانة"

    except Exception as e:
        reply = "❌ الخدمة تحت صيانة"

    send_message(sender_id, reply)

# ---------------------------
# Handle Info Command
# ---------------------------
def handle_info(uid, sender_id):
    try:
        api_url = f"https://api-info-alli-ff-v1.vercel.app/{uid}"
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Player info
            player_nickname = data["basicInfo"]["nickname"]
            player_level = data["basicInfo"]["level"]
            player_liked = data["basicInfo"]["liked"]

            # Clan captain
            captain_nickname = data["captainBasicInfo"]["nickname"]
            captain_level = data["captainBasicInfo"]["level"]
            captain_liked = data["captainBasicInfo"]["liked"]

            # Clan info
            clan_name = data["clanBasicInfo"]["clanName"]
            clan_level = data["clanBasicInfo"]["clanLevel"]
            clan_members = data["clanBasicInfo"]["memberNum"]

            reply = (
                "🎮 Player Info:\n"
                f"✨ Nickname: {player_nickname}\n"
                f"📈 Level: {player_level}\n"
                f"👍 Likes: {player_liked}\n\n"
                "👑 Clan Captain Info:\n"
                f"✨ Nickname: {captain_nickname}\n"
                f"📈 Level: {captain_level}\n"
                f"👍 Likes: {captain_liked}\n\n"
                "🏰 Clan Info:\n"
                f"🏷️ Name: {clan_name}\n"
                f"⭐ Level: {clan_level}\n"
                f"👥 Members: {clan_members}"
            )
        else:
            reply = "❌ لم أتمكن من جلب المعلومات الآن."

    except Exception as e:
        reply = "❌ لم أتمكن من جلب المعلومات الآن."

    send_message(sender_id, reply)

# ---------------------------
# Webhook for Facebook
# ---------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    for entry in data.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            if "message" in messaging_event:
                sender_id = messaging_event["sender"]["id"]
                message_text = messaging_event["message"].get("text", "")

                if message_text.startswith("/like"):
                    try:
                        uid = message_text.split()[1]
                        handle_like(uid, sender_id)
                    except:
                        send_message(sender_id, "⚠️ استعمل هكدا: /like <uid>")
                elif message_text.startswith("/info"):
                    try:
                        uid = message_text.split()[1]
                        handle_info(uid, sender_id)
                    except:
                        send_message(sender_id, "⚠️ استعمل هكدا: /info <uid>")
                else:
                    send_message(sender_id, "⚙️ الأوامر المتاحة:\n/like <uid>\n/info <uid>")

    return "ok", 200

# Verify webhook
@app.route("/webhook", methods=["GET"])
def verify():
    VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Verification token mismatch", 403


if __name__ == "__main__":
    app.run(port=3000)
    
