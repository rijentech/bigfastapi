import sqlalchemy.orm as orm
from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, DateTime
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from uuid import uuid4
from bigfastapi.db import database
import bigfastapi.schemas.users_schemas as schema


class videos(database.Base):
    __tablename__ = "videos"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    title = Column(String(255), index=True)
    url = Column(String(255), index=True)
    thumbnail = Column(String(255), index=True)
    duration = Column(String(255), index=True)
    added_by = Column(String(255), ForeignKey("users.id"))
    likes = Column(Integer, default=0, nullable=False)
    time_added = Column(DateTime(timezone=True), server_default=func.now())

    @hybrid_method
    def like(self):
        self.likes += 1
        return self.likes

    @hybrid_method
    def unlike(self):
        self.likes -= 1
        return self.likes


def video_picker(user: schema.User,
                 id: str, db: orm.Session):
    video = db.query(videos).filter_by(added_by=user.id).filter(videos.id == id).first()
    return video
