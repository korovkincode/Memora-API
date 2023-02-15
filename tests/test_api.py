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
    response = client.post("/api/signup/", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "User with this username already exists"}

def test_auth():
    data = {"username": "test1", "password": "1234"}
    response = client.post("/api/login/", json=data)
    assert response.status_code == 404
    assert response.json() == {"detail": "No such user!"}
    data["username"] = "test"
    response = client.post("/api/login/", json=data)
    assert response.status_code == 200
    global TOKEN
    TOKEN = response.json()["message"]
    assert len(TOKEN) == 10

def test_createPost():
    data = {"data": "Hello, World!"}
    response = client.post("/api/post/")
    assert response.status_code == 422
    response = client.post("/api/post/", headers={"token": TOKEN + ","}, json=data)
    assert response.status_code == 404
    assert response.json() == {"detail": "No such user!"}
    response = client.post("/api/post/", headers={"token": TOKEN}, json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "/api/post/1/"
    response = client.post("/api/post/file/", headers={"token": TOKEN},
    files={"file": ("picture.jpg", open("picture.jpg", "rb"), "image/jpeg")})
    assert response.status_code == 200
    assert response.json()["message"] == "/api/post/2/"

def test_readPost():
    response = client.get("/api/post/3/")
    assert response.status_code == 200
    assert response.json() == {"message": "No token!"}
    response = client.get("/api/post/3/", headers={"token": "1234"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No such post!"}
    response = client.get("/api/post/1/", headers={"token": "1234"})
    assert response.status_code == 200
    assert response.json() == {"message": "Wrong token!"}
    response = client.get("/api/post/1/", headers={"token": TOKEN})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_updatePost():
    data = {"data": "Hello!"}
    response = client.put("/api/post/3/")
    assert response.status_code == 422
    response = client.put("/api/post/3/", json=data)
    assert response.status_code == 404
    assert response.json() == {"detail": "No such post!"}
    response = client.put("/api/post/1/", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "Wrong token!"}
    response = client.put("/api/post/1/", headers={"token": TOKEN}, json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "/api/post/1/"}
    response = client.get("/api/post/1/", headers={"token": TOKEN})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello!"}

def test_deletePost():
    response = client.delete("/api/post/3/")
    assert response.status_code == 200
    assert response.json() == {"message": "No token!"}
    response = client.delete("/api/post/3/", headers={"token": "1234"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No such post!"}
    response = client.delete("/api/post/1/", headers={"token": "1234"})
    assert response.status_code == 200
    assert response.json() == {"message": "Wrong token!"}
    response = client.delete("/api/post/1/", headers={"token": TOKEN})
    assert response.status_code == 200
    assert response.json() == {"message": "Delete post"}
    response = client.get("/api/post/1/", headers={"token": TOKEN})
    assert response.status_code == 404
    assert response.json() == {"detail": "No such post!"}

def test_postTags():
    response = client.post("/api/post/1/tags/")
    assert response.status_code == 422
    response = client.post("/api/post/1/tags/", json={"tags": ["Photo"]})
    assert response.status_code == 200
    assert response.json() == {"message": "No token!"}
    response = client.post("/api/post/1/tags/", headers={"token": "1234"}, json={"tags": ["Photo"]})
    assert response.status_code == 404
    assert response.json() == {"detail": "Wrong token or post doesn't exist!"}
    response = client.post("/api/post/2/tags/", headers={"token": TOKEN + "@"}, json={"tags": ["Photo"]})
    assert response.status_code == 404
    assert response.json() == {"detail": "Wrong token or post doesn't exist!"}
    response = client.post("/api/post/2/tags/", headers={"token": TOKEN}, json={"tags": ["Photo"]})
    assert response.status_code == 200
    assert response.json() == {"message": "/api/post/2/tags/"}
    response = client.get("/api/post/1/tags/")
    assert response.status_code == 200
    assert response.json() == {"message": "No token!"}
    response = client.get("/api/post/1/tags/", headers={"token": "1234"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Wrong token or post doesn't exist!"}
    response = client.get("/api/post/2/tags/", headers={"token": "1234"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Wrong token or post doesn't exist!"}
    response = client.get("/api/post/2/tags/", headers={"token": TOKEN})
    assert response.status_code == 200
    assert response.json() == {"tags": ["Photo"]}
    response = client.post("/api/post/2/tags/", headers={"token": TOKEN}, json={"tags": ["Note"]})
    assert response.status_code == 200
    assert response.json() == {"message": "/api/post/2/tags/"}
    response = client.get("/api/post/2/tags/", headers={"token": TOKEN})
    assert response.status_code == 200
    assert response.json() == {"tags": ["Note"]}

def test_Pfp():
    response = client.get("/api/user/pfp/")
    assert response.status_code == 200
    assert response.json() == {"message": "No token!"}
    response = client.get("/api/user/pfp/", headers={"token": "1234"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No pfp for this token!"}
    response = client.get("/api/user/pfp/", headers={"token": TOKEN})
    assert response.status_code == 404
    assert response.json() == {"detail": "No pfp for this token!"}
    response = client.delete("/api/user/pfp/")
    assert response.status_code == 200
    assert response.json() == {"message": "No token!"}
    response = client.delete("/api/user/pfp/", headers={"token": "1234"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Wrong token!"}
    response = client.delete("/api/user/pfp/", headers={"token": TOKEN})
    assert response.status_code == 200
    assert response.json() == {"message": "Delete pfp"}
    response = client.post("/api/user/pfp/", files={"file": ("picture.jpg", open("picture.jpg", "rb"), "image/jpeg")})
    assert response.status_code == 200
    assert response.json() == {"message": "No token!"}
    response = client.post("/api/user/pfp/", headers={"token": "1234"},
    files={"file": ("picture.jpg", open("picture.jpg", "rb"), "image/jpeg")})
    assert response.status_code == 404
    assert response.json() == {"detail": "Wrong token!"}
    response = client.post("/api/user/pfp/", headers={"token": TOKEN},
    files={"file": ("picture.jpg", open("picture.jpg", "rb"), "image/jpeg")})
    assert response.status_code == 200
    assert response.json() == {"message": "Set pfp"}
    response = client.get("/api/user/pfp/", headers={"token": TOKEN})
    assert response.status_code == 200
    response = client.delete("/api/user/pfp/", headers={"token": TOKEN})
    assert response.status_code == 200
    assert response.json() == {"message": "Delete pfp"}
    response = client.get("/api/user/pfp/", headers={"token": TOKEN})
    assert response.status_code == 404
    assert response.json() == {"detail": "No pfp for this token!"}