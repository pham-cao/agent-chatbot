from flask import Flask, request
import requests
app = Flask(__name__)
from agent.multi_tool_agent.agent import async_main
VERIFY_TOKEN = "my_secret_token"

@app.route("/", methods=["GET"])
def verify():
    # Facebook webhook verification (GET)
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Verification token mismatch", 403
PAGE_ACCESS_TOKEN = "EAAGOUhOszhoBOwzZCfaDDk1FfGqJD9pwnn9E9CpyOXZBZCy7kx9156UArEvH4hjjuckhxl18HJKVOFrp7ZBdDPioDqJ297hNQNEm39pyhNC8JwtrWL719ZBffxuHMmuqsyHZBhtYbRXT8ZCdw7vmCixYavVbAHV1BW52gTHQz6CZBoHHIunRbTbRZCNHKINYiPJAgzJr8fE82VL3KXHf9"

def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v19.0/me/messages"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    params = {"access_token": PAGE_ACCESS_TOKEN}
    response = requests.post(url, headers=headers, json=payload, params=params)
    print("📤 Sent message:", response.json())
@app.route("/", methods=["POST"])
async def webhook():
    data = request.get_json()
    print("🔔 Received webhook event:")
    print(data)

    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]

            print("------------------------------",sender_id)

            if "message" in event:
                text = event["message"].get("text")
                if text:
                    reply = f"Bạn vừa nói: {text}"
                    reply = await async_main(text)
                    print(reply)
                    send_message(sender_id, reply)

    return "ok", 200

if __name__ == "__main__":
    app.run(port=5555)
