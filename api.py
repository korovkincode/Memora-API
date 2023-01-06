from fastapi import FastAPI, Request
from pydantic import BaseModel

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
    
    return {"message": "Got data"}