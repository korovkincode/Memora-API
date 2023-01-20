import sqlalchemy as db
import secrets

def setup(db_name: str) -> None:
    engine, conn, metadata = connect(db_name)

    users = db.Table(
        db_name.capitalize(), metadata,
        db.Column("UserID", db.Integer(), primary_key=True),
        db.Column("Username", db.String(50), nullable=False),
        db.Column("Password", db.String(150), nullable=False),
        db.Column("Token", db.String(10), nullable=False)
    )
    metadata.create_all(engine)

def connect(db_name: str):
    engine = db.create_engine(f"sqlite:///db/{db_name}.sqlite")
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata

def add(db_name: str, user: dict) -> dict:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    if conn.execute(table.select().where(table.columns.Username == user["username"])).fetchall():
        return {"message": "User with this username already exists"}
    query = db.insert(table).values(Username=user["username"], Password=user["password"], Token=secrets.token_hex(5))
    conn.execute(query)
    return {"message": "Add new user"}

def auth(db_name: str, user: dict) -> dict:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.Username == user["username"])).fetchall()
    if table_list[0][2] == user["password"]:
        return {"message": table_list[0][3]}
    return {"message": "No such user"}

def getUserByToken(db_name: str, token: str) -> bool:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.Token == token)).fetchall()
    if table_list:
        return 1
    return 0