from flask import Blueprint, request, jsonify
from models import db, Activity, Category

activity_bp = Blueprint("activity_bp", __name__)

@activity_bp.route("/", methods=["GET"])
def get_activities():
    """Retrieve all activities."""
    activities = Activity.query.all()
    return jsonify([
        {"name": act.name, "category": act.category_name, "description": act.description} for act in activities
    ]), 200

@activity_bp.route("/<string:name>/<string:category>", methods=["GET"])
def get_activity(name, category):
    """Retrieve a single activity."""
    activity = Activity.query.filter_by(name=name, category_name=category).first()
    if not activity:
        return jsonify({"error": "Activity not found"}), 404
    return jsonify({
        "name": activity.name,
        "category": activity.category_name,
        "description": activity.description
    }), 200

@activity_bp.route("/", methods=["POST"])
def create_activity():
    """Create a new activity."""
    data = request.json
    if not all(k in data for k in ["name", "category_name"]):
        return jsonify({"error": "Missing required fields"}), 400

    category = Category.query.filter_by(name=data["category_name"]).first()
    if not category:
        return jsonify({"error": "Category does not exist"}), 404

    activity = Activity(name=data["name"], category_name=data["category_name"], description=data.get("description"))
    db.session.add(activity)

    try:
        db.session.commit()
        return jsonify({"message": "Activity created successfully"}), 201
    except:
        db.session.rollback()
        return jsonify({"error": "Activity already exists"}), 409

@activity_bp.route("/<string:name>/<string:category>", methods=["PUT"])
def update_activity(name, category):
    """Update an activity."""
    activity = Activity.query.filter_by(name=name, category_name=category).first()
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    data = request.json
    activity.description = data.get("description", activity.description)
    db.session.commit()
    return jsonify({"message": "Activity updated"}), 200

@activity_bp.route("/<string:name>/<string:category>", methods=["DELETE"])
def delete_activity(name, category):
    """Delete an activity."""
    activity = Activity.query.filter_by(name=name, category_name=category).first()
    if not activity:
        return jsonify({"error": "Activity not found"}), 404

    db.session.delete(activity)
    db.session.commit()
    return jsonify({"message": "Activity deleted"}), 200
