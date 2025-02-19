from datetime import datetime
from flask_restful import Resource, reqparse
from models import db, Log, User



class LogListResource(Resource):
    def get(self):
        """Retrieve all logs."""
        logs = Log.query.all()
        return [
            {
                "id": log.rid,
                "user_id": log.user_id,
                "activity_name": log.activity_name,
                "start_time": log.start_time.isoformat(),
                "end_time": log.end_time.isoformat(),
                "comments": log.comments,
            }
            for log in logs
        ], 200

    def post(self):
        """Create a new log entry."""
        parser = reqparse.RequestParser()
        parser.add_argument("user_id", required=True, help="User ID is required")
        parser.add_argument("activity_name", required=True, help="Activity name is required")
        parser.add_argument("start_time", required=True, help="Start time is required")
        parser.add_argument("end_time", required=True, help="End time is required")
        parser.add_argument("comments", required=False)
        data = parser.parse_args()

        user = User.query.filter_by(username=data["user_id"]).first()
        if not user:
            return {"error": "User does not exist"}, 404

        try:
            start_time = datetime.fromisoformat(data["start_time"])
            end_time = datetime.fromisoformat(data["end_time"])
        except ValueError:
            return {"error": "Invalid date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"}, 400

        if start_time >= end_time:
            return {"error": "Start time must be before end time"}, 400

        log = Log(
            user_id=data["user_id"],
            activity_name=data["activity_name"],
            start_time=start_time,
            end_time=end_time,
            comments=data["comments"],
        )
        db.session.add(log)
        db.session.commit()
        return {"message": "Log created successfully"}, 201


class LogResource(Resource):
    def get(self, rid):
        """Retrieve a specific log entry."""
        log = Log.query.get(rid)
        if not log:
            return {"error": "Log not found"}, 404
        return {
            "id": log.rid,
            "user_id": log.user_id,
            "activity_name": log.activity_name,
            "start_time": log.start_time.isoformat(),
            "end_time": log.end_time.isoformat(),
            "comments": log.comments,
        }, 200

    def delete(self, rid):
        """Delete a log entry."""
        log = Log.query.get(rid)
        if not log:
            return {"error": "Log not found"}, 404

        db.session.delete(log)
        db.session.commit()
        return {"message": "Log deleted"}, 200
