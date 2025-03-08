from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

mongo = PyMongo(app)
jwt = JWTManager(app)

# Register API blueprint if needed
from routes import routes
app.register_blueprint(routes)

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Form-based Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid credentials, try again."
    return render_template('login.html')

# Form-based Signup Page (Separate or use toggle in login page)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        new_username = request.form['new_username']
        email = request.form['email']
        new_password = request.form['new_password']
        if mongo.db.users.find_one({"username": new_username}):
            return "Username already exists. Try another one."
        hashed_password = generate_password_hash(new_password)
        mongo.db.users.insert_one({"username": new_username, "email": email, "password": hashed_password, "role": "user"})
        return redirect(url_for('login'))
    return render_template('signup.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
