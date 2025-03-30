import json
from flask import Response, request, url_for
from flask_restful import Resource, reqparse
from models import db, Activity, Category
from utils import HourLoggerBuilder, create_error_response
from constants import *

class ActivityListResource(Resource):
    def get(self, category):
        """Retrieve all activities for a given category."""
        body = HourLoggerBuilder()
        body.add_namespace("hlog", LINK_RELATIONS_URL)
        body.add_control("self", url_for("activitylistresource", category=category))
        body.add_control("categories-all", url_for("categorylistresource"))
        body.add_control_add_activity(category)
        body["items"] = []
        
        activities = Activity.query.filter_by(category_name=category).all()
        for activity in activities:
            item = HourLoggerBuilder()
            item.add_control("self", url_for("activityresource", name=activity.name, category=category))
            item.add_control("profile", ACTIVITY_PROFILE)
            item["name"] = activity.name
            item["category"] = category
            item["description"] = activity.description
            body["items"].append(item)
            
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, category):
        """Create a new activity under the specified category."""
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
        
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True, help="Activity name is required")
        parser.add_argument("description", required=False)
        data = parser.parse_args()

        # Validate that the category exists (using the category in the URL)
        category_obj = Category.query.filter_by(name=category).first()
        if not category_obj:
            return {"error": "Category does not exist"}, 404

        activity = Activity(
            name=data["name"],
            category_name=category,
            description=data.get("description")
        )
        db.session.add(activity)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": "Activity already exists"}, 409
            
        return Response(status=201, headers={
            "Location": url_for("activityresource", name=activity.name, category=activity.category)
        })


class ActivityResource(Resource):
    def get(self, name, category):
        """Retrieve a single activity."""
        activity = Activity.query.filter_by(name=name, category_name=category).first()
        if not activity:
            return {"error": "Activity not found"}, 404
            
        body = HourLoggerBuilder()
        body.add_namespace("hlog", LINK_RELATIONS_URL)
        body.add_control("self", url_for("activityresource", name=name, category=category))
        body.add_control("profile", ACTIVITY_PROFILE)
        body.add_control("collection", url_for("activitylistresource", category=category))
        body.add_control_delete_activity(name, category)
        body.add_control_modify_activity(name, category)
        
        body["name"] = activity.name
        body["category"] = activity.category_name
        body["description"] = activity.description
        
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, name, category):
        """Update an activity."""
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
        
        activity = Activity.query.filter_by(name=name, category_name=category).first()
        if not activity:
            return {"error": "Activity not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("description", required=False)
        data = parser.parse_args()

        activity.description = data["description"] or activity.description
        db.session.commit()
        return {"message": "Activity updated"}, 200

    def delete(self, name, category):
        """Delete an activity."""
        activity = Activity.query.filter_by(name=name, category_name=category).first()
        if not activity:
            return {"error": "Activity not found"}, 404

        db.session.delete(activity)
        db.session.commit()
        return {"message": "Activity deleted"}, 200
