from flask import Blueprint, request, jsonify
from models import db, Log, User, Activity
from datetime import datetime

log_bp = Blueprint("log_bp", __name__)

@log_bp.route("/", methods=["GET"])
def get_logs():
    """Retrieve all logs."""
    logs = Log.query.all()
    return jsonify([
        {
            "id": log.rid, "user": log.user_id, "activity": log.activity_name,
            "start_time": log.start_time, "end_time": log.end_time, "comments": log.comments
        } for log in logs
    ]), 200

@log_bp.route("/<int:rid>", methods=["GET"])
def get_log(rid):
    """Retrieve a single log entry."""
    log = Log.query.get(rid)
    if not log:
        return jsonify({"error": "Log not found"}), 404
    return jsonify({
        "id": log.rid, "user": log.user_id, "activity": log.activity_name,
        "start_time": log.start_time, "end_time": log.end_time, "comments": log.comments
    }), 200

@log_bp.route("/", methods=["POST"])
def create_log():
    """Create a new log entry."""
    data = request.json
    if not all(k in data for k in ["user_id", "activity_name", "start_time", "end_time"]):
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter_by(username=data["user_id"]).first()
    activity = Activity.query.filter_by(name=data["activity_name"]).first()

    if not user or not activity:
        return jsonify({"error": "User or activity does not exist"}), 404

    log = Log(
        user_id=data["user_id"],
        activity_name=data["activity_name"],
        start_time=datetime.fromisoformat(data["start_time"]),
        end_time=datetime.fromisoformat(data["end_time"]),
        comments=data.get("comments")
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({"message": "Log created successfully"}), 201

@log_bp.route("/<int:rid>", methods=["DELETE"])
def delete_log(rid):
    """Delete a log entry."""
    log = Log.query.get(rid)
    if not log:
        return jsonify({"error": "Log not found"}), 404

    db.session.delete(log)
    db.session.commit()
    return jsonify({"message": "Log deleted"}), 200
