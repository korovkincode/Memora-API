import sqlalchemy as db
import secrets

USERS_NAME = "Users"
POSTS_NAME = "Posts"

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
        db.Column("Token", db.String(10), nullable=False)
    )
    metadata.create_all(engine)

def connect():
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

def auth(user: dict) -> dict:
    engine, conn, metadata = connect()
    table = db.Table(USERS_NAME, metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.Username == user["username"])).fetchall()
    if len(table_list) and table_list[0][2] == user["password"]:
        return {"message": table_list[0][-1]}
    return {"message": "No such user"}

def getUserByToken(token: str) -> int:
    engine, conn, metadata = connect()
    table = db.Table(USERS_NAME, metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.Token == token)).fetchall()
    if table_list:
        return 1
    return 0