import sqlalchemy as db
import db_users, os
from typing import Union

def setup(db_name: str) -> None:
    engine, conn, metadata = connect(db_name)

    posts = db.Table(
        db_name.capitalize(), metadata,
        db.Column("PostID", db.Integer(), primary_key=True),
        db.Column("UserToken", db.String(10), nullable=False),
        db.Column("Data", db.String(), nullable=False),
        db.Column("IsFile", db.Boolean(), default=False, nullable=False),
        db.Column("Path", db.String(100))
    )
    metadata.create_all(engine)

def connect(db_name: str):
    engine = db.create_engine(f"sqlite:///db/{db_name}.sqlite")
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata

def createPost(db_name: str, post: dict, file=None, isFile=False) -> dict:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    if not db_users.getUserByToken("Users", post["token"]):
        return {"message": "No such user"}
    if not isFile:
        query = db.insert(table).values(UserToken=post["token"], Data=post["data"], IsFile=False)
        conn.execute(query)
        table_list = conn.execute(table.select()).fetchall()
        cur_id = table_list[0][0]
        return {"message": f"/api/post/{cur_id}/read/"}
    filename = createFile(file)
    query = db.insert(table).values(UserToken=post["token"], Data="File", IsFile=True, Path=f"/static/{filename}")
    conn.execute(query)
    table_list = conn.execute(table.select()).fetchall()
    cur_id = table_list[0][0]
    return {"message": f"/static/{filename}"}

def readPost(db_name: str, post_id: int, token: Union[str,None]) -> dict:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    #print(table_list, post_id, type(post_id))
    if not table_list:
        return {"message": "No such post"}
    if table_list[0][1] != token:
        return {"message": "Wrong token!"}
    if table_list[0][3]:
        return {"message": table_list[0][4]}
    return {"message": table_list[0][2]}

def updatePost(db_name: str, post: dict, post_id: int, file=None, isFile=False) -> dict:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    if not table_list:
        return {"message": "No such post"}
    delFile(post_id)
    if not isFile:
        query = table.update().values(Data=post["data"], IsFile=0, Path=None).where(table.columns.PostID == post_id)
        conn.execute(query)
        return {"message": "Updated post"}
    filename = createFile(file, post_id)
    query = table.update().values(Data="File", IsFile=1, Path=f"/static/{filename}").where(table.columns.PostID == post_id)
    conn.execute(query)
    return {"message": "Updated post"}

def deletePost(db_name: str, post_id: int, token: str) -> dict:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    if not table_list:
        return {"message": "No such post"}
    if table_list[0][1] != token:
        return {"message": "Wrong token!"}
    query = table.delete().where(table.columns.PostID == post_id)
    conn.execute(query)
    delFile(post_id)
    return {"message": "Deleted post"}

def getNumberOfPosts(db_name: str) -> int:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    return len(conn.execute(table.select()).fetchall())

def delFile(name: int) -> Union[int,None]:
    for filename in os.listdir("static"):
        curName = filename[:filename.index(".")]
        if int(curName) == name:
            os.remove(f"static/{filename}")
            return 1

def createFile(file, post_id=None) -> str:
    if post_id is not None:
        name = post_id
    else:
        name = getNumberOfPosts("Posts") + 1
    filename = f"{name}.{file.filename[file.filename.index('.') + 1:]}"
    with open(f"static/{filename}", "wb") as f:
        f.write(file.file.read())
    return filename