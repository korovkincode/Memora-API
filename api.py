from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import db_users, db_posts

#TOKEN -> b5eed51d8b

db_users.setup('Users')
db_posts.setup('Posts')

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

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
    return db_users.add("Users", user)

@app.post("/api/login")
async def login(user_json: User) -> dict:
    user = user_json.dict()
    return db_users.auth("Users", user)

@app.post("/api/post/create")
async def create(post_json: Post) -> dict:
    post = post_json.dict()
    return db_posts.createPost("Posts", post)