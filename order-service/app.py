# app.py
import os
from flask import Flask, request, jsonify
import jwt
from pymongo import MongoClient
from models import get_db

app = Flask(__name__)
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/")

client = MongoClient(MONGO_URL)
db = get_db(client)
orders_col = db["orders"]

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

@app.route("/create", methods=["POST"])
def create_order():
    token = get_token()
    user_id, username = verify_jwt(token)

    if not user_id:
        return jsonify({"error": "Invalid token"}), 401

    data = request.json or {}
    item = data.get("item")
    price = data.get("price")

    order = {
        "item": item,
        "price": price,
        "user_id": user_id,
        "username": username
    }

    result = orders_col.insert_one(order)
    return jsonify({"message": "order created", "order_id": str(result.inserted_id)})

@app.route("/check", methods=["GET"])
def get_orders():
    token = get_token()
    user_id, username = verify_jwt(token)

    if not user_id:
        return jsonify({"error": "Invalid token"}), 401

    orders = list(orders_col.find({"user_id": user_id}, {"_id": 0}))
    return jsonify(orders)

app.run(host="0.0.0.0", port=5002)
