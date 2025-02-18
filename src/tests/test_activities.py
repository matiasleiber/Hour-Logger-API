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
    response = client.post("/activities/", json={"name": "Yoga", "category_name": "Exercise", "description": "Morning yoga"})
    assert response.status_code == 201

def test_create_activity_with_nonexistent_category(client):
    """ Tests trying to create an activity under a non-existing category (should fail) """
    response = client.post("/activities/", json={"name": "Meditation", "category_name": "Mindfulness"})
    assert response.status_code == 404

def test_create_duplicate_activity(client):
    """ Tests trying to create a duplicate activity (should fail) """
    client.post("/activities/", json={"name": "Yoga", "category_name": "Exercise"})
    response = client.post("/activities/", json={"name": "Yoga", "category_name": "Exercise"})
    assert response.status_code == 409

def test_delete_nonexistent_activity(client):
    """ Test deleting an activity that does not exist (should return 404) """
    response = client.delete("/activities/NonExistentActivity")
    assert response.status_code == 404

def test_create_activity_invalid_category(client):
    """ Test creating an activity with a non-existent category (should return 404) """
    response = client.post("/activities/", json={"name": "Pilates", "category_name": "UnknownCategory"})
    assert response.status_code == 404

def test_create_activity_missing_fields(client):
    """ Tests creating an activity with missing fields (should fail) """
    response = client.post("/activities/", json={"name": "Pilates"})
    assert response.status_code == 400
    assert "error" in response.json

def test_get_all_activities(client):
    """ Test retrieving all activities """
    client.post("/activities/", json={"name": "Yoga", "category_name": "Exercise"})
    client.post("/activities/", json={"name": "Pilates", "category_name": "Exercise"})
    
    response = client.get("/activities/")
    assert response.status_code == 200
    assert len(response.json) >= 2

def test_update_nonexistent_activity(client):
    """ Test updating an activity that does not exist (should return 404) """
    response = client.put("/activities/UnknownActivity", json={"description": "Updated desc"})
    assert response.status_code == 404
    