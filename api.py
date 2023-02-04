from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import db_users, db_posts, db_tags
from typing import Union

#TOKEN -> 7c927a25f9

db_users.setup()
db_posts.setup()
db_tags.setup()

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
    data: str


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
async def create(request: Request, post_json: Post) -> dict:
    post = post_json.dict()
    token = request.headers.get("token")
    post["token"] = token
    return db_posts.createPost(post)

@app.post("/api/post/create/file/")
async def createFile(request: Request, file: UploadFile = File(...)) -> dict:
    token = request.headers.get('token')
    return db_posts.createPost({"token": token}, file, isFile=True)

@app.get("/api/post/{post_id}/read/")
async def read(request: Request, post_id: int) -> Union[FileResponse, dict]:
    token = request.headers.get("token")
    return db_posts.readPost(post_id, token)

@app.put("/api/post/{post_id}/update/")
async def update(request: Request, post_id: int, post_json: Post) -> dict:
    post = post_json.dict()
    token = request.headers.get('token')
    post["token"] = token
    return db_posts.updatePost(post, post_id)

@app.put("/api/post/{post_id}/update/file/")
async def updateFile(request: Request, post_id: int, file: UploadFile = File(...)) -> dict:
    token = request.headers.get("token")
    return db_posts.updatePost({"token": token}, post_id, file, isFile=True)

@app.delete("/api/post/{post_id}/delete/")
async def delete(request: Request, post_id: int) -> dict:
    token = request.headers.get("token")
    return db_posts.deletePost(post_id, token)