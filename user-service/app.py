# app.py
import os
import datetime
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import jwt

app = Flask(__name__)

# Config from env
DB_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# create tables on first run (only for simple local dev)
with app.app_context():
    db.create_all()

@app.route("/users/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "user exists"}), 409

    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "user created", "user_id": user.id}), 201

@app.route("/users/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    payload = {
        "sub": user.id,
        "username": user.username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=4)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token})

def get_token_from_header():
    auth = request.headers.get("Authorization", "")
    if not auth:
        return None
    # Accept "Bearer <token>" or just token
    parts = auth.split()
    return parts[-1]

@app.route("/users/profile", methods=["GET"])
def profile():
    token = get_token_from_header()
    if not token:
        return jsonify({"error": "authorization required"}), 401
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("sub")
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "user not found"}), 404
        return jsonify({"id": user.id, "username": user.username})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "token expired"}), 401
    except Exception as e:
        return jsonify({"error": "invalid token", "detail": str(e)}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
