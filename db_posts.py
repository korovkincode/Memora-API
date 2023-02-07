import sqlalchemy as db
import db_users, os
from typing import Union
from fastapi.responses import FileResponse
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.sql.schema import MetaData

POSTS_NAME = "Posts"

def setup() -> None:
    engine, conn, metadata = connect()

    posts = db.Table(
        POSTS_NAME, metadata,
        db.Column("PostID", db.Integer(), primary_key=True),
        db.Column("UserToken", db.String(10), nullable=False),
        db.Column("Data", db.String(), nullable=False),
        db.Column("IsFile", db.Boolean(), default=False, nullable=False),
        db.Column("Path", db.String(100))
    )
    metadata.create_all(engine)

def connect() -> tuple[Engine, Connection, MetaData]:
    engine = db.create_engine(f"sqlite:///db/{POSTS_NAME}.sqlite")
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata

def createPost(post: dict, file=None, isFile=False) -> dict:
    if not db_users.getUserByToken(post["token"]):
        return {"message": "No such user"}
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    if not isFile:
        query = db.insert(table).values(UserToken=post["token"], Data=post["data"], IsFile=False)
        conn.execute(query)
        tableL = conn.execute(table.select()).fetchall()
        cur_id = tableL[-1][0]
        return {"message": f"/api/post/{getNumberOfPosts()}/read/"}
    filename = createFile(file)
    query = db.insert(table).values(UserToken=post["token"], Data="File", IsFile=True, Path=f"static/{filename}")
    conn.execute(query)
    tableL = conn.execute(table.select()).fetchall()
    cur_id = tableL[0][0]
    return {"message": f"/api/post/{getNumberOfPosts()}/read/"}

def readPost(post_id: int, token: Union[str, None]) -> Union[FileResponse, dict]:
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    if not tableL:
        return {"message": "No such post"}
    if tableL[0][1] != token:
        return {"message": "Wrong token!"}
    if tableL[0][3]:
        return FileResponse(tableL[0][4])
    return {"message": tableL[0][2]}

def updatePost(post: dict, post_id: int, file=None, isFile=False) -> dict:
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    if not tableL:
        return {"message": "No such post"}
    if tableL[0][1] != post["token"]:
        return {"message": "Wrong token!"}
    delFile(post_id)
    if not isFile:
        query = table.update().values(Data=post["data"], IsFile=0, Path=None).where(table.columns.PostID == post_id)
        conn.execute(query)
        return {"message": f"/api/post/{post_id}/read/"}
    filename = createFile(file, post_id)
    query = table.update().values(Data="File", IsFile=1, Path=f"/static/{filename}").where(table.columns.PostID == post_id)
    conn.execute(query)
    return {"message": f"/api/post/{post_id}/read/"}

def deletePost(post_id: int, token: Union[str, None]) -> dict:
    engine, conn, metadata = connect()
    table = db.Table(POSTS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    if not tableL:
        return {"message": "No such post"}
    if tableL[0][1] != token:
        return {"message": "Wrong token!"}
    query = table.delete().where(table.columns.PostID == post_id)
    conn.execute(query)
    delFile(post_id)
    return {"message": "Deleted post"}

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

def delFile(name: int) -> Union[int, None]:
    for filename in os.listdir("static"):
        curName = filename[:filename.index(".")]
        if int(curName) == name:
            os.remove(f"static/{filename}")
            return 1

def createFile(file, post_id=None) -> str:
    if post_id is not None:
        name = post_id
    else:
        name = getNumberOfPosts() + 1
    filename = f"{name}.{file.filename[file.filename.index('.') + 1:]}"
    with open(f"static/{filename}", "wb") as f:
        f.write(file.file.read())
    return filename