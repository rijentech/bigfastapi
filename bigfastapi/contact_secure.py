from uuid import uuid4
import fastapi as fastapi
import passlib.hash as _hash
from bigfastapi.models import contact_secure_model as model
from .utils import utils
from fastapi import APIRouter, HTTPException, status
import sqlalchemy.orm as orm
from bigfastapi.db.database import get_db
from .schemas import contact_secure_schemas as schemas

app = APIRouter(tags=["contact us security"])


@app.post("/contact/secure", status_code=201)
def create_pin(secure: schemas.ContactSecureCreate, db: orm.Session = fastapi.Depends(get_db)):
    c_secure = db.query(model.ContactSecure).filter(model.ContactSecure.email == secure.email).first()
    print(c_secure)
    if c_secure is not None:
        raise fastapi.HTTPException(status_code=403, detail="Email already exist")

    cont = model.ContactSecure(id=uuid4().hex,
                               email=secure.email,
                               code=secure.code)
    db.add(cont)
    db.commit()
    db.refresh(cont)
    return {"message": f"pin created for {cont.email}"}


@app.post("/contact/secure/login", status_code=200)
async def login(secure: schemas.ContactSecureLogin, db: orm.Session = fastapi.Depends(get_db)):
    secure_info = db.query(model.ContactSecure).filter(model.ContactSecure.email == secure.email).first()
    if secure_info.code == secure.code:
        return {"message": "Welcome back"}
    raise fastapi.HTTPException(status_code=403, detail="pin Incorrect")


@app.put("/contact/secure/{email}")
def ForgotSecurePin(secure: schemas.CodeUpdate, email: str, db: orm.Session = fastapi.Depends(get_db)):
    secure_code = db.query(model.ContactSecure).filter(model.ContactSecure.email == email).first()
    if secure_code:
        secure_code.code = secure.code
        db.commit()
        db.refresh(secure_code)
        return {"message": "Code changed, kindly log in"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not registered")
