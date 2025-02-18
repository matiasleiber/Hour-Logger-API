import pytest
from models import db, User
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
    yield app.test_client()
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_create_user(client):
    response = client.post("/users/", json={"username": "test_user", "password": "1234"})
    assert response.status_code == 201

def test_get_user(client):
    client.post("/users/", json={"username": "test_user", "password": "1234"})
    response = client.get("/users/test_user")
    assert response.status_code == 200
    assert response.json["username"] == "test_user"
