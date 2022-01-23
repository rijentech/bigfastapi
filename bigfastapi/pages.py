import fastapi
from uuid import uuid4
from typing import List
import sqlalchemy.orm as orm
from datetime import datetime
from fastapi import APIRouter
from bigfastapi.db.database import get_db
from .models import pages_models as model
from .schemas import pages_schemas as schema
from starlette.responses import JSONResponse

app = APIRouter()


@app.get("/pages", response_model=List[schema.Page])
def get_all_pages(db: orm.Session = fastapi.Depends(get_db)):
    pages = db.query(model.Page).all()
    return list(map(schema.Page.from_orm, pages))


@app.post("/page", response_model=schema.Page)
def create_page(page: schema.PageInput, db: orm.Session = fastapi.Depends(get_db)):
    page = model.Page(id=uuid4().hex, title=page.title, content=page.content)
    db.add(page)
    db.commit()
    db.refresh(page)
    return schema.Page.from_orm(page)


@app.put("/page/{page_id}")
def update_page(request: schema.PageInput, page_id: str, db: orm.Session = fastapi.Depends(get_db)):
    page = get_page_by("id", page_id, db)

    if page:
        if request.title != "":
            page.title = request.title
        if request.content != "":
            page.content = request.content
        page.last_updated = datetime.utcnow()

        db.commit()
        db.refresh(page)
        return page

    return fastapi.HTTPException(status_code=404)


@app.get("/page/{page_id}", response_model=schema.Page)
def get_page(page_id: str, db: orm.Session = fastapi.Depends(get_db)):
    page = get_page_by("id", page_id, db)
    if page:
        return page
    raise fastapi.HTTPException(status_code=404)


@app.delete("/page/{page_id}")
def delete_page(page_id: str, db: orm.Session = fastapi.Depends(get_db)):
    page = get_page_by("id", page_id, db)
    if page:
        db.delete(page)
        db.commit()
        return JSONResponse(status_code=200, content="Page successfully deleted")
    raise fastapi.HTTPException(status_code=404)


def get_page_by(field: str, value: str, db: orm.Session):
    return db.query(model.Page).filter(model.Page.__getattribute__(model.Page, field) == value).first()
