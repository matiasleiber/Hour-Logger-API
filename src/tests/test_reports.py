import pytest
from models import db, TimeReport, User
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
        db.session.commit()
    yield app.test_client()
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_create_time_report(client):
    """ Tests creating a time report (valid case) """
    response = client.post("/reports/", json={
        "user_id": "test_user",
        "start_time": "2024-02-10T08:00:00",
        "end_time": "2024-02-10T16:00:00"
    })
    assert response.status_code == 201

def test_create_report_for_invalid_user(client):
    """ Tests trying to create a report for a non-existent user (should fail) """
    response = client.post("/reports/", json={"user_id": "non_existent", "start_time": "2024-02-10T08:00:00", "end_time": "2024-02-10T16:00:00"})
    assert response.status_code == 404
