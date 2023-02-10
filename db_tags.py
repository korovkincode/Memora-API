import sqlalchemy as db
from fastapi import HTTPException
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.sql.schema import MetaData
from typing import Union
import db_users, db_posts


TAGS_NAME = "Tags"
LINK_NAME = "Link"

def setupTags() -> None:

    engine, conn, metadata = connect(TAGS_NAME)

    tags = db.Table(
        TAGS_NAME, metadata,
        db.Column("TagID", db.Integer(), primary_key=True),
        db.Column("Name", db.String(200), nullable=False)
    )
    metadata.create_all(engine)

def setupLink() -> None:

    engine, conn, metadata = connect(LINK_NAME)

    link = db.Table(
        LINK_NAME, metadata,
        db.Column("PostID", db.Integer(), nullable=False),
        db.Column("TagID", db.Integer(), nullable=False)
    )
    metadata.create_all(engine)

def connect(NAME: str) -> tuple[Engine, Connection, MetaData]:
    engine = db.create_engine(f"sqlite:///db/{NAME}.sqlite")
    conn = engine.connect()
    metadata = db.MetaData()
    return engine, conn, metadata

def updatePostTags(post_id: int, token: Union[str, None], tags: dict) -> Union[HTTPException, dict]:
    if token is None:
        return {"message": "No token!"}
    engine, conn, metadata = connect(TAGS_NAME)
    if token != db_posts.getTokenByPost(post_id):
        raise HTTPException(status_code=404, detail="Wrong token or post doesn't exist!")
    clearLinks(post_id)
    table = db.Table(TAGS_NAME, metadata, autoload=True, autoload_with=engine)
    for tag in tags["tags"]:
        if getTagID(tag) is None:
            query = db.insert(table).values(Name=tag)
            conn.execute(query)
        addLink(post_id, getTagID(tag))
    return {"message": "Updated tags"}

def readPostTags(post_id: int, token: Union[str, None]) -> Union[HTTPException, dict]:
    if token is None:
        return {"message": "No token!"}
    engine, conn, metadata = connect(LINK_NAME)
    if token != db_posts.getTokenByPost(post_id):
        raise HTTPException(status_code=404, detail="Wrong token or post doesn't exist!")
    table = db.Table(LINK_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.PostID == post_id)).fetchall()
    tags = []
    for postid, tag_id in tableL:
        tags.append(getTagName(tag_id))
    return {"tags": tags}

def getTagID(tag_name: str) -> Union[int, None]:
    engine, conn, metadata = connect(TAGS_NAME)
    table = db.Table(TAGS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.Name == tag_name)).fetchall()
    if len(tableL):
        return tableL[0][0]

def getTagName(tag_id: int) -> Union[str, None]:
    engine, conn, metadata = connect(TAGS_NAME)
    table = db.Table(TAGS_NAME, metadata, autoload=True, autoload_with=engine)
    tableL = conn.execute(table.select().where(table.columns.TagID == tag_id)).fetchall()
    if len(tableL):
        return tableL[0][1]

def addLink(post_id: int, tag_id: Union[int, None]) -> None:
    if tag_id is not None:
        engine, conn, metadata = connect(LINK_NAME)
        table = db.Table(LINK_NAME, metadata, autoload=True, autoload_with=engine)
        query = db.insert(table).values(PostID=post_id, TagID=tag_id)
        conn.execute(query)
    
def clearLinks(post_id: int) -> None:
    engine, conn, metadata = connect(LINK_NAME)
    table = db.Table(LINK_NAME, metadata, autoload=True, autoload_with=engine)
    query = table.delete().where(table.columns.PostID == post_id)
    conn.execute(query)