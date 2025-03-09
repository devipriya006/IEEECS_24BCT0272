from flask import Blueprint, request, jsonify
from extensions import mongo
from bson.objectid import ObjectId

owner_routes = Blueprint('owner_routes', __name__)

# API endpoint to add a movie (used by owner_dashboard and signup)
@owner_routes.route('/api/owner/add_movie', methods=['POST'])
def add_movie():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    price = data.get('price')
    seats = data.get('seats')
    
    if not title or not description or not price or not seats:
        return jsonify({"error": "All fields are required"}), 400
    
    movie = {
        'title': title,
        'description': description,
        'price': price,
        'seats': seats
    }
    mongo.db.movies.insert_one(movie)
    return jsonify({"message": "Movie added successfully!"}), 201

# API endpoint to fetch owner's movies
@owner_routes.route('/api/owner/movies', methods=['GET'])
def get_owner_movies():
    movies = mongo.db.movies.find()
    movie_list = []
    for movie in movies:
        movie_list.append({
            '_id': str(movie.get('_id')),
            'title': movie.get('title'),
            'description': movie.get('description'),
            'price': movie.get('price'),
            'seats': movie.get('seats')
        })
    return jsonify(movie_list)

# API endpoint to update movie seats
@owner_routes.route('/api/owner/update_seats', methods=['POST'])
def update_seats():
    data = request.get_json()
    movie_id = data.get('movie_id')
    seats = data.get('seats')
    if not movie_id or seats is None:
        return jsonify({"error": "Movie ID and seats required"}), 400
    
    result = mongo.db.movies.update_one(
        {"_id": ObjectId(movie_id)},
        {"$set": {"seats": seats}}
    )
    if result.modified_count == 1:
        return jsonify({"message": "Seats updated successfully!"}), 200
    else:
        return jsonify({"error": "Failed to update seats"}), 400
