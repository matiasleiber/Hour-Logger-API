from flask import Blueprint, request, jsonify
from models import db, User

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/", methods=["GET"])
def get_users():
    """Retrieve all users."""
    users = User.query.all()
    return jsonify([
        {"username": user.username, "password": user.password} for user in users
    ]), 200

@user_bp.route("/<string:username>", methods=["GET"])
def get_user(username):
    """Retrieve a single user."""
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"username": user.username, "password": user.password}), 200

@user_bp.route("/", methods=["POST"])
def create_user():
    """Create a new user."""
    data = request.json
    if "username" not in data or "password" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    user = User(username=data["username"], password=data["password"])
    db.session.add(user)

    try:
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except:
        db.session.rollback()
        return jsonify({"error": "User already exists"}), 409

@user_bp.route("/<string:username>", methods=["PUT"])
def update_user(username):
    """Update a user's password."""
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    user.password = data.get("password", user.password)
    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200

@user_bp.route("/<string:username>", methods=["DELETE"])
def delete_user(username):
    """Delete a user."""
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200
