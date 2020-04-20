import os
import collections
import http.client
import json

conn = http.client.HTTPSConnection("nd0044.eu.auth0.com")

AUDIENCE='capstone'

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

users = []
User = collections.namedtuple('User', 'email password env_var')
casting_assistant = User('casting_assistant%40mail.com', os.environ['USER_PASSWORD'], 'CASTING_ASSISTANT_TOKEN')
casting_director = User('casting_director%40mail.com', os.environ['USER_PASSWORD'], 'CASTING_DIRECTOR_TOKEN')
executive_producer = User('executive_producer%40mail.com', os.environ['USER_PASSWORD'], 'EXECUTIVE_PRODUCER_TOKEN')

users.append(casting_assistant)
users.append(casting_director)
users.append(executive_producer)

for user in users:
    payload = f"grant_type=password&username={user.email}&password={user.password}&audience={AUDIENCE}&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"
    headers = { 'content-type': "application/x-www-form-urlencoded" }

    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse()
    data = res.read()

    data_json = json.loads(data.decode("utf-8"))
    print(f"export {user.env_var}={data_json['access_token']}")
    os.environ[f'{user.env_var}'] = data_json['access_token']
