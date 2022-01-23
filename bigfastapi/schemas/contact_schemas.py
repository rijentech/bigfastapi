import datetime as dt
import pydantic
from typing import Optional, List


class _contactBase(pydantic.BaseModel):
    address: str
    phone: str
    map_coordinates: str


class Contact(_contactBase):
    id: str
    date_created: dt.datetime
    last_updated: dt.datetime

    class Config:
        orm_mode = True


class ContactCreate(_contactBase):
    pass


class ContactUpdate(_contactBase):
    pass


class _contactUSbase(pydantic.BaseModel):
    name: str
    email: str
    subject: Optional[str] = None
    message: str


class ContactUS(_contactUSbase):
    id: str
    date_created: dt.datetime

    class Config:
        orm_mode = True


class ContactUSCreate(_contactUSbase):
    pass
