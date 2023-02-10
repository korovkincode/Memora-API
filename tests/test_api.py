import sys, os
sys.path.append('..')

try:
    os.remove("db/Users.sqlite")
    os.remove("db/Posts.sqlite")
    os.remove("db/Tags.sqlite")
    os.remove("db/Link.sqlite")
except:
    pass

from api import app
from fastapi.testclient import TestClient

TOKEN = ""
client = TestClient(app)


def test_signup():
    data = {"username": "test", "password": "1234", "name": "Test", "surname": "Test", 
    "email": "test1234@gmail.com", "gender": "Male", "birthdate": "01.01.1970"}
    response = client.post("/api/signup/", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "Add new user"}
    response = client.post("/api/signup", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "User with this username already exists"}

def test_auth():
    data = {"username": "test1", "password": "1234"}
    response = client.post("/api/login/", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "No such user"}
    data["username"] = "test"
    response = client.post("/api/login/", json=data)
    assert response.status_code == 200
    global TOKEN
    TOKEN = response.json()["message"]
    assert len(TOKEN) == 10

def test_createPost():
    data = {"data": "Hello, World!"}
    response = client.post("/api/post/create/", headers={"token": TOKEN + ","}, json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "No such user"}
    response = client.post("/api/post/create/", headers={"token": TOKEN}, json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "/api/post/1/read/"
    response = client.post("/api/post/create/file/", headers={"token": TOKEN},
    files={"file": ("picture.jpg", open("picture.jpg", "rb"), "image/jpeg")})
    assert response.status_code == 200
    assert response.json()["message"] == "/api/post/2/read/"

def test_readPost():
    response = client.get("/api/post/3/read")
    assert response.status_code == 200
    assert response.json() == {"message": "No token!"}