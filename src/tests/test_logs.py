import pytest
from models import db, Log, User, Activity, Category
from app import app
from datetime import datetime

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        db.session.add(User(username="test_user", password="1234"))
        db.session.add(Category(name="Exercise", description="Workout activities"))
        db.session.add(Activity(name="Yoga", category_name="Exercise", description="Morning yoga"))
        db.session.commit()
    yield app.test_client()
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_create_log(client):
    response = client.post("/logs/", json={
        "user_id": "test_user",
        "activity_name": "Yoga",
        "start_time": "2024-02-10T08:00:00",
        "end_time": "2024-02-10T09:00:00",
        "comments": "Great session!"
    })
    assert response.status_code == 201
