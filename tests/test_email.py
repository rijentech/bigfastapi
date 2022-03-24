from http import client
from main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bigfastapi.db.database import Base, get_db
from fastapi_mail.errors import ConnectionErrors

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


def test_send_email():
    response = client.post(
        "/email/send",
        json={
            "subject": "Rejection",
            "recipient": ["test@email.com"],
            "title": "title",
            "first_name": "Samuel",
            "body": "the body",
            "sender_address": "test",
            "sender_city": "test",
            "sender_state": "test"
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Email will be sent in the background"

def test_send_notification_email():
    response = client.post(
        "/email/send/notification",
        json={
            "subject": "Rejection",
            "recipient": ["test@email.com"],
            "title": "title",
            "first_name": "Samuel",
            "body": "the body",
            "sender": "mark",
            "sender_address": "test",
            "sender_city": "test",
            "sender_state": "test"
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Notification Email will be sent in the background"



def test_send_invoice_mail():
    response = client.post(
        "/email/send/invoice",
        json={
            "subject": "Invoice from BigFastAPI",
            "recipient": ["test@email.com"],
            "title": "Invoice for Ps5",
            "first_name": "Psami",
            "amount": "$1000",
            "due_date": "Today Today",
            "payment_link": "paystack.com",
            "invoice_id": "7976GDDHD573JDJVJ",
            "description": "PlayStation 5 Console",
            "sender_address": "test",
            "sender_city": "test",
            "sender_state": "test"
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Invoice Email will be sent in the background"


def test_send_receipt_mail():
    response = client.post(
        "/email/send/receipt",
        json={
            "subject": "Receipt from BigFastAPI",
            "recipient": ["test@email.com"],
            "title": "Payment for Ps5",
            "first_name": "Samuel",
            "amount": "$600",
            "receipt_id": "HDGY4532WHMMS",
            "description": "PlayStation 5 Console",
            "sender_address": "test",
            "sender_city": "test",
            "sender_state": "test"
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Receipt Email will be sent in the background"

def test_send_welcome_email():
    response = client.post(
        "/email/send/welcome",
        json={
            "subject": "Welcome",
            "recipient": ["test@email.com"],
            "title": "Payment for Ps5",
            "first_name": "Samuel",
            "body": "test_body",
            "link": "clickme",
            "sender_address": "test",
            "sender_city": "test",
            "sender_state": "test"
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Welcome Email will be sent in the background"

def test_send_verification_email():
    response = client.post(
        "/email/send/verification",
        json={
            "subject": "Verify Your Email",
            "recipient": ["test@email.com"],
            "title": "Payment for Ps5",
            "first_name": "Samuel",
            "body": "test_body",
            "link": "dbshj",
            "sender_address": "test",
            "sender_city": "test",
            "sender_state": "test"
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Verification Email will be sent in the background"

def test_send_reset_password_email():
    try: 
        response = client.post(
            "/email/send/reset-password",
            json={
                "subject": "Reset Password",
                "recipient": ["okechukwusamuel16@gmail.com"],
                "title": "Payment for Ps5",
                "first_name": "Samuel",
                "link": "reset_password_link",
                "sender_address": "test",
                "sender_city": "test",
                "sender_state": "test"
            },
        )
        assert response.status_code == 200, response.text
        assert response.json()["message"] == "Reset Password Email will be sent in the background"
    except ConnectionErrors:
        print("Connection Errors")
        pass
