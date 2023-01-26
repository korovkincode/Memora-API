import sqlalchemy as db
import db_users, os

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

def createPost(db_name: str, post: dict, isFile=False, filename=None) -> dict:
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
    query = db.insert(table).values(UserToken=post["token"], Data="File", IsFile=True, Path=f"/static/{filename}")
    conn.execute(query)
    table_list = conn.execute(table.select()).fetchall()
    cur_id = table_list[0][0]
    return {"message": f"/static/{filename}"}

def readPost(db_name: str, post_id: int, token: str) -> dict:
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

def updatePost(db_name: str, post: dict, post_id: int, isFile=False, filename=None) -> dict:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    if not table_list:
        return {"message": "No such post"}
    if not isFile:
        query = table.update().values(Data=post["data"], IsFile=0, Path=None).where(table.columns.PostID == post_id)
        conn.execute(query)
        return {"message": "Updated post"}
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
    for filename in os.listdir("static"):
        curName = filename[:filename.index(".")]
        if int(curName) == post_id:
            os.remove(f"static/{filename}")
            break
    return {"message": "Deleted post"}

def getNumberOfPosts(db_name: str) -> int:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    return len(conn.execute(table.select()).fetchall())