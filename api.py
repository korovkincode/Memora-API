from fastapi import FastAPI, Request
from pydantic import BaseModel
import db_users, db_posts

db_users.setup('Users')
db_posts.setup('Posts')

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

class Post(BaseModel):
    token: str
    data: str
    is_file: bool

@app.get("/api/")
async def root() -> dict:
    return {"message": "Hello, World!"}

@app.post("/api/signup")
async def signup(user_json: User) -> dict:
    user = user_json.dict()
    return db_users.addUser("Users", user)

@app.post("/api/login")
async def login(user_json: User) -> dict:
    user = user_json.dict()
    return db_users.authUser("Users", user)

@app.post("/api/add")
async def add(post_json: Post) -> dict:
    post = post_json.dict()
    return {"message": "Hello, World!"}