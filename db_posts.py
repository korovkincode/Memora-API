import sqlalchemy as db

def setup(db_name: str) -> None:
    engine, conn, metadata = connect(db_name)

    posts = db.Table(
        db_name.capitalize(), metadata,
        db.Column('Post-ID', db.Integer(), primary_key=True),
        db.Column('User Token', db.String(10), nullable=False),
        db.Column('Data', db.String(), nullable=False),
        db.Column('Is-file', db.Boolean(), default=False, nullable=False),
        db.Column('Path', db.String(100))
    )
    metadata.create_all(engine)

def connect(db_name: str):
    engine = db.create_engine(f"sqlite:///{db_name}.sqlite")
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata