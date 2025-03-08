from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo

routes = Blueprint('routes', __name__)

# API Endpoint for User Registration
@routes.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    
    if not username or not password or not email:
        return jsonify({"message": "All fields are required"}), 400

    if mongo.db.users.find_one({"username": username}):
        return jsonify({"message": "User already exists"}), 400

    hashed = generate_password_hash(password)
    mongo.db.users.insert_one({"username": username, "email": email, "password": hashed, "role": "user"})
    return jsonify({"message": "User registered successfully"}), 201

# API Endpoint for User Login
@routes.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    user = mongo.db.users.find_one({"username": username})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    token = create_access_token(identity=username)
    return jsonify({"access_token": token}), 200

# Additional endpoints (movies, booking, etc.) can be added similarly.
