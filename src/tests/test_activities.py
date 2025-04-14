import pytest
from models import db, Activity, Category
from app import app

@pytest.fixture
def client():
    """ Sets up a test client and a temporary in-memory database """
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
    """ Tests creating a new activity (valid case) """
    response = client.post("/categories/Exercise/activities/", json={"name": "Yoga", "description": "Morning yoga"})
    assert response.status_code == 201

def test_create_activity_with_nonexistent_category(client):
    """ Tests trying to create an activity under a non-existing category (should fail) """
    response = client.post("/categories/Mindfulness/activities/", json={"name": "Meditation"})
    assert response.status_code == 404

def test_create_duplicate_activity(client):
    """ Tests trying to create a duplicate activity (should fail) """
    client.post("/categories/Exercise/activities/", json={"name": "Yoga"})
    response = client.post("/categories/Exercise/activities/", json={"name": "Yoga"})
    assert response.status_code == 409

def test_delete_nonexistent_activity(client):
    """ Test deleting an activity that does not exist (should return 404) """
    response = client.delete("/categories/Exercise/activities/NonExistentActivity")
    assert response.status_code == 404

def test_create_activity_missing_fields(client):
    """ Tests creating an activity with missing fields (should fail) """
    response = client.post("/categories/Exercise/activities/", json={})
    assert response.status_code == 415
    assert "Unsupported media type" in response.json["@error"]["@message"]

def test_get_all_activities(client):
    """ Test retrieving all activities in a category """
    client.post("/categories/Exercise/activities/", json={"name": "Yoga"})
    client.post("/categories/Exercise/activities/", json={"name": "Pilates"})

    response = client.get("/categories/Exercise/activities/")
    assert response.status_code == 200
    assert "@controls" in response.json
    assert "items" in response.json
    assert len(response.json["items"]) >= 2

def test_get_activity_not_found(client):
    """ Tests retrieving an activity that does not exist (should return 404) """
    response = client.get("/categories/UnknownCategory/activities/NonExistentActivity")
    assert response.status_code == 404

def test_update_nonexistent_activity(client):
    """ Test updating an activity that does not exist (should return 404) """
    response = client.put("/categories/Exercise/activities/UnknownActivity", json={"description": "Updated desc"})
    assert response.status_code == 404

def test_update_activity_description(client):
    """ Tests updating an activity's description """
    client.post("/categories/Exercise/activities/", json={"name": "Swimming"})
    response = client.put("/categories/Exercise/activities/Swimming", json={"description": "Pool swimming"})
    assert response.status_code == 200

def test_delete_existing_activity(client):
    """ Test deleting an existing activity """
    client.post("/categories/Exercise/activities/", json={"name": "Jogging"})
    response = client.delete("/categories/Exercise/activities/Jogging")
    assert response.status_code == 200
    
def test_update_activity_missing_payload(client):
    """ Test updating an activity with no payload (should return 415) """
    client.post("/categories/Exercise/activities/", json={"name": "Stretching"})
    response = client.put("/categories/Exercise/activities/Stretching")
    assert response.status_code == 415