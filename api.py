from fastapi import FastAPI, Body, Request
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

class Token(BaseModel):
    token: str

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

@app.get("/api/post/{post_id}/read/")
async def read(post_id: int, request: Request) -> dict:
    token = request.headers.get('token')
    return db_posts.readPost("Posts", post_id, token)

@app.put("/api/post/{post_id}/update/")
async def update(post_id: int, post_json: Post) -> dict:
    post = post_json.dict()
    return db_posts.updatePost("Posts", post, post_id)

@app.delete("/api/post/{post_id}/delete/")
async def delete(post_id: int, token_json: Token) -> dict:
    token = token_json.dict()["token"]
    return db_posts.deletePost("Posts", post_id, token)