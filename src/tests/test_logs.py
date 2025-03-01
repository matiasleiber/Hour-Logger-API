import pytest
from models import db, Log, User, Activity, Category
from app import app
from datetime import datetime

@pytest.fixture
def client():
    """ Sets up a test client and a temporary in-memory database """
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
    """ Tests creating a new log (valid case) """
    response = client.post("/logs/", json={
        "user_id": "test_user",
        "activity_name": "Yoga",
        "start_time": "2024-02-10T08:00:00",
        "end_time": "2024-02-10T09:00:00",
        "comments": "Great session!"
    })
    assert response.status_code == 201

def test_create_log_with_invalid_user(client):
    """ Tests trying to log an activity for a non-existent user (should fail) """
    response = client.post("/logs/", json={
        "user_id": "invalid_user",
        "activity_name": "Pilates",
        "start_time": "2024-02-10T08:00:00",
        "end_time": "2024-02-10T09:00:00"
    })
    assert response.status_code == 404
    assert response.json["error"] == "User does not exist"

def test_get_logs_nonexistent_user(client):
    """ Test retrieving logs for a user that does not exist (should return 404) """
    response = client.get("/logs/nonexistent_user")
    assert response.status_code == 404

def test_create_log_invalid_timestamps(client):
    """ Tests creating a log with invalid timestamps (start >= end) """
    client.post("/users/", json={"username": "test_user", "password": "1234"})
    client.post("/activities/", json={"name": "Running", "category_name": "Exercise"})
    
    response = client.post("/logs/", json={
        "user_id": "test_user",
        "activity_name": "Running",
        "start_time": "2024-02-10T10:00:00",
        "end_time": "2024-02-10T09:00:00",
        "comments": "Invalid times"
    })
    assert response.status_code == 400
    
def test_get_empty_logs(client):
    """ Tests retrieving logs when none exist (should return an empty list) """
    response = client.get("/logs/")
    assert response.status_code == 200
    assert response.json == []
