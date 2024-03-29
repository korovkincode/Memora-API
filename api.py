from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import db_users, db_posts, db_tags
from typing import Union

#TOKEN -> 408c2f5554

db_users.setup()
db_posts.setupPosts()
db_posts.setupLink()
db_tags.setupTags()
db_tags.setupLink()

app = FastAPI()

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

class Tags(BaseModel):
    tags: list[str]

class Filename(BaseModel):
    filename: str

@app.get("/api/")
async def root() -> dict:
    return {"message": "API for Memora with Python + FastAPI -> https://github.com/korovkincode/Memora-API"}

@app.post("/api/signup/")
async def signup(user_json: UserRegister) -> dict:
    user = user_json.dict()
    return db_users.add(user)

@app.post("/api/login/")
async def login(user_json: UserAuth) -> Union[HTTPException, dict]:
    user = user_json.dict()
    return db_users.auth(user)

@app.get("/api/user/pfp/")
async def viewPfp(request: Request) -> Union[HTTPException, FileResponse, dict]:
    token = request.headers.get("token")
    return db_users.viewPfp(token)

@app.post("/api/user/pfp/")
async def setPfp(request: Request, file: UploadFile = File(...)) -> dict:
    token = request.headers.get("token")
    return db_users.setPfp(token, file)

@app.delete("/api/user/pfp/")
async def deletePfp(request: Request) -> dict:
    token = request.headers.get("token")
    return db_users.deletePfp(token)

@app.get("/api/user/tags/")
async def getUserTags(request: Request) -> dict:
    token = request.headers.get("token")
    return db_tags.getUserTags(token)

@app.post("/api/post/")
async def createPost(request: Request, post_json: Post) -> Union[HTTPException, dict]:
    token = request.headers.get("token")
    post = post_json.dict()
    post["token"] = token
    return db_posts.createPost(post)

@app.get("/api/post/{post_id}/")
async def readPost(request: Request, post_id: int) -> Union[HTTPException, dict]:
    token = request.headers.get("token")
    return db_posts.readPost(post_id, token)

@app.put("/api/post/{post_id}/")
async def updatePost(request: Request, post_id: int, post_json: Post) -> Union[HTTPException, dict]:
    token = request.headers.get("token")
    post = post_json.dict()
    post["token"] = token
    return db_posts.updatePost(post, post_id)

@app.put("/api/post/{post_id}/file/")
async def updatePostFile(request: Request, post_id: int, file: UploadFile = File(...)) -> Union[HTTPException, dict]:
    token = request.headers.get("token")
    return db_posts.updatePost({"token": token}, post_id, file, isFile=1)

@app.delete("/api/post/{post_id}/")
async def deletePost(request: Request, post_id: int) -> Union[HTTPException, dict]:
    token = request.headers.get("token")
    return db_posts.deletePost(post_id, token)

@app.delete("/api/post/{post_id}/file/")
async def deletePostFile(request: Request, post_id: int, filename_json: Filename) -> Union[HTTPException, dict]:
    token = request.headers.get("token")
    return db_posts.deletePost(post_id, token, filename=filename_json.dict()["filename"])

@app.post("/api/post/{post_id}/tags/")
async def updatePostTags(request: Request, tags_json: Tags, post_id: int) -> Union[HTTPException, dict]:
    token = request.headers.get("token")
    tags = tags_json.dict()
    return db_tags.updatePostTags(post_id, token, tags)

@app.get("/api/post/{post_id}/tags/")
async def readPostTags(request: Request, post_id: int) -> Union[HTTPException, dict]:
    token = request.headers.get("token")
    return db_tags.readPostTags(post_id, token)

@app.get("/api/static/{filename}")
async def getStaticFile(request: Request, filename: str) -> Union[HTTPException, FileResponse, dict]:
    token = request.headers.get("token")
    return db_posts.getStaticFile(token, filename)