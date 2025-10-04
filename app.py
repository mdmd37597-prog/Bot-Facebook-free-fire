import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"
PAGE_ACCESS_TOKEN = "EAAnpHaKS0ZAsBPsC16IJvU4odCutNSj2PzbECwzWlPpksfWIZCVhGhrvUaLLDHa1cT5hZCZAs74eKjfwZBzAEdRLFl1PzRsDRPeFJoONA7831L0AEk1NrkbBufdZCFZCVSsh3rgIQ3msAdgEg1q0KUg4ZC7pUiYrmnFgYZBOLixKWYRecf8MzOb8EAGoNwdjGogRdYelPU3phBwZDZD"


# إرسال رسالة لمسنجر
def send_message(recipient_id, message):
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    requests.post(url, params=params, headers=headers, json=data)


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge
        return "Invalid token"
    elif request.method == "POST":
        data = request.get_json()
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                if "message" in event and "text" in event["message"]:
                    sender_id = event["sender"]["id"]
                    message_text = event["message"]["text"]

                    if message_text.startswith("/like"):
                        parts = message_text.split(" ")
                        if len(parts) == 2:
                            uid = parts[1]
                            url = f"https://api-likes-alli-ff.vercel.app/like?uid={uid}"
                            try:
                                res = requests.get(url).json()
                                name = res.get("Name", "Unknown")
                                before = res.get("Likes Before", 0)
                                after = res.get("Likes After", 0)
                                added = res.get("Likes Added", 0)

                                if added == 0:
                                    reply = "رصيدك اليومي تم استهلاكه 😔، جرب غدا 🔄"
                                else:
                                    reply = f"""[✓] تم إرسال بنجاح ✅
- لأيدي : {uid} 💎
- اسم الحساب : {name} 🍑
- عدد ليكات القديمة : {before}
- عدد ليكات الحالية : {after} ✊🏻
- عدد ليكات المضافة : {added} 💀
مطور البوت : AB WJDAN"""
                                send_message(sender_id, reply)
                            except:
                                send_message(sender_id, "❌ الخدمة تحت صيانة")

                    elif message_text.startswith("/info"):
                        parts = message_text.split(" ")
                        if len(parts) == 2:
                            uid = parts[1]
                            url = f"https://api-info-alli-ff-v1.vercel.app/{uid}"
                            try:
                                res = requests.get(url).json()

                                # player info
                                player = res.get("basicInfo", {})
                                captain = res.get("captainBasicInfo", {})
                                clan = res.get("clanBasicInfo", {})

                                reply = f"""🎮 Player Info:
✨ Nickname: {player.get('nickname')}
📈 Level: {player.get('level')}
👍 Likes: {player.get('liked')}

👑 Clan Captain Info:
✨ Nickname: {captain.get('nickname')}
📈 Level: {captain.get('level')}
👍 Likes: {captain.get('liked')}

🏰 Clan Info:
🏷️ Name: {clan.get('clanName')}
⭐ Level: {clan.get('clanLevel')}
👥 Members: {clan.get('memberNum')}
"""
                                send_message(sender_id, reply)
                            except:
                                send_message(sender_id, "❌ الخدمة تحت صيانة")

        return "EVENT_RECEIVED"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
                    
