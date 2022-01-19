from fastapi import FastAPI
from bigfastapi import database as _db
from bigfastapi import organization, comments, accounts, blog
from bigfastapi import token

_db.create_database()
app = FastAPI()

# app.include_router(accounts.app)
# app.include_router(organization.app)
# app.include_router(comments.app)
app.include_router(blog.app)


@app.get("/")
async def root():
    return {"message": "Hello World!"}


@app.get("/schema")
async def schema():
    return app.openapi()