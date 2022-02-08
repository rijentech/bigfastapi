from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.db.database import get_db, Base
from bigfastapi.auth import is_authenticated
from bigfastapi.schemas.users_schemas import User
from main import app
from uuid import uuid4

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db


async def override_is_authenticated():
    user_data = {
        "id": uuid4().hex,
        "email": "test@zuri.com",
        "first_name": "Sparrow",
        "last_name": "Jack",
        "phone_number": "+2345669506045",
        "password": "hashedpassword",
        "is_active": True,
        "is_verified": True,
        "is_superuser": True,
        "organization": "Dorime"
    }
    return User(**user_data)


app.dependency_overrides[is_authenticated] = override_is_authenticated


def test_stream_videos():
    response = client.post(
        '/video/stream',
        json={"url": "https://www.youtube.com/watch?v=T5y9kRXgYEM"})
    assert response.status_code == 200, response.text
    data = response.json()
    print(data)


def test_user_stream_list():
    response = client.get('/video/stream')
    assert response.status_code == 200, response.text


def test_get_stream():
    response = client.get('/video/stream/f4335345f43564f454436')
    assert response.status_code == 200, response.text


def test_delete_video():
    response = client.delete('/video/stream/f4335345f43564f454436')
    assert response.status_code == 404, response.text


def test_download_videos():
    response = client.post(
        '/video/download',
        json={"video_id": "f4335345f43564f454436"})
    assert response.status_code == 422, response.text
    data = response.json()
    print(data)
