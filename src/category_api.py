import json
from flask import Response, request, url_for
from flask_restful import Resource, reqparse
from models import db, Category
from utils import HourLoggerBuilder, create_error_response
from constants import *

class CategoryListResource(Resource):
    def get(self):
        """Retrieve all categories."""
        body = HourLoggerBuilder()
        body.add_namespace("hlog", LINK_RELATIONS_URL)
        body.add_control("self", url_for("categorylistresource"))
        body.add_control("users-all", url_for("userlistresource"))
        body.add_control_add_category()
        body["items"] = []
        categories = Category.query.all()
        for category in categories:
            item = HourLoggerBuilder()
            item.add_control("self", url_for("categoryresource", name=category.name))
            item.add_control("profile", CATEGORY_PROFILE)
            item.add_control("activities-in", url_for("activitylistresource", category=category.name))
            item["name"] = category.name
            item["description"] = category.description
            body["items"].append(item)
            
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        """Create a new category."""
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
        
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True, help="Category name is required")
        parser.add_argument("description", required=False)
        data = parser.parse_args()

        category = Category(name=data["name"], description=data["description"])
        db.session.add(category)

        try:
            db.session.commit()
            return {"message": "Category created successfully"}, 201
        except:
            db.session.rollback()
            return {"error": "Category already exists"}, 409


class CategoryResource(Resource):
    def get(self, name):
        """Retrieve a single category."""
        category = Category.query.filter_by(name=name).first()
        if not category:
            return {"error": "Category not found"}, 404
            
        body = HourLoggerBuilder()
        body.add_namespace("hlog", LINK_RELATIONS_URL)
        body.add_control("self", url_for("categoryresource", name=name))
        body.add_control("profile", CATEGORY_PROFILE)
        body.add_control("collection", url_for("categorylistresource"))
        body.add_control("activities-in", url_for("activitylistresource", category=category.name))
        body.add_control_delete_category(name)
        body.add_control_modify_category(name)
            
        body["name"] = category.name
        body["description"] = category.description
        
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, name):
        """Update a category's description."""
        if not request.json:
            return create_error_response(
                415, "Unsupported media type",
                "Requests must be JSON"
            )
        
        category = Category.query.filter_by(name=name).first()
        if not category:
            return {"error": "Category not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("description", required=False)
        data = parser.parse_args()

        category.description = data["description"] or category.description
        db.session.commit()
        return {"message": "Category updated"}, 200

    def delete(self, name):
        """Delete a category."""
        category = Category.query.filter_by(name=name).first()
        if not category:
            return {"error": "Category not found"}, 404

        db.session.delete(category)
        db.session.commit()
        return {"message": "Category deleted"}, 200
