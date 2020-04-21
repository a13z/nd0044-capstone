# FSDN Capstone Project
## Casting Agency
This is the final project for the full stack developer nanodegree program from Udacity.
The project is based on the suggested Casting Agency specifications. 

The Casting Agency models a company that is responsible for creating movies and managing and assigning actors to those movies. You are an Executive Producer within the company and are creating a system to simplify and streamline your process.

Models:
- Movies with attributes title and release date
- Actors with attributes name, age and gender
- Helper table to create a M2M relationship between Movies and Actors.

Endpoints:
- GET /actors and /movies
- DELETE /actors/ and /movies/
- POST /actors and /movies and
- PATCH /actors/ and /movies/

Roles:
- Casting Assistant: Can view actors and movies
- Casting Director:
    - All permissions a Casting Assistant has and…
    - Add or delete an actor from the database
    - Modify actors or movies
- Executive Producer:
    - All permissions a Casting Director has and…
    - Add or delete a movie from the database

## Getting Started
Pre-requisites and Local Development
Developers using this project should already have Python3 and pip installed on their local machines. 
A virtual environment such as virtualenv, pipenv or conda is highly recommended.

## Backend
From the backend folder run `pip install requirements.txt`. All required packages are included in the requirements file being some of them Flask to build an API, Flask SQLAlchemy to access Postgres database, Flask Migrate for database migrations and Auth0 which provides JWT tokens, Role Based Authentication and roles-based access control (RBAC).

The backend relies on a database to persist the data being Postgres the database being used for this project. Heroku provides postgres database as a free addon.

Once we have a database intance running, we need to provide it as database connection string via a environment variable named `DATABASE_URL`, for example having a local database named udacity_fsdn_capstone:

`export DATABASE_URL=postgres://postgres:mysecretpassword@localhost:5432/udacity_fsdn_capstone`

We also need a few environment variables to setup Auth0. These are
```
export AUTH0_DOMAIN=<your_auth0_domain>
export AUTH0_ALGORITHMS=['<your_algorithms>']
export AUTH0_API_AUDIENCE=<your_api_audience>
```

To run the application run the following commands:
```
export FLASK_APP=app.py
export FLASK_ENV=development
python app.py
```

These commands put the application in development and directs our application to use the __init__.py in the current folder. Working in development mode shows an interactive debugger in the console and restarts the server whenever changes are made. If running locally on Windows, look for the commands in the Flask documentation.

The application will run on http://127.0.0.1:5000/ by default in development.

The application is also deployed in Heroku on http://nd0044-capstone.herokuapp.com/

## Tests
In order to run tests there are two things required. One is the `DATABASE_URL` environment variable and the other one are the Auth0 Tokens for the different type of roles.

### Database
This is a database connection URL string. If the database is running locally and named `udacity_fsdn_capstone_test` we need to export this environment variable in the shell:

```
## export to the shell the DATABASE_URL
export DATABASE_URL=postgres://postgres:mysecretpassword@localhost:5432/udacity_fsdn_capstone_test
```
If the database is not initialised, we need to run migrations with the following command:

```
python manage.py db migrate
```

### Test Auth0 Tokens
In order to test the permissions for the three type of roles, we need to create some tokens.
We could generate the tokens for the three types of roles running the following command:
```
CLIENT_ID=xxxxxx CLIENT_SECRET=yyyyyyy USER_PASSWORD='asdfsdfsdc' python auth/generate_token.py
```
This command will output three environment variables command we need to execute in order to make those tokens available for the tests.

*NOTE:For security reasons, CLIENT_ID, CLIENT_SECRET and USER_PASSWORDS are not in this README or repository and they were shared when the project was submitted.

### Running unit tests
Before running tests we need to drop and to create the test database:

```
## drop database
$dropdb udacity_fsdn_capstone_test

## create database
$createdb udacity_fsdn_capstone_test

## import sample database
psql udacity_fsdn_capstone_test < movie_actors.psql

## run tests
python test_app.py
```

The first time you run the tests, omit the dropdb command.

All tests are kept in that file and should be maintained as updates are made to app functionality.

### Running postman tests
You could also test the api either locally or in heruko using postman collection in the repository. This is run using newman. [newman documentation](https://www.npmjs.com/package/newman):

For development environment:
`newman run -e Development.postman_environment.json fsnd-capstone-movies-actors.postman_collection.json`

For production environemnt:
`newman run -e Production.postman_environment.json fsnd-capstone-movies-actors.postman_collection.json`

*NOTE: Since some of the postman endpoints use a particular id to patch and/or to delete they might not be available if a second time is run. It is advised to change those parameters so the tests. This is not a problem for test environment since database is recreated everytime.

## API Reference Library
These are the methods and resources available in the API.

### Getting Started
- Base URL: The backend app is hosted on `http://nd0044-capstone.herokuapp.com/`
- It can be run locally on `http://127.0.0.1:5000/`
- Authentication: This version of the application requires authentication for all endpoints.

#### GET /movies (Require Authentication. Minimum Casting Assistant Role)
- General:
    - Returns a list of movie objects and success value. 
- Sample: `curl --location --request GET 'localhost:5000/movies' --header 'Content-Type: application/json' --header 'Authorization: Bearer '"$CASTING_ASSISTANT_TOKEN"''`
```
{
  "movies": [
    {
      "id": 2,
      "release_date": "Wed, 22 Nov 1989 00:00:00 GMT",
      "title": "Back to the future 2"
    },
    {
      "id": 3,
      "release_date": "Fri, 25 May 1990 00:00:00 GMT",
      "title": "Back to the future 3"
    },
    {
      "id": 1,
      "release_date": "Sat, 22 Jun 1985 00:00:00 GMT",
      "title": "The Goonies"
    }
  ],
  "success": true
}
```

#### GET /actors (Require Authentication. Minimum Casting Assistant Role)
- General:
    - Returns a list of actors objects and success value.
- Sample: `curl --location --request GET 'localhost:5000/actors' --header 'Content-Type: application/json' --header 'Authorization: Bearer '"$CASTING_ASSISTANT_TOKEN"''`
``` 
{
  "actors": [
    {
      "age": 81,
      "gender": "Male",
      "id": 2,
      "name": "Christopher Allen Lloyd"
    },
    {
      "age": 58,
      "gender": "Female",
      "id": 3,
      "name": "Lea Thompson"
    },
    {
      "age": 53,
      "gender": "Female",
      "id": 4,
      "name": "Claudia Grace Wells"
    },
    {
      "age": 60,
      "gender": "Male",
      "id": 1,
      "name": "Tom Hanks"
    }
  ],
  "success": true
}
```

#### POST /movies (Required Authentication and Executive Producer Role)
- General:
    - Creates a new movie using the title and release date. 
    - Returns the id of the created movie, an array with the details of the movie created and success value.
 
- `curl --location --request POST 'localhost:5000/movies' --header 'Content-Type: application/json' --header 'Authorization: Bearer '"$EXECUTIVE_PRODUCER_TOKEN"'' -d '{"title": "The thing", "release_date": "1990-05-25T00:00:00"}'`
```
{
  "created": 5,
  "movies": [
    {
      "id": 5,
      "release_date": "Fri, 25 May 1990 00:00:00 GMT",
      "title": "The thing"
    }
  ],
  "success": true
}
```

#### POST /actors (Required Authentication and Casting Director or Executive Producer Role)
- General:
    - Creates a new movie using the name, age and gender. 
    - Returns the id of the created movie, an array with the details of new object created and success value.
 
- `curl --location --request POST 'localhost:5000/actors' --header 'Content-Type: application/json' --header 'Authorization: Bearer '"$CASTING_DIRECTOR_TOKEN"'' -d '{"name": "James Dean", "age": "24", "gender": "Male"}'`
```
{
  "actors": [
    {
      "age": 24,
      "gender": "Male",
      "id": 6,
      "name": "James Dean"
    }
  ],
  "created": 6,
  "success": true
}
```

#### PATCH /actors/<actor_id> (Required Authentication and Casting Director or Executive Producer Role)
- General:
    - Modify an actor passed as parameter 
    - Returns an array with the details of object edited and success value.
 
- `curl --location --request PATCH 'localhost:5000/actors/6' --header 'Content-Type: application/json' --header 'Authorization: Bearer '"$CASTING_DIRECTOR_TOKEN"'' -d '{"name": "James Dean", "age": "26", "gender": "Male"}'`
```
{
  "actors": [
    {
      "age": 26,
      "gender": "Male",
      "id": 6,
      "name": "James Dean"
    }
  ],
  "success": true
}
```

#### PATCH /movies/<actor_id> (Required Authentication and Casting Director or Executive Producer Role)
- General:
    - Modify a movie passed as parameter 
    - Returns an array with the details of object edited and success value.
 
- `curl --location --request PATCH 'localhost:5000/movies/5' --header 'Content-Type: application/json' --header 'Authorization: Bearer '"$CASTING_DIRECTOR_TOKEN"'' -d '{"title": "The thang", "release_date": "1990-05-25T00:00:00"}'`
```
{
  "movies": [
    {
      "id": 5,
      "release_date": "Fri, 25 May 1990 00:00:00 GMT",
      "title": "The thang"
    }
  ],
  "success": true
}
```

#### DELETE /movies/<movie_id> (Required Authentication and Executive Producer Role)
- General:
    - Delete a movie passed as parameter 
    - Returns a delete field with the deleted movie id and success value.
 
- `curl --location --request DELETE 'localhost:5000/movies/5' --header 'Content-Type: application/json' --header 'Authorization: Bearer '"$EXECUTIVE_PRODUCER_TOKEN"''`
```
{
  "delete": 5,
  "success": true
}
```

#### DELETE /actors/<actor_id> (Required Authentication and Casting Director or Executive Producer Role)
- General:
    - Delete an actor passed as parameter 
    - Returns a delete field with the deleted movie id and success value.
 
- `curl --location --request DELETE 'localhost:5000/actors/6' --header 'Content-Type: application/json' --header 'Authorization: Bearer '"$CASTING_DIRECTOR_TOKEN"''`
```
{
  "delete": 6,
  "success": true
}
```

## Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:

- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable
- 500: Internal Server Error


# Authors
Thanks to Flask, SQLAlchemy, Flask Migrate, flask CORS developers, Auth0, jose jwt library for their wonderful work in their libraries that made this project a reality.

Authors
Yours truly

# Acknowledgements
Thanks to my parents. :)
