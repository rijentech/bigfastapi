
import datetime as dt

import pydantic as pydantic
from typing import Optional, List

class BlogPost(pydantic.BaseModel):
    id: Optional[str]
    creator: Optional[str]
    title: str
    content: str
    blog_id: Optional[str]
    tags: Optional[List[str]] = []
    date_created: Optional[dt.datetime]
    last_updated: Optional[dt.datetime]

    class Config:
        orm_mode = True

class Blog(pydantic.BaseModel):
    id: Optional[str]
    creator: Optional[str]
    title: str
    blogposts: Optional[List[BlogPost]] = []
    date_created: Optional[dt.datetime]
    last_updated: Optional[dt.datetime]
    class Config:
        orm_mode = True
        