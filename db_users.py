from fastapi import File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import sqlalchemy as db
import secrets, os
from typing import Union
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.sql.schema import MetaData

USERS_NAME = "Users"

def setup() -> None:
    engine, conn, metadata = connect()

    users = db.Table(
        USERS_NAME, metadata,
        db.Column("UserID", db.Integer(), primary_key=True),
        db.Column("Username", db.String(50), nullable=False),
        db.Column("Password", db.String(150), nullable=False),
        db.Column("Name", db.String(50), nullable=False),
        db.Column("Surname", db.String(50), nullable=False),
        db.Column("Email", db.String(60), nullable=False),
        db.Column("Gender", db.String(20), nullable=False),
        db.Column("BirthDate", db.String(20), nullable=False),
        db.Column("Token", db.String(10), nullable=False),
        db.Column("PicturePath", db.String(30))
    )
    metadata.create_all(engine)

def connect() -> tuple[Engine, Connection, MetaData]:
    engine = db.create_engine(f"sqlite:///db/{USERS_NAME}.sqlite")
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata

def add(user: dict) -> dict:
    engine, conn, metadata = connect()
    table = db.Table(USERS_NAME, metadata, autoload=True, autoload_with=engine)
    if conn.execute(table.select().where(table.columns.Username == user["username"])).fetchall():
        return {"message": "User with this username already exists"}
    query = db.insert(table).values(Username=user["username"], Password=user["password"], Name=user["name"],
    Surname=user["surname"], Email=user["email"], Gender=user["gender"],
    BirthDate=user["birthdate"], Token=secrets.token_hex(5))
    conn.execute(query)
    return {"message": "Add new user"}

def auth(user: dict) -> Union[HTTPException, dict]:
    engine, conn, metadata = connect()
    table = db.Table(USERS_NAME, metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.Username == user["username"])).fetchall()
    if len(table_list) and table_list[0][2] == user["password"]:
        return {"message": table_list[0][-2]}
    raise HTTPException(status_code=404, detail="No such user")

def viewPfp(token: Union[str, None]) -> Union[HTTPException, FileResponse, dict]:
    if token is None:
        return {"message": "No token!"}
    for filename in os.listdir("pfp"):
        curName = filename[:filename.index(".")]
        if curName == token:
            return FileResponse(f"pfp/{filename}")
    raise HTTPException(status_code=404, detail="No pfp for this token!")

def setPfp(token: Union[str, None], file: UploadFile = File(...)) -> dict:
    if token is None:
        return {"message": "No token!"}
    engine, conn, metadata = connect()
    table = db.Table(USERS_NAME, metadata, autoload=True, autoload_with=engine)
    filename = createFilePfp(token, file)
    query = table.update().values(PicturePath=f"/pfp/{filename}").where(table.columns.Token == token)
    conn.execute(query)
    return {"message": "Set pfp"}

def deletePfp(token: Union[str, None]) -> dict:
    if token is None:
        return {"message": "No token!"}
    engine, conn, metadata = connect()
    table = db.Table(USERS_NAME, metadata, autoload=True, autoload_with=engine)
    query = table.update().values(PicturePath=None).where(table.columns.Token == token)
    conn.execute(query)
    delFilePfp(token)
    return {"message": "Delete pfp"}

def getUserByToken(token: str) -> int:
    engine, conn, metadata = connect()
    table = db.Table(USERS_NAME, metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.Token == token)).fetchall()
    if table_list:
        return 1
    return 0

def delFilePfp(name: str) -> Union[int, None]:
    for filename in os.listdir("pfp"):
        curName = filename[:filename.index(".")]
        if curName == name:
            os.remove(f"pfp/{filename}")
            return 1

def createFilePfp(token: str, file: UploadFile = File(...)) -> str:
    filename = f"{token}.{file.filename[file.filename.index('.') + 1:]}"
    with open(f"pfp/{filename}", "wb") as f:
        f.write(file.file.read())
    return filename