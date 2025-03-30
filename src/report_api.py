import json
from flask import Response, request, url_for
from flask_restful import Resource, reqparse
from models import db, TimeReport, User
from datetime import datetime
from utils import HourLoggerBuilder, create_error_response
from constants import *

class ReportListResource(Resource):
    def get(self, username):
        """Retrieve all reports for a specific user."""
        body = HourLoggerBuilder()
        body.add_namespace("hlog", LINK_RELATIONS_URL)
        body.add_control("self", url_for("reportlistresource", username=username))
        body.add_control_add_report(username)
        body["items"] = []
        
        reports = TimeReport.query.filter_by(user_id=username).all()
        for report in reports:
            item = HourLoggerBuilder()
            item.add_control("self", url_for("reportresource", rid=report.rid))
            item.add_control("profile", LOG_PROFILE)
            item.add_control("user", url_for("userresource", username=username))
            item["id"] = report.rid,
            item["user_id"] = report.user_id,
            item["start_time"] = report.start_time.isoformat()
            item["end_time"] = report.end_time.isoformat()
            
            body["items"].append(item)
            
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, username):
        """Create a new time report for the specified user."""
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
            
        parser = reqparse.RequestParser()
        parser.add_argument("start_time", required=True, help="Start time is required")
        parser.add_argument("end_time", required=True, help="End time is required")
        data = parser.parse_args()

        user = User.query.filter_by(username=username).first()
        if not user:
            return {"error": "User not found"}, 404

        try:
            start_time = datetime.fromisoformat(data["start_time"])
            end_time = datetime.fromisoformat(data["end_time"])
        except ValueError:
            return {"error": "Invalid date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"}, 400

        if start_time >= end_time:
            return {"error": "Start time must be before end time"}, 400

        report = TimeReport(user_id=username, start_time=start_time, end_time=end_time)
        db.session.add(report)
        db.session.commit()
        return {"message": "Report created successfully"}, 201


class ReportResource(Resource):
    def get(self, rid):
        """Retrieve a specific report."""
        report = TimeReport.query.get(rid)
        if not report:
            return {"error": "Report not found"}, 404
            
        body = HourLoggerBuilder()
        body.add_namespace("hlog", LINK_RELATIONS_URL)
        body.add_control("self", url_for("logresource", rid=rid))
        body.add_control("profile", REPORT_PROFILE)
        body.add_control("collection", url_for("reportlistresource", username=report.user_id))
        body.add_control("user", url_for("userresource", username=report.user_id))
        body.add_control_delete_report(rid)
        
        body["id"] = report.rid,
        body["user_id"] = report.user_id,
        body["start_time"] = report.start_time.isoformat()
        body["end_time"] = report.end_time.isoformat()
        
        return Response(json.dumps(body), 200, mimetype=MASON)

    def delete(self, rid):
        """Delete a report."""
        report = TimeReport.query.get(rid)
        if not report:
            return {"error": "Report not found"}, 404

        db.session.delete(report)
        db.session.commit()
        return {"message": "Report deleted"}, 200
