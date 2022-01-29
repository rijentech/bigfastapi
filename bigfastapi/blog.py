
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter
from typing import List
import fastapi as fastapi
import sqlalchemy.orm as orm
from .auth import is_authenticated
from .schemas import users_schemas as user_schema
from .schemas import blog_schemas as schema
from .models import blog_models as model
from bigfastapi.db.database import get_db
from fastapi_pagination import Page, add_pagination, paginate

app = APIRouter(tags=["Blog"])

@app.post("/blog", response_model=schema.BlogPost)
def create_blogpost(blog: schema.BlogPost, user: user_schema.User = fastapi.Depends(is_authenticated), db: orm.Session = fastapi.Depends(get_db)):
    
    """Create a new blog
    
    Returns:
        schema.BlogPost: Details of the newly created blog
    """
   
    blog = model.BlogPost(id=uuid4().hex, title=blog.title, content=blog.content, creator=user.id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return schema.BlogPost.from_orm(blog)

@app.get("/blog/{blog_id}", response_model=schema.BlogPost)
def get_blog(blog_id: str, db: orm.Session = fastapi.Depends(get_db)):

    """Get the details of a blog
    
    Args:
        blog_id (str): the id of the blog

    Returns:
        schema.BlogPost: Details of the requested blog
    """

    return model.blogpost_selector(id=blog_id, db=db)

@app.get("/blogs", response_model=Page[schema.BlogPost])
def get_all_blogs(db: orm.Session = fastapi.Depends(get_db)):

    """Get all the blogs in the database
    
    Returns:
        List of schema.BlogPost: A list of all the blogs
    """

    blogs = db.query(model.BlogPost).all()
    return paginate(list(map(schema.BlogPost.from_orm, blogs)))

@app.get("/blogs/{user_id}", response_model=List[schema.BlogPost])
def get_user_blogposts(user_id: str, db: orm.Session = fastapi.Depends(get_db)):

    """Get all the blogs created by a user
    
    Args:
        user_id (str): the id of the user

    Returns:
        List of schema.BlogPost: A list of all the blogs created by the user
    """

    user_blogs = db.query(model.BlogPost).filter(model.BlogPost.creator == user_id).all()
    return list(map(schema.BlogPost.from_orm, user_blogs))
    
@app.put("/blog/{blog_id}", response_model=schema.BlogPost)
def update_blogpost(blog: schema.BlogPost, blog_id: str, user: user_schema.User = fastapi.Depends(is_authenticated), db: orm.Session = fastapi.Depends(get_db)):

    """Update the details of a blog by the user or superuser
    
    Args:
        blog_id (str): the id of the blog to be updated

    Returns:
        schema.BlogPost: Refreshed data of the updated blog
    """

    blog_db = model.blogpost_selector(id=blog_id, db=db)

    if blog_db == None:
        raise fastapi.HTTPException(status_code=404, detail="Blog does not exist")

    if blog_db.creator != user.id:
        raise fastapi.HTTPException(status_code=403, detail="You are not the creator of the blog post")
    
    if blog.content != "":
        blog_db.content = blog.content

    if blog.title != "":
        blog_db.title = blog.title

    blog_db.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(blog_db)

    return schema.BlogPost.from_orm(blog_db)

@app.delete("/blog/{blog_id}")
def delete_blogpost(blog_id: str, user: user_schema.User = fastapi.Depends(is_authenticated), db: orm.Session = fastapi.Depends(get_db)):
    
    """Delete a blog from the database by the user or superuser
    
    Args:
        blog_id (str): the id of the blog to be deleted

    Returns:
        object (dict): successfully deleted
    """
    
    blog = model.blogpost_selector(id=blog_id, db=db)
    if blog == None:
        raise fastapi.HTTPException(status_code=404, detail="Blog does not exist")
       
    if blog.creator == user.id or user.is_superuser == True:
        db.delete(blog)
        db.commit()

        return {"message":"successfully deleted"}
    else:
        raise fastapi.HTTPException(status_code=403, detail="You are not the allowed to delete the blog post")


add_pagination(app)