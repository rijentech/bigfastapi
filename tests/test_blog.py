import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.models import blog_models as model
from bigfastapi.schemas import blog_schemas, users_schemas
from bigfastapi.db import database
from bigfastapi.auth import is_authenticated
from main import app


SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
_db = TestingSessionLocal()

async def override_is_authenticated():
    user_data = {
        "id":"9cd87677378946d88dc7903b6710ae55", 
        "first_name": "John", 
        "last_name": "Doe", 
        "email": "test@gmail.com", 
        "password": "hashedpassword", 
        "is_active": True, 
        "is_verified":True, 
        "is_superuser":False, 
        "phone_number":"123456789000", 
        "organization":"test"
    }
    return users_schemas.User(**user_data)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)


@pytest.fixture
def setUp():
    database.Base.metadata.create_all(engine, tables=[model.BlogPost.__table__, model.Blog.__table__])
    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[is_authenticated] = override_is_authenticated

    blog = model.Blog(id="9cd87677378946d88dc7903b6710ae00", creator="9cd87677378946d88dc7903b6710ae55", title="Test Blog")

    blog_data1 = {"title":"First Test Data", "content":"Testing Blog Endpoint"}
    blog_data2 = {"title":"Second Test Data", "content":"Testing Blog Update Endpoint"}
    
    blogpost1 = model.BlogPost(id="9cd87677378946d88dc7903b6710ae44", creator="9cd87677378946d88dc7903b6710ae54", blog_id="9cd87677378946d88dc7903b6710ae00", **blog_data1)
    blogpost2 = model.BlogPost(id="9cd87677378946d88dc7903b6710ae45", creator="9cd87677378946d88dc7903b6710ae55", blog_id="9cd87677378946d88dc7903b6710ae00", **blog_data2)
    _db.add_all([blog, blogpost1, blogpost2])
    _db.commit()
    _db.refresh(blog)
    _db.refresh(blogpost1)
    _db.refresh(blogpost2)

    yield blog_schemas.BlogPost.from_orm(blogpost1)

    database.Base.metadata.drop_all(engine, tables=[model.BlogPost.__table__, model.Blog.__table__])

def test_create_blog(setUp):
    response = client.post("/blog", json={"title":"Testing Blog"})
    assert response.status_code == 200, response.text
    assert response.json().get("title") == "Testing Blog"

def test_get_blog(setUp):
    response = client.get("/blog/9cd87677378946d88dc7903b6710ae00")
    assert response.status_code == 200, response.text
    assert response.json().get("title") == "Test Blog"

def test_get_all_blogs(setUp):
    response = client.get("/blogs")
    assert response.status_code == 200, response.text
    assert len(response.json().get("items")) == 1

def test_get_user_blogs(setUp):
    response = client.get("/blogs/9cd87677378946d88dc7903b6710ae55")
    assert response.status_code == 200, response.text
    assert len(response.json()) == 1

def test_update_blog(setUp):
    response = client.put("/blog/9cd87677378946d88dc7903b6710ae00", json={"title":"Testing Blog!!!"})
    assert response.status_code == 200, response.text
    assert response.json().get("title") == "Testing Blog!!!"

def test_delete_blog(setUp):
    response = client.delete("/blog/9cd87677378946d88dc7903b6710ae00")
    assert response.status_code == 200, response.text
    assert response.json().get("message") == "successfully deleted"

def test_create_blogpost(setUp):
    response = client.post("/blog/9cd87677378946d88dc7903b6710ae00/post", json={"title":"Testing Create Endpoint!!!", "content":"Testing Create Blog Endpoint", "tags":["music", "sport"]})
    assert response.status_code == 200
    assert response.json().get("title") == "Testing Create Endpoint!!!"
    assert response.json().get('tags') == ["music", "sport"]

def test_get_all_blogposts(setUp):
    response = client.get("/blog/9cd87677378946d88dc7903b6710ae00/posts")
    assert response.status_code == 200, response.text
    assert len(response.json()['items']) == 2

def test_get_blogpost(setUp):
    response = client.get("/blog/9cd87677378946d88dc7903b6710ae00/post/9cd87677378946d88dc7903b6710ae44")
    response.status_code = 200
    assert response.json().get("title") == "First Test Data"
    assert response.json().get("content") == "Testing Blog Endpoint"

def test_get_user_blogposts(setUp):
    response = client.get("/blog/9cd87677378946d88dc7903b6710ae00/posts/9cd87677378946d88dc7903b6710ae55")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_update_blogpost(setUp):
    response = client.put("/blog/9cd87677378946d88dc7903b6710ae00/post/9cd87677378946d88dc7903b6710ae45", json={"title": "","content": "Testing Update Blog Endpoint!!!"})
    assert response.status_code == 200, response.text
    assert response.json().get("title") == "Second Test Data"
    assert response.json().get("content") == "Testing Update Blog Endpoint!!!"

def test_update_blogpost_that_was_not_created_by_user(setUp):
    response = client.put("/blog/9cd87677378946d88dc7903b6710ae00/post/9cd87677378946d88dc7903b6710ae44", json={"title": "Second Test Data", "content": "Testing Update Blog Endpoint"})
    assert response.status_code == 403, response.text

def test_delete_blogpost(setUp):
    response = client.delete("/blog/9cd87677378946d88dc7903b6710ae00/post/9cd87677378946d88dc7903b6710ae45")
    assert response.status_code == 200
    assert response.json().get("message") == "successfully deleted"

def test_delete_blogpost_that_was_not_created_by_user(setUp):
    response = client.delete("/blog/9cd87677378946d88dc7903b6710ae00/post/9cd87677378946d88dc7903b6710ae44")
    assert response.status_code == 403