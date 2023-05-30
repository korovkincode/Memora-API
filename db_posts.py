import sqlalchemy as db
import db_users, os, time, hmac, hashlib
from typing import Union
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.sql.schema import MetaData

POSTS_NAME = "Posts"
LINK_NAME = "Posts-Link"

def setupPosts() -> None:
    engine, conn, metadata = connect()

    posts = db.Table(
        POSTS_NAME, metadata,
        db.Column("PostID", db.Integer(), primary_key=True),
        db.Column("UserToken", db.String(10), nullable=False),
        db.Column("Data", db.String(), nullable=False),
    )
    metadata.create_all(engine)

def setupLink() -> None:
    print("here")
    engine, conn, metadata = connect(flag=1)

    link = db.Table(
        LINK_NAME, metadata,
        db.Column("PostID", db.Integer()),
        db.Column("Filename", db.String(100))
    )
    metadata.create_all(engine)

def connect(flag=0) -> tuple[Engine, Connection, MetaData]:
    engine = db.create_engine(f"sqlite:///db/{LINK_NAME if flag else POSTS_NAME}.sqlite?check_same_thread=False")
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata

def createPost(post: dict) -> Union[HTTPException, dict]:
    if not db_users.getUserByToken(post["token"]):
        raise HTTPException(status_code=404, detail="No such user!")
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    query = db.insert(table).values(UserToken=post["token"], Data=post["data"])
    conn.execute(query)
    tableL = conn.execute(table.select()).fetchall()
    curID = tableL[-1][0]
    return {"message": f"/api/post/{curID}/"}

def readPost(post_id: int, token: Union[str, None]) -> Union[HTTPException, FileResponse, dict]:
    if token is None:
        return {"message": "No token!"}
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    if not tableL:
        raise HTTPException(status_code=404, detail="No such post!")
    if tableL[0][1] != token:
        return {"message": "Wrong token!"}
    return {"data": tableL[0][2], "filenames": getFilesByID(post_id)}

def updatePost(post: dict, post_id: int, file=None, isFile=False) -> Union[HTTPException, dict]:
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    if not tableL:
        raise HTTPException(status_code=404, detail="No such post!")
    if tableL[0][1] != post["token"]:
        return {"message": "Wrong token!"}
    if not isFile:
        query = table.update().values(Data=post["data"]).where(table.columns.PostID == post_id)
        conn.execute(query)
        return {"message": f"/api/post/{post_id}/"}
    filename = createFile(file, post_id)
    engine, conn, metadata = connect(flag=1)
    table = db.Table(LINK_NAME, metadata, autoload=True, autoload_with=engine)
    query = db.insert(table).values(PostID=post_id, Filename=f"/static/{filename}")
    conn.execute(query)
    return {"message": f"/api/post/{post_id}/"}

def deletePost(post_id: int, token: Union[str, None]) -> Union[HTTPException, dict]:
    if token is None:
        return {"message": "No token!"}
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    if not tableL:
        raise HTTPException(status_code=404, detail="No such post!")
    if tableL[0][1] != token:
        return {"message": "Wrong token!"}
    query = table.delete().where(table.columns.PostID == post_id)
    conn.execute(query)
    delFile(post_id)
    return {"message": "Delete post"}

def getNumberOfPosts() -> int:
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    return len(conn.execute(table.select()).fetchall())

def getTokenByPost(post_id: int) -> Union[str, None]:
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    if len(tableL):
        return tableL[0][1]

def getPostsIDByToken(token: str) -> list[int]:
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.UserToken == token)).fetchall()
    return [post[0] for post in tableL]

def getFilesByID(post_id: int) -> list[str]:
    engine, conn, metadata = connect(flag=1)
    table = db.Table(LINK_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    return [file[1] for file in tableL] 

def delFile(name: int) -> Union[int, None]:
    for filename in os.listdir("static"):
        curName = filename[:filename.index(".")]
        if int(curName) == name:
            os.remove(f"static/{filename}")
            return 1

def createFile(file, post_id) -> str:
    timestamp = str(int(time.time() * 1000))
    name = hmac.new(str(post_id).encode('utf-8'), timestamp.encode('utf-8'), hashlib.sha256).hexdigest()
    filename = f"{name}.{file.filename[file.filename.index('.') + 1:]}"
    with open(f"static/{filename}", "wb") as f:
        f.write(file.file.read())
    return filename