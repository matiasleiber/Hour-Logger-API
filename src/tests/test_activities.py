import pytest
from models import db, Activity, Category
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        db.session.add(Category(name="Exercise", description="Workout activities"))
        db.session.commit()
    yield app.test_client()
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_create_activity(client):
    response = client.post("/activities/", json={"name": "Yoga", "category_name": "Exercise", "description": "Morning yoga"})
    assert response.status_code == 201
