import sqlalchemy as db
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.sql.schema import MetaData
from typing import Union
import db_users, db_posts


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

def createPostTags(post_id: int, token: Union[str, None], tags: dict) -> dict:
    engine, conn, metadata = connect()
    if token != db_posts.getTokenByPost(post_id):
        return {"message": "Wrong token or post doesn't exist!"}
    table = db.Table(TAGS_NAME, metadata, autoload=True, autoload_with=engine)
    for tag in tags["tags"]:
        if getTagID(tag) is None:
            query = db.insert(table).values(Name=tag)
            conn.execute(query)
    return {"message": "Added tags"}


def getTagID(tag_name: str) -> Union[int, None]:
    engine, conn, metadata = connect()
    table = db.Table(TAGS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.Name == tag_name)).fetchall()
    if len(tableL):
        return tableL[0][0]