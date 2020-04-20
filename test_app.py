import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from database.models import setup_db, Movie, Actor


class CapstonesTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ['DATABASE_URL']
        self.headers_casting_assistant = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + os.environ.get('CASTING_ASSISTANT_TOKEN')}
        self.headers_casting_director = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + os.environ.get('CASTING_DIRECTOR_TOKEN')}
        self.headers_executive_producer = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + os.environ.get('EXECUTIVE_PRODUCER_TOKEN')}

        setup_db(self.app, self.database_path)

        self.new_movie = {
            'title': 'The Goonies',
            'release_date': '1985-06-22T00:00:00'
        }
        self.new_actor = {
            'name': 'Tom Hanks',
            'age': '60',
            'gender': 'Male'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            # self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        # self.app = Flask(__name__)
        # self.db.init_app(self.app)
        with self.app.app_context(): 
            self.db.session.remove()
            self.db.drop_all()

    def test_401_get_movies_without_authentication(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message']['code'], "authorization_header_missing")
        self.assertEqual(data['message']['description'], "Authorization header is expected.")

    def test_401_get_actors_without_authentication(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message']['code'], "authorization_header_missing")
        self.assertEqual(data['message']['description'], "Authorization header is expected.")

    def test_401_post_new_movie_without_authentication(self):
        res = self.client().post('/movies', json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message']['code'], "authorization_header_missing")
        self.assertEqual(data['message']['description'], "Authorization header is expected.")

    def test_401_post_new_actor_without_authentication(self):
        res = self.client().post('/actors', json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message']['code'], "authorization_header_missing")
        self.assertEqual(data['message']['description'], "Authorization header is expected.")

    def test_401_patch_new_movie_without_authentication(self):
        res = self.client().patch('/movies/1', json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message']['code'], "authorization_header_missing")
        self.assertEqual(data['message']['description'], "Authorization header is expected.")

    def test_401_patch_new_actor_without_authentication(self):
        res = self.client().patch('/actors/1', json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message']['code'], "authorization_header_missing")
        self.assertEqual(data['message']['description'], "Authorization header is expected.")

    def test_401_delete_new_movie_without_authentication(self):
        res = self.client().delete('/movies/1', json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message']['code'], "authorization_header_missing")
        self.assertEqual(data['message']['description'], "Authorization header is expected.")

    def test_401_delete_new_actor_without_authentication(self):
        res = self.client().delete('/actors/1', json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message']['code'], "authorization_header_missing")
        self.assertEqual(data['message']['description'], "Authorization header is expected.")

    def test_get_movies_with_casting_assistant_role(self):
        res = self.client().get('/movies', headers=self.headers_casting_assistant)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        self.assertEqual(len(data['movies']), 3)

    def test_get_actors_as_casting_assistant(self):
        res = self.client().get('/actors', headers=self.headers_casting_assistant)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertEqual(len(data['actors']), 4)

    def test_403_post_new_actor_as_casting_assistant(self):
        res = self.client().post('/actors', headers=self.headers_casting_assistant, json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['message']['code'], "forbidden")
        self.assertEqual(data['message']['description'], "Forbidden")

    def test_403_post_new_movie_as_casting_assistant(self):
        res = self.client().post('/movies', headers=self.headers_casting_assistant, json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['message']['code'], "forbidden")
        self.assertEqual(data['message']['description'], "Forbidden")

    def test_post_new_actor_as_casting_director(self):
        res = self.client().post('/actors', headers=self.headers_casting_director, json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['actors'])
        self.assertEqual(len(data['actors']), 1)
        self.assertEqual(data['actors'][0]['name'], 'Tom Hanks')

        # remove the actor we added to keep the data consistent for the rest of the test and check permissions
        actor = Actor.query.filter(Actor.id == data['created']).one_or_none()
        self.assertEqual(actor.name, self.new_actor['name'])

        res2 = self.client().delete(f'/actors/{data["created"]}',  headers=self.headers_casting_director,)
        data2 = json.loads(res2.data)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(data2['success'], True)
        self.assertEqual(data2['delete'], data['created'])

    def test_403_post_new_movie_as_casting_director(self):
        res = self.client().post('/movies', headers=self.headers_casting_director, json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['message']['code'], "forbidden")
        self.assertEqual(data['message']['description'], "Forbidden")

    def test_patch_movie_as_casting_director(self):
        res = self.client().patch('/movies/1', headers=self.headers_casting_director, json=self.new_movie)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        self.assertEqual(len(data['movies']), 1)
        self.assertEqual(data['movies'][0]['title'], 'The Goonies')

    def test_403_delete_movie_as_casting_director(self):
        res = self.client().delete('/movies/1', headers=self.headers_casting_director, json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['message']['code'], "forbidden")
        self.assertEqual(data['message']['description'], "Forbidden")

    def test_post_new_actor_as_executive_producer(self):
        res = self.client().post('/movies', headers=self.headers_executive_producer, json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['movies'])
        self.assertEqual(len(data['movies']), 1)
        self.assertEqual(data['movies'][0]['title'], 'The Goonies')
        
        # remove the actor we added to keep the data consistent for the rest of the test and check permissions
        movie = Movie.query.filter(Movie.id == data['created']).one_or_none()
        self.assertEqual(movie.title, self.new_movie['title'])

        res2 = self.client().delete(f'/movies/{data["created"]}',  headers=self.headers_executive_producer)
        data2 = json.loads(res2.data)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(data2['success'], True)
        self.assertEqual(data2['delete'], data['created'])

    def test_patch_actor_as_executive_producer(self):
        res = self.client().patch('/actors/1', headers=self.headers_executive_producer, json=self.new_actor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertEqual(len(data['actors']), 1)
        self.assertEqual(data['actors'][0]['name'], 'Tom Hanks')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()