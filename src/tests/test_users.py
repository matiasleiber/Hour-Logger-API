import pytest
from models import db, User, Category, Activity
from app import app

@pytest.fixture
def client():
    """ Sets up a test client and a temporary in-memory database """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        db.session.add(Category(name="Hobby", description="Fun stuff"))
        db.session.commit()
    yield app.test_client()
    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_create_user(client):
    """ Tests creating a new user (valid case) """
    response = client.post("/users/", json={"username": "test_user", "password": "securepass"})
    assert response.status_code == 201

def test_get_user(client):
    """ Tests fetching a user that exists (valid case) """
    client.post("/users/", json={"username": "test_user", "password": "securepass"})
    response = client.get("/users/test_user")
    assert response.status_code == 200
    assert response.json["username"] == "test_user"

def test_create_duplicate_user(client):
    """ Tests trying to create a duplicate user (should fail) """
    client.post("/users/", json={"username": "test_user", "password": "securepass"})
    response = client.post("/users/", json={"username": "test_user", "password": "newpass"})
    assert response.status_code == 409
    assert "error" in response.json

def test_create_user_missing_fields(client):
    """ Tests creating a user with missing fields (should fail) """
    response = client.post("/users/", json={"username": "test_user"})
    assert response.status_code == 400
    assert "message" in response.json
    assert "password" in response.json["message"]

def test_get_non_existent_user(client):
    """ Tests fetching a user that does not exist (should fail) """
    response = client.get("/users/nonexistent")
    assert response.status_code == 404
    assert "error" in response.json

def test_update_user_password(client):
    """ Test updating a user's password """
    client.post("/users/", json={"username": "test_user", "password": "securepass"})
    response = client.put("/users/test_user", json={"password": "new_secure_pass"})
    assert response.status_code == 200
    assert response.json["message"] == "User password updated"

def test_get_all_users(client):
    """ Test retrieving all users """
    client.post("/users/", json={"username": "user1", "password": "pass1"})
    client.post("/users/", json={"username": "user2", "password": "pass2"})

    response = client.get("/users/")
    assert response.status_code == 200
    assert "items" in response.json
    assert len(response.json["items"]) >= 2

def test_delete_user_with_logs(client):
    """ Tests deleting a user with logs (logs should be set to NULL) """
    client.post("/users/", json={"username": "test_user", "password": "1234"})
    client.post("/categories/Hobby/activities/", json={"name": "Reading"})

    response = client.post("/users/test_user/logs/", json={
        "activity_category": "Hobby",
        "activity_name": "Reading",
        "start_time": "2024-02-10T12:00:00",
        "end_time": "2024-02-10T14:00:00",
        "comments": "Read a book"
    })
    assert response.status_code == 201

    delete_response = client.delete("/users/test_user")
    assert delete_response.status_code == 200

def test_update_nonexistent_user(client):
    """ Test updating a user that doesn't exist (should return 404) """
    response = client.put("/users/ghost", json={"password": "irrelevant"})
    assert response.status_code == 404
    
def test_create_user_invalid_content_type(client):
    """ Test creating a user with no JSON payload (should return 415) """
    response = client.post("/users/")
    assert response.status_code == 415
