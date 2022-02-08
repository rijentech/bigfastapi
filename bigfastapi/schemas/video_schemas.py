import datetime as dt
from typing import Optional
from pydantic import BaseModel, HttpUrl


class videoSearch(BaseModel):
    url: HttpUrl


class videoBase(BaseModel):
    id: str
    title: str
    url: str
    thumbnail: str
    duration: str
    added_by: str
    time_added: dt.datetime

    class Config:
        orm_mode = True
        validate_all = True
        validate_assignment = True


class videos(videoBase):
    likes = int

    class Config:
        orm_mode = True
        validate_all = True
        validate_assignment = True
