from flask_restful import Resource, reqparse
from models import db, Activity, Category

class ActivityListResource(Resource):
    def get(self):
        """Retrieve all activities."""
        activities = Activity.query.all()
        return [{"name": act.name, "category": act.category_name, "description": act.description} for act in activities], 200

    def post(self):
        """Create a new activity."""
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True, help="Activity name is required")
        parser.add_argument("category_name", required=True, help="Category name is required")
        parser.add_argument("description", required=False)
        data = parser.parse_args()

        category = Category.query.filter_by(name=data["category_name"]).first()
        if not category:
            return {"error": "Category does not exist"}, 404

        activity = Activity(name=data["name"], category_name=data["category_name"], description=data["description"])
        db.session.add(activity)

        try:
            db.session.commit()
            return {"message": "Activity created successfully"}, 201
        except:
            db.session.rollback()
            return {"error": "Activity already exists"}, 409


class ActivityResource(Resource):
    def get(self, name, category):
        """Retrieve a single activity."""
        activity = Activity.query.filter_by(name=name, category_name=category).first()
        if not activity:
            return {"error": "Activity not found"}, 404
        return {"name": activity.name, "category": activity.category_name, "description": activity.description}, 200

    def put(self, name, category):
        """Update an activity."""
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
