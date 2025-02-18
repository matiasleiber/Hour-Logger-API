import pytest
from models import db, Category
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

def test_create_category(client):
    response = client.post("/categories/", json={"name": "Exercise", "description": "Workout activities"})
    assert response.status_code == 201
