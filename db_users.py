import sqlalchemy as db
import secrets

def setup(db_name: str) -> None:
    engine, conn, metadata = connect(db_name)

    users = db.Table(
        db_name.capitalize(), metadata,
        db.Column('User-ID', db.Integer(), primary_key=True),
        db.Column('Username', db.String(50), nullable=False),
        db.Column('Password', db.String(150), nullable=False),
        db.Column('Token', db.String(10), nullable=False)
    )
    metadata.create_all(engine)

def connect(db_name: str):
    engine = db.create_engine(f"sqlite:///{db_name}.sqlite")
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata

def addUser(db_name: str, user: dict) -> str:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    if conn.execute(table.select().where(table.columns.Username == user['username'])).fetchall():
        return {'message': 'User with this username already exists'}
    query = db.insert(table).values(Username=user['username'], Password=user['password'], Token=secrets.token_hex(5))
    conn.execute(query)
    return {'message': 'Add new user'}

def authUser(db_name: str, user: dict) -> str:
    engine, conn, metadata = connect(db_name)
    table = db.Table(db_name.capitalize(), metadata, autoload=True, autoload_with=engine)
    table_list = conn.execute(table.select().where(table.columns.Username == user['username'])).fetchall()
    if table_list:
        return {'message': table_list[0][3]}
    else:
        return {'message': 'No such user'}