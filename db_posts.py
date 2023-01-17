import sqlalchemy as db
import db_users

def setup(db_name: str) -> None:
    engine, conn, metadata = connect(db_name)

    posts = db.Table(
        db_name.capitalize(), metadata,
        db.Column('PostID', db.Integer(), primary_key=True),
        db.Column('UserToken', db.String(10), nullable=False),
        db.Column('Data', db.String(), nullable=False),
        db.Column('IsFile', db.Boolean(), default=False, nullable=False),
        db.Column('Path', db.String(100))
    )
    metadata.create_all(engine)

def connect(db_name: str):
    engine = db.create_engine(f"sqlite:///db/{db_name}.sqlite")
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata

def createPost(db_name: str, post: dict):
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    if not db_users.getUserByToken("Users", post['token']):
        return {"message": "No such user"}
    if not post['is_file']:
        query = db.insert(table).values(UserToken=post['token'], Data=post['data'], IsFile=False)
        conn.execute(query)
        return {"message": "Add new post"}
    return {"message": "Cannot handle a file yet!"}

def readPost(db_name: str, post_id: int, token: str):
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.PostID == post_id).fetchall())
    if not table_list:
        return {"message": "No such post"}
    if table_list[0][1] != token:
        return {"message": "Wrong token!"}
    if table_list[0][3] == True:
        return {"message": "Cannot handle a file yet!"}
    return {"message": table_list[0][2]}