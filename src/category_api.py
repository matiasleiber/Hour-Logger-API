from flask_restful import Resource, reqparse
from models import db, Category

class CategoryListResource(Resource):
    def get(self):
        """Retrieve all categories."""
        categories = Category.query.all()
        return [{"name": cat.name, "description": cat.description} for cat in categories], 200

    def post(self):
        """Create a new category."""
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
        return {"name": category.name, "description": category.description}, 200

    def put(self, name):
        """Update a category's description."""
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
