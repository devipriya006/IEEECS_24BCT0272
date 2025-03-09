import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from bson.objectid import ObjectId

app = Flask(__name__)


# Configure MongoDB and secret key using environment variables
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/cinepass_db")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "supersecretkey")  # Use a strong key in production

# Initialize MongoDB
mongo = PyMongo(app)
CORS(app)

# --------------------- Web Routes ---------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/owner_dashboard')
def owner_dashboard():
    return render_template('owner_dashboard.html')

@app.route('/user_dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')

# --------------------- API Endpoints ---------------------

# Signup Endpoint: For owners, mark approved as False; others True.
@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')  # Default to 'user'

    if not all([username, email, password, role]):
        return jsonify({'error': 'All fields are required'}), 400

    if mongo.db.users.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 409

    hashed_password = generate_password_hash(password)
    new_user = {
        'username': username,
        'email': email,
        'password': hashed_password,
        'role': role,
        'approved': False if role == 'owner' else True
    }

    mongo.db.users.insert_one(new_user)
    return jsonify({'message': 'Sign Up successful!'}), 201

# Login Endpoint: Block owner login if not approved.
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400

    user = mongo.db.users.find_one({'username': username})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid password'}), 401

    role = user.get('role', 'user')
    if role == 'owner' and not user.get('approved', False):
        return jsonify({'message': 'Your owner account is pending admin approval.'}), 403

    # Store login info in session
    session['username'] = username  
    session['role'] = role  

    return jsonify({'message': 'Login successful', 'role': role}), 200

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# Admin Endpoint: Get pending owners
@app.route('/api/admin/pending_owners', methods=['GET'])
def pending_owners():
    pending = list(mongo.db.users.find({'role': 'owner', 'approved': False}))
    for owner in pending:
        owner['_id'] = str(owner['_id'])
    return jsonify(pending)

# Admin Endpoint: Approve an owner
@app.route('/api/admin/approve_owner', methods=['POST'])
def approve_owner():
    data = request.json
    owner_id = data.get('owner_id')
    if not owner_id:
        return jsonify({'error': 'Owner ID required'}), 400

    result = mongo.db.users.update_one(
        {'_id': ObjectId(owner_id), 'role': 'owner'},
        {'$set': {'approved': True}}
    )
    return jsonify({'message': 'Owner approved successfully!'}), 200 if result.modified_count == 1 else 400

# Owner: Add a Movie
@app.route('/api/owner/add_movie', methods=['POST'])
def add_movie():
    try:
        if 'username' not in session or session.get('role') != 'owner':
            return jsonify({'error': 'Unauthorized'}), 403  

        data = request.json
        title = data.get('title')
        description = data.get('description')
        ticket_price = data.get('ticket_price')
        total_seats = data.get('total_seats')

        if not all([title, description, ticket_price, total_seats]):
            return jsonify({'error': 'All fields are required'}), 400

        movie = {
            'title': title,
            'description': description,
            'ticket_price': ticket_price,
            'total_seats': total_seats,
            'owner': session['username']
        }

        result = mongo.db.movies.insert_one(movie)
        return jsonify({'message': 'Movie added successfully!', 'id': str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Owner: Get all movies added by them
@app.route('/api/owner/movies', methods=['GET'])
def get_owner_movies():
    try:
        if 'username' not in session or session.get('role') != 'owner':
            return jsonify({'error': 'Unauthorized'}), 403  

        movies = list(mongo.db.movies.find({'owner': session['username']}))  
        for movie in movies:
            movie['_id'] = str(movie['_id'])  

        return jsonify(movies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User: Get all movies from all theater owners
@app.route('/api/movies/all', methods=['GET'])
def get_all_movies():
    try:
        movies = list(mongo.db.movies.find({}, {"_id": 1, "title": 1, "description": 1, "ticket_price": 1, "total_seats": 1}))
        for movie in movies:
            movie["_id"] = str(movie["_id"])  # Convert ObjectId to string for frontend
        return jsonify(movies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User: Book a Movie Ticket
@app.route('/book/<movie_id>', methods=['POST'])
def book_movie(movie_id):
    try:
        if 'username' not in session or session.get('role') != 'user':
            return jsonify({'error': 'Unauthorized'}), 403

        movie = mongo.db.movies.find_one({"_id": ObjectId(movie_id)})
        if not movie:
            return jsonify({'error': 'Movie not found'}), 404

        if movie["total_seats"] <= 0:
            return jsonify({'error': 'No seats available'}), 400

        mongo.db.movies.update_one(
            {"_id": ObjectId(movie_id)},
            {"$inc": {"total_seats": -1}}
        )

        return jsonify({'message': 'Ticket booked successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --------------------- Main Entry ---------------------
if __name__ == "__main__":
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint}, URL: {rule}")
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT or default to 5000
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", "False").lower() == "true")
