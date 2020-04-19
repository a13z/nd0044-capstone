import os, sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import setup_db, Movie, Actor
from .auth.auth import AuthError, requires_auth


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={ r'/*': {'origins': '*'}}, supports_credentials=True)

    @app.after_request
    def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

    ## ROUTES
    '''
        GET /movies
        returns status code 200 and json {"success": True, "movies": movies} where movies is the list of movies
            or appropriate status code indicating reason for failure
    '''
    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies():
        movies = Movie.query.all()
        if movies is None:
            abort(404)

        movies_list = [movie.format() for movie in movies]

        return jsonify({
            "success": True,
            "movies": movies_list
        })

    '''
        POST /movies
        returns status code 200 and json {"success": True, "movies": movie} where movie an array containing only the newly created movie
            or appropriate status code indicating reason for failure
    '''
    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def add_movie():
        body = request.get_json()
        print("Movie POST body", body)
        title = body.get('title')
        release_date = body.get('release_date')

        try:
            movie = Movie(title=title, release_date=json.dumps(release_date))
            movie.insert()
            return jsonify({
                "success": True,
                "created": movie.id,
                "movies": [movie.format()]
            })
        except Exception as e:
            error = True
            print(sys.exc_info())
            print(e)
            abort(422)

    '''
        PATCH /movies/<id>
        returns status code 200 and json {"success": True, "movies": movie} where movie an array containing only the updated movie
            or appropriate status code indicating reason for failure
    '''
    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movie(movie_id):
        body = request.get_json()
        title = body.get('title')
        release_date = body.get('release_date', [])

        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        
        if movie is None:
            abort(404)
        
        try:
            movie.title = title
            movie.release_date = json.dumps(release_date)
            movie.update()

            return jsonify({
                "success": True,
                "movies": [movie.format()]
            })

        except Exception as e:
            error = True
            print(sys.exc_info())
            print(e)
            abort(422)

    '''
        DELETE /movies/<id>
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movie(movie_id):
        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        
        if movie is None:
            abort(404)
        
        try:
            movie.delete()

            return jsonify({
                "success": True,
                "delete": movie.id
            })

        except Exception as e:
            error = True
            print(sys.exc_info())
            print(e)
            abort(422)

    ### Actors API

    '''
        GET /actors
        returns status code 200 and json {"success": True, "actors": actors} where actors is the list of actors
            or appropriate status code indicating reason for failure
    '''

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors():
        actors = Actor.query.all()
        if actors is None:
            abort(404)

        actors_list = [actor.format() for actor in actors]

        return jsonify({
            "success": True,
            "actors": actors_list
        })

    '''
        POST /actors
        returns status code 200 and json {"success": True, "actors": actor} where actor an array containing only the newly created actor
            or appropriate status code indicating reason for failure
    '''
    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def add_actor():
        print(request.get_json())
        body = request.get_json()
        print("Actor POST body ", body)
        name = body.get('name')
        age = body.get('age')
        gender = body.get('gender')

        try:
            actor = Actor(name=name, age=age, gender=gender)
            actor.insert()
            return jsonify({
                "success": True,
                "created": actor.id,
                "actors": [actor.format()]
            })
        except Exception as e:
            error = True
            print(sys.exc_info())
            print(e)
            abort(422)

    '''
        PATCH /actors/<id>
        returns status code 200 and json {"success": True, "actors": actor} where actor an array containing only the updated actor
            or appropriate status code indicating reason for failure
    '''
    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actor(actor_id):
        body = request.get_json()
        name = body.get('name')
        age = body.get('age')
        gender = body.get('gender')

        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        
        if actor is None:
            abort(404)
        
        try:
            actor.name = name
            actor.age = age
            actor.gender = gender
            actor.update()

            return jsonify({
                "success": True,
                "actors": [actor.format()]
            })

        except Exception as e:
            error = True
            print(sys.exc_info())
            print(e)
            abort(422)

    '''
        DELETE /actors/<id>
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actor(actor_id):
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        
        if actor is None:
            abort(404)
        
        try:
            actor.delete()

            return jsonify({
                "success": True,
                "delete": actor.id
            })

        except Exception as e:
            error = true
            print(sys.exc_info())
            print(e)
            abort(422)


    ## Error Handling

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "resouce not found"
            }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
            }), 422 

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500   


    '''
    @DONE implement error handler for AuthError
        error handler should conform to general task above 
    '''
    @app.errorhandler(AuthError)
    def auth_error(AuthError):
        response = {
            "success": True,
            "error": AuthError.status_code,
            "message": AuthError.error
        }
        return jsonify(response), AuthError.status_code

    return app

app = create_app()

if __name__ == '__main__':
    app.run()
