from flask import Flask, request, jsonify
import os

app = Flask(__name__)
DATA_FILE = "/data/messages.txt"

@app.route("/")
def home():
    return "DevOps Lab Project App is Running!"

@app.route("/add", methods=["POST"])
def add_message():
    message = request.json.get("message")
    if not message:
        return jsonify({"error": "No message provided"}), 400

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "a") as f:
        f.write(message + "\n")

    return jsonify({"status": "Message saved successfully"})

@app.route("/messages", methods=["GET"])
def get_messages():
    if not os.path.exists(DATA_FILE):
        return jsonify([])

    with open(DATA_FILE, "r") as f:
        messages = f.read().splitlines()

    return jsonify(messages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
