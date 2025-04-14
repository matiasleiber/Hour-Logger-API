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
    response = client.post("/users/test_user/reports/", json={
        "start_time": "2024-02-10T08:00:00",
        "end_time": "2024-02-10T16:00:00"
    })
    assert response.status_code == 201

def test_create_report_for_invalid_user(client):
    """ Tests trying to create a report for a non-existent user (should fail) """
    response = client.post("/users/non_existent/reports/", json={
        "start_time": "2024-02-10T08:00:00",
        "end_time": "2024-02-10T16:00:00"
    })
    assert response.status_code == 404

def test_create_time_report_missing_fields(client):
    """ Tests creating a time report with missing fields """
    response = client.post("/users/test_user/reports/", json={})
    assert response.status_code == 415

def test_create_time_report_invalid_times(client):
    """ Tests creating a time report where start_time >= end_time (should fail) """
    response = client.post("/users/test_user/reports/", json={
        "start_time": "2024-02-10T18:00:00",
        "end_time": "2024-02-10T16:00:00"
    })
    assert response.status_code == 400

def test_get_nonexistent_time_report(client):
    """ Tests retrieving a time report that does not exist """
    response = client.get("/reports/999")
    assert response.status_code == 404

def test_delete_time_report(client):
    """ Test deleting an existing time report """
    client.post("/users/test_user/reports/", json={
        "start_time": "2024-02-10T08:00:00",
        "end_time": "2024-02-10T16:00:00"
    })
    with app.app_context():
        rid = TimeReport.query.first().rid
    response = client.delete(f"/reports/{rid}")
    assert response.status_code == 200

def test_delete_nonexistent_report(client):
    """ Test deleting a time report that does not exist (should return 404) """
    response = client.delete("/reports/9999")
    assert response.status_code == 404
    
def test_create_report_invalid_json(client):
    """ Test creating a report with no JSON body (should return 415) """
    response = client.post("/users/test_user/reports/")
    assert response.status_code == 415

def test_create_report_malformed_time(client):
    """ Test creating a report with invalid datetime format (should return 400) """
    response = client.post("/users/test_user/reports/", json={
        "start_time": "bad-format",
        "end_time": "bad-format-2"
    })
    assert response.status_code == 400
