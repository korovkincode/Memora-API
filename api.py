from fastapi import FastAPI, Request
from pydantic import BaseModel
import db_users

db_users.setup('Users')

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

@app.get("/")
async def root() -> dict:
    return {"message": "Hello, World!"}

@app.post("/register")
async def register(user_json: User) -> dict:
    user = user_json.dict()
    return db_users.addUser('Users', user)

@app.post("/login")
async def login(user_json: User) -> dict:
    user = user_json.dict()
    return db_users.authUser('Users', user)