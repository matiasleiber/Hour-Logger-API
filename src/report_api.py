from flask import Blueprint, request, jsonify
from models import db, TimeReport, User
from datetime import datetime

report_bp = Blueprint("report_bp", __name__)

@report_bp.route("/", methods=["GET"])
def get_reports():
    """Retrieve all time reports."""
    reports = TimeReport.query.all()
    return jsonify([
        {
            "id": report.rid, "user": report.user_id,
            "start_time": report.start_time, "end_time": report.end_time
        } for report in reports
    ]), 200

@report_bp.route("/", methods=["POST"])
def create_report():
    """Create a new time report."""
    data = request.json
    if not all(k in data for k in ["user_id", "start_time", "end_time"]):
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter_by(username=data["user_id"]).first()
    if not user:
        return jsonify({"error": "User does not exist"}), 404

    report = TimeReport(
        user_id=data["user_id"],
        start_time=datetime.fromisoformat(data["start_time"]),
        end_time=datetime.fromisoformat(data["end_time"])
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({"message": "Report created successfully"}), 201
