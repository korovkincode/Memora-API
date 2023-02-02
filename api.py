from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import db_users, db_posts
from typing import Union

#TOKEN -> 7c927a25f9

USERS_NAME = "Users"
POSTS_NAME = "POSTS"

db_users.setup()
db_posts.setup()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class UserRegister(BaseModel):
    username: str
    password: str
    name: str
    surname: str
    email: str
    gender: str
    birthdate: str

class UserAuth(BaseModel):
    username: str
    password: str

class Post(BaseModel):
    token: str
    data: str

class Token(BaseModel):
    token: str

@app.get("/api/")
async def root() -> dict:
    return {"message": "API for Memora with Python + FastAPI -> https://github.com/korovkincode/Memora-API"}

@app.post("/api/signup/")
async def signup(user_json: UserRegister) -> dict:
    user = user_json.dict()
    return db_users.add(user)

@app.post("/api/login/")
async def login(user_json: UserAuth) -> dict:
    user = user_json.dict()
    return db_users.auth(user)

@app.post("/api/post/create/")
async def create(post_json: Post) -> dict:
    post = post_json.dict()
    return db_posts.createPost(post)

@app.post("/api/post/create/file/")
async def createFile(token: str = Form(...), file: UploadFile = File(...)) -> dict:
    #token = request.headers.get('token')
    return db_posts.createPost({"token": token}, file, isFile=True)

@app.get("/api/post/{post_id}/read/")
async def read(post_id: int, request: Request) -> Union[FileResponse, dict]:
    token = request.headers.get("token")
    return db_posts.readPost(post_id, token)

@app.put("/api/post/{post_id}/update/")
async def update(post_id: int, post_json: Post) -> dict:
    post = post_json.dict()
    return db_posts.updatePost(post, post_id)

@app.put("/api/post/{post_id}/update/file/")
async def updateFile(post_id: int, token: str = Form(...), file: UploadFile = File(...)) -> dict:
    return db_posts.updatePost({"token": token}, post_id, file, isFile=True)

@app.delete("/api/post/{post_id}/delete/")
async def delete(post_id: int, token_json: Token) -> dict:
    token = token_json.dict()["token"]
    return db_posts.deletePost(post_id, token)