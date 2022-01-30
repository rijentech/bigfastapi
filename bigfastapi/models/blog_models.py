import datetime as datetime
import sqlalchemy.orm as orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime, PickleType
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import ForeignKey
from uuid import uuid4
import bigfastapi.db.database as database
import bigfastapi.schemas.users_schemas as schema

class BlogPost(database.Base):
    __tablename__ = "blogs"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    creator = Column(String(255), ForeignKey("users.id"))
    title = Column(String(50), index=True)
    content = Column(String(255), index=True)
    tags = Column(MutableList.as_mutable(PickleType), default=[])
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)


def blogpost_selector(id: str, db: orm.Session):
    blog = db.query(BlogPost).filter(BlogPost.id == id).first()
    return blog

def get_blog_by_title(title: str, db: orm.Session):
    return db.query(BlogPost).filter(BlogPost.title == title).first()