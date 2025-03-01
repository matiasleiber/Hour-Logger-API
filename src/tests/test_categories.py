import pytest
from models import db, Category
from app import app

@pytest.fixture
def client():
    """ Sets up a test client and a temporary in-memory database """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
    yield app.test_client()
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_create_category(client):
    """ Tests creating a new category (valid case) """
    response = client.post("/categories/", json={"name": "Exercise", "description": "Workout activities"})
    assert response.status_code == 201

def test_create_duplicate_category(client):
    """ Tests trying to create a duplicate category (should fail) """
    client.post("/categories/", json={"name": "Exercise", "description": "Workout activities"})
    response = client.post("/categories/", json={"name": "Exercise", "description": "Different description"})
    assert response.status_code == 409

def test_create_category_missing_name(client):
    """ Tests creating a category with missing name (should fail) """
    response = client.post("/categories/", json={"description": "Workout activities"})
    assert response.status_code == 400

def test_get_non_existent_category(client):
    """ Tests fetching a category that does not exist (should fail) """
    response = client.get("/categories/UnknownCategory")
    assert response.status_code == 404

def test_delete_nonexistent_category(client):
    """ Test deleting a category that does not exist (should return 404) """
    response = client.delete("/categories/NonExistentCategory")
    assert response.status_code == 404

def test_get_all_categories(client):
    """ Test retrieving all categories """
    client.post("/categories/", json={"name": "Work", "description": "Work-related tasks"})
    client.post("/categories/", json={"name": "Hobby", "description": "Leisure activities"})
    
    response = client.get("/categories/")
    assert response.status_code == 200
    assert len(response.json) >= 2

def test_update_nonexistent_category(client):
    """ Test updating a category that does not exist (should return 404) """
    response = client.put("/categories/UnknownCategory", json={"description": "Updated desc"})
    assert response.status_code == 404
    

def test_update_category_description(client):
    """ Tests updating a category description """
    client.post("/categories/", json={"name": "Music", "description": "Old description"})
    
    response = client.put("/categories/Music", json={"description": "New description"})
    assert response.status_code == 200
