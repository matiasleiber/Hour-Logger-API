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
    response = client.post("/users/test_user/logs/", json={
        "activity_category": "Exercise",
        "activity_name": "Yoga",
        "start_time": "2024-02-10T08:00:00",
        "end_time": "2024-02-10T09:00:00",
        "comments": "Great session!"
    })
    assert response.status_code == 201

def test_create_log_with_invalid_user(client):
    """ Tests trying to log an activity for a non-existent user (should fail) """
    response = client.post("/users/invalid_user/logs/", json={
        "activity_category": "Exercise",
        "activity_name": "Pilates",
        "start_time": "2024-02-10T08:00:00",
        "end_time": "2024-02-10T09:00:00"
    })
    assert response.status_code == 404
    assert response.json["error"] == "User does not exist"

def test_get_logs_nonexistent_user(client):
    """ Test retrieving logs for a user that does not exist (should return empty) """
    response = client.get("/users/nonexistent_user/logs/")
    assert response.status_code in (200, 404)

def test_create_log_invalid_timestamps(client):
    """ Tests creating a log with invalid timestamps (start >= end) """
    response = client.post("/users/test_user/logs/", json={
        "activity_category": "Exercise",
        "activity_name": "Yoga",
        "start_time": "2024-02-10T10:00:00",
        "end_time": "2024-02-10T09:00:00",
        "comments": "Invalid times"
    })
    assert response.status_code == 400

def test_get_empty_logs(client):
    """ Tests retrieving logs when none exist (should return an empty list) """
    response = client.get("/users/test_user/logs/")
    assert response.status_code == 200
    assert "items" in response.json
    assert isinstance(response.json["items"], list)

def test_get_single_log(client):
    """ Test retrieving a single, already existing log entry """
    client.post("/users/test_user/logs/", json={
        "activity_category": "Exercise",
        "activity_name": "Yoga",
        "start_time": "2024-02-10T10:00:00",
        "end_time": "2024-02-10T11:00:00"
    })
    with app.app_context():
        log_id = Log.query.first().rid
    response = client.get(f"/logs/{log_id}")
    assert response.status_code == 200
    
def test_delete_log(client):
    """ Test deleting an existing log """
    client.post("/users/test_user/logs/", json={
        "activity_category": "Exercise",
        "activity_name": "Yoga",
        "start_time": "2024-02-10T10:00:00",
        "end_time": "2024-02-10T11:00:00"
    })
    with app.app_context():
        log_id = Log.query.first().rid
    response = client.delete(f"/logs/{log_id}")
    assert response.status_code == 200
    
def test_get_nonexistent_log(client):
    """ Test retrieving a log that does not exist (should return 404) """
    response = client.get("/logs/9999")
    assert response.status_code == 404
    
def test_create_log_no_json(client):
    """ Test creating a log with no JSON payload (should return 415) """
    response = client.post("/users/test_user/logs/")
    assert response.status_code == 415

def test_create_log_invalid_time_format(client):
    """ Test creating a log with bad datetime format (should return 400) """
    response = client.post("/users/test_user/logs/", json={
        "activity_category": "Exercise",
        "activity_name": "Yoga",
        "start_time": "bad-time",
        "end_time": "worse-time"
    })
    assert response.status_code == 400
