import json
from datetime import datetime
from flask import Response, request, url_for
from flask_restful import Resource, reqparse
from models import db, Log, User
from utils import HourLoggerBuilder, create_error_response
from constants import *



class LogListResource(Resource):
    def get(self, username):
        """Retrieve all logs for a specific user."""
        body = HourLoggerBuilder()
        body.add_namespace("hlog", LINK_RELATIONS_URL)
        body.add_control("self", url_for("loglistresource", username=username))
        body.add_control("categories-all", url_for("categorylistresource"))
        body.add_control_add_log(username)
        body["items"] = []
        
        logs = Log.query.filter_by(user_id=username).all()
        for log in logs:
            item = HourLoggerBuilder()
            item.add_control("self", url_for("logresource", rid=log.rid))
            item.add_control("profile", LOG_PROFILE)
            item.add_control("user", url_for("userresource", username=username))
            item.add_control("activity", url_for("activityresource", category=log.activity_category, name=log.activity_name))
            item["id"] = log.rid,
            item["user_id"] = log.user_id,
            item["activity_name"] = log.activity_name
            item["start_time"] = log.start_time.isoformat()
            item["end_time"] = log.end_time.isoformat()
            item["comments"] = log.comments
            
            body["items"].append(item)
            
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, username):
        """Create a new log entry for the specified user."""
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
            
        parser = reqparse.RequestParser()
        parser.add_argument("activity_category", required=True, help="Activity category is required")
        parser.add_argument("activity_name", required=True, help="Activity name is required")
        parser.add_argument("start_time", required=True, help="Start time is required")
        parser.add_argument("end_time", required=True, help="End time is required")
        parser.add_argument("comments", required=False)
        data = parser.parse_args()

        user = User.query.filter_by(username=username).first()
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
            user_id=username,
            activity_category=data["activity_category"],
            activity_name=data["activity_name"],
            start_time=start_time,
            end_time=end_time,
            comments=data.get("comments"),
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
        
        body = HourLoggerBuilder()
        body.add_namespace("hlog", LINK_RELATIONS_URL)
        body.add_control("self", url_for("logresource", rid=rid))
        body.add_control("profile", LOG_PROFILE)
        body.add_control("collection", url_for("loglistresource", username=log.user_id))
        body.add_control("user", url_for("userresource", username=log.user_id))
        body.add_control("activity", url_for("activityresource", category=log.activity_category, name=log.activity_name))
        body.add_control_delete_log(rid)
            
        
        body["id"] = log.rid,
        body["user_id"] = log.user_id,
        body["activity_name"] = log.activity_name
        body["start_time"] = log.start_time.isoformat()
        body["end_time"] = log.end_time.isoformat()
        body["comments"] = log.comments
        
        return Response(json.dumps(body), 200, mimetype=MASON)

    def delete(self, rid):
        """Delete a log entry."""
        log = Log.query.get(rid)
        if not log:
            return {"error": "Log not found"}, 404

        db.session.delete(log)
        db.session.commit()
        return {"message": "Log deleted"}, 200
