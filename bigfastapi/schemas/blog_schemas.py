
import datetime as _dt

import pydantic as _pydantic
from typing import Optional

class Blog(_pydantic.BaseModel):
    id: Optional[str]
    creator: Optional[str]
    title: str
    content: str
    date_created: Optional[_dt.datetime]
    last_updated: Optional[_dt.datetime]

    class Config:
        orm_mode = True
