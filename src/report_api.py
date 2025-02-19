from flask_restful import Resource, reqparse
from models import db, TimeReport, User
from datetime import datetime

class ReportListResource(Resource):
    def get(self):
        """Retrieve all reports."""
        reports = TimeReport.query.all()
        return [
            {
                "id": report.rid,
                "user_id": report.user_id,
                "start_time": report.start_time.isoformat(),
                "end_time": report.end_time.isoformat(),
            }
            for report in reports
        ], 200

    def post(self):
        """Create a new time report."""
        parser = reqparse.RequestParser()
        parser.add_argument("user_id", required=True, help="User ID is required")
        parser.add_argument("start_time", required=True, help="Start time is required")
        parser.add_argument("end_time", required=True, help="End time is required")
        data = parser.parse_args()

        user = User.query.filter_by(username=data["user_id"]).first()
        if not user:
            return {"error": "User not found"}, 404

        start_time = datetime.fromisoformat(data["start_time"])
        end_time = datetime.fromisoformat(data["end_time"])

        if start_time >= end_time:
            return {"error": "Start time must be before end time"}, 400

        report = TimeReport(user_id=data["user_id"], start_time=start_time, end_time=end_time)
        db.session.add(report)
        db.session.commit()
        return {"message": "Report created successfully"}, 201


class ReportResource(Resource):
    def get(self, rid):
        """Retrieve a specific report."""
        report = TimeReport.query.get(rid)
        if not report:
            return {"error": "Report not found"}, 404
        return {
            "id": report.rid,
            "user_id": report.user_id,
            "start_time": report.start_time.isoformat(),
            "end_time": report.end_time.isoformat(),
        }, 200

    def delete(self, rid):
        """Delete a report."""
        report = TimeReport.query.get(rid)
        if not report:
            return {"error": "Report not found"}, 404

        db.session.delete(report)
        db.session.commit()
        return {"message": "Report deleted"}, 200
