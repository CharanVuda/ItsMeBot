import os
import openai 
import requests 
from flask import Flask, jsonify, request

app = Flask(__name__)

whatsapp_token = os.environ.get("WHATSAPP_TOKEN")
verify_token = os.environ.get("VERIFY_TOKEN")

dict_msgs = {}
LANGUGAGE = "en-US"

openai_model = "gpt-3.5-turbo"
openai.api_key = os.getenv("OPENAI_API_KEY")

init_msg = [{"role": "system", "content": "Assume you are Krish Malhotra from the book '2 States' and start responding to further messages in a friendly manner. Do not reveal that you are an AI assistant. Do not mention about the book in conversations",}]

# Validate Webhook is working fine
def validate(request):
    
    token = request.args.get("hub.verify_token")
    mode = request.args.get("hub.mode")
    challenge = request.args.get("hub.challenge")
    
    if mode and token: 
        if mode == "subscribe" and token == verify_token:
            print("Webhook validated!!!")
            return challenge, 200
        else: 
            print("*** Webhook validation failed ***")
            return jsonify({"status": "error", "message": "Webhook Validation failed"}), 403
    else:
        print("Invalid request")
        return jsonify({"status": "error", "message": "Invalid request"}), 400

def send_message(body, message):
    value = body["entry"][0]["changes"][0]["value"]
    phone_number_id = value["metadata"]["phone_number_id"]
    from_number = value["messages"][0]["from"]
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }
    url = "https://graph.facebook.com/v17.0/" + phone_number_id + "/messages"
    data = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"message response: {response.json()}")
    response.raise_for_status()


def append_msgs(message, phone_number, role):

    if phone_number not in dict_msgs:
        dict_msgs[phone_number] = init_msg

    dict_msgs[phone_number].append({"role": role, "content": message})
    print(dict_msgs[phone_number])
    return dict_msgs[phone_number]


def openai_conv(message, from_number):
    try:
        message_log = append_msgs(message, from_number, "user")
        print('message_log: ',message_log)
        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=message_log,
            temperature=0.9,
        )
        response_message = response.choices[0].message["content"]
        print(f"openai response: {response_message}")
        append_msgs(response_message, from_number, "assistant")

    except Exception as e:
        print(f"openai error: {e}")
        response_message = "I am currently busy. Please message me later." 

    return response_message


def process_message(body):
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message["type"] == "text":
        message_body = message["text"]["body"]
        response = openai_conv(message_body, message["from"])
    else:
        response = "I can respond to text messages only at this time."
    send_message(body, response)


@app.route("/", methods=["GET"])
def home():
    return "This is a WhatsApp Webhook for MeBot!!"


@app.route("/webhook", methods=["POST", "GET"])
def webhook():

    if request.method == "GET":
        return validate(request)
    
    elif request.method == "POST":
        body = request.get_json()
        print(f"request: {body}")

        try:
            if body.get("object"):
                if (
                    body.get("entry")
                    and body["entry"][0].get("changes")
                    and body["entry"][0]["changes"][0].get("value")
                    and body["entry"][0]["changes"][0]["value"].get("messages")
                    and body["entry"][0]["changes"][0]["value"]["messages"][0]
                ):
                    process_message(body)
                return jsonify({"status": "ok"}), 200
            else:
                return (
                    jsonify({"status": "error", "message": "Not a valid event"}),
                    404,
                )
        except Exception as e:
            print(f"unknown error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/chathistory", methods=["GET"])
def show_chats():  
    return dict_msgs

@app.route("/clear", methods=["GET"])
def clear_chats():  
    dict_msgs.clear()
    return jsonify({"status": "ok", "message": "Cleared chat history"}), 200

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))