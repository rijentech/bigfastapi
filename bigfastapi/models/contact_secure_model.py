import passlib.hash as _hash
import datetime as dt
from sqlalchemy.schema import Column
from sqlalchemy.types import String, DateTime
from uuid import uuid4
import bigfastapi.db.database as database


class ContactSecure(database.Base):
    __tablename__ = "contact secure"
    id = Column(String(255), primary_key=True, index=True, default=uuid4().hex)
    email = Column(String(255), index=True)
    code = Column(String(255), nullable=False)
    date_created = Column(DateTime, default=dt.datetime.utcnow)

    def verify_code(self, code: str):
        return (code, self.code)
