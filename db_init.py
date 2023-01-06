import sqlalchemy as db

def setup_users(db_name):
    engine = db.create_engine(f"sqlite:///{db_name}.sqlite")
    conn = engine.connect()
    metadata = db.MetaData()

    users = db.Table(
        db_name.capitalize(), metadata,
        db.Column('User-ID', db.Integer(), primary_key=True),
        db.Column('Username', db.String(50), nullable = False),
        db.Column('Password', db.String(150), nullable = False)
    )
    metadata.create_all(engine)
