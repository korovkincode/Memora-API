import sys 
sys.path.append('..')

from api import app
from fastapi.testclient import TestClient


client = TestClient(app)

def test_register():
    data = {"username": "test", "password": "1234", "name": "Test", "surname": "Test", 
    "email": "test1234@gmail.com", "gender": "Male", "birthdate": "01.01.1970"}
    response = client.post("/api/signup/", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "Add new user"}
