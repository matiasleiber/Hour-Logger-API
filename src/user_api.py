import json
from flask import Response, request, url_for
from flask_restful import Resource, reqparse
from models import db, User
from utils import HourLoggerBuilder, create_error_response
from constants import *

class UserListResource(Resource):
    def get(self):
        """Retrieve all users."""
        body = HourLoggerBuilder()
        body.add_namespace("hlog", LINK_RELATIONS_URL)
        body.add_control("self", url_for("userlistresource"))
        body.add_control_add_user()
        body["items"] = []
        
        users = User.query.all()
        for user in users:
            item = HourLoggerBuilder()
            item.add_control("self", url_for("userresource", username=user.username))
            item.add_control("profile", USER_PROFILE)
            item.add_control("categories-all", url_for("categorylistresource"))
            item.add_control("logs-by", url_for("loglistresource", username=user.username))
            item.add_control("reports-by", url_for("reportlistresource", username=user.username))
            item["username"] = user.username
            body["items"].append(item)
            
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        """Create a new user."""
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
        
        parser = reqparse.RequestParser()
        parser.add_argument("username", required=True, help="Username is required")
        parser.add_argument("password", required=True, help="Password is required")
        data = parser.parse_args()

        if User.query.filter_by(username=data["username"]).first():
            return {"error": "User already exists"}, 409

        user = User(username=data["username"], password=data["password"])
        db.session.add(user)
        db.session.commit()
        return {"message": "User created successfully"}, 201


class UserResource(Resource):
    def get(self, username):
        """Retrieve a user by username."""
        user = User.query.filter_by(username=username).first()
        if not user:
            return {"error": "User not found"}, 404
        
        body = HourLoggerBuilder()
        body.add_namespace("hlog", LINK_RELATIONS_URL)
        body.add_control("self", url_for("userresource", username=username))
        body.add_control("profile", USER_PROFILE)
        body.add_control("collection", url_for("userlistresource"))
        body.add_control("categories-all", url_for("categorylistresource"))
        body.add_control("logs-by", url_for("loglistresource", username=username))
        body.add_control("reports-by", url_for("reportlistresource", username=username))
        body.add_control_delete_user(username)
        body.add_control_modify_user(username)
            
        body["username"] = user.username
        
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, username):
        """Update a user's password."""
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
            
        user = User.query.filter_by(username=username).first()
        if not user:
            return {"error": "User not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("password", required=True, help="New password is required")
        data = parser.parse_args()

        user.password = data["password"]
        db.session.commit()
        return {"message": "User password updated"}, 200

    def delete(self, username):
        """Delete a user."""
        user = User.query.filter_by(username=username).first()
        if not user:
            return {"error": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200
