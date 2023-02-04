import sqlalchemy as db
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.sql.schema import MetaData

TAGS_NAME = "Tags"

def setup() -> None:

    engine, conn, metadata = connect()

    tags = db.Table(
        TAGS_NAME, metadata,
        db.Column("TagID", db.Integer(), primary_key=True),
        db.Column("Name", db.String(200), nullable=False)
    )
    metadata.create_all(engine)

def connect() -> tuple[Engine, Connection, MetaData]:
    engine = db.create_engine(f"sqlite:///db/{TAGS_NAME}.sqlite")
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata