import datetime as dt
import pydantic


class SecureBase(pydantic.BaseModel):
    email: str


class ContactSecureCreate(SecureBase):
    code: str

    class Config:
        orm_mode = True


class CodeUpdate(pydantic.BaseModel):
    code: str


class ContactSecureLogin(SecureBase):
    code: str


class ContactSecure(SecureBase):
    id: str
    date_created: dt.datetime

    class Config:
        orm_mode = True
