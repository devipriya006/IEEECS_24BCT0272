from flask import Blueprint, request, jsonify
from extensions import mongo

routes = Blueprint('routes', __name__)

@routes.route('/test', methods=['GET'])
def test_route():
    return "Test route is working!"

@routes.route('/movies', methods=['GET'])
def get_movies():
    movies = mongo.db.movies.find()
    movie_list = []
    for movie in movies:
        movie_list.append({
            'title': movie['title'],
            'year': movie['year'],
            'director': movie['director']
        })
    return jsonify(movie_list)
