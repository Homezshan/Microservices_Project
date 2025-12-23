# app.py
import os
from flask import Flask, request, jsonify
import jwt
import redis
import time

app = Flask(__name__)

SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def get_token():
    auth = request.headers.get("Authorization", "")
    if not auth:
        return None
    return auth.split()[-1]

def verify_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded["sub"], decoded["username"]
    except:
        return None, None

@app.route("/pay", methods=["POST"])
def make_payment():
    token = get_token()
    user_id, username = verify_jwt(token)

    if not user_id:
        return jsonify({"error": "Invalid token"}), 401

    data = request.json or {}
    amount = data.get("amount")

    # Fake payment processing
    transaction_id = f"txn_{int(time.time())}"
    status = "SUCCESS"

    r.set(transaction_id, status)

    return jsonify({
        "transaction_id": transaction_id,
        "status": status,
        "user": username
    })

@app.route("/pay/status/<txn_id>", methods=["GET"])
def get_status(txn_id):
    status = r.get(txn_id)
    if not status:
        return jsonify({"error": "Transaction not found"}), 404
    return jsonify({"transaction_id": txn_id, "status": status})

app.run(host="0.0.0.0", port=5003)
