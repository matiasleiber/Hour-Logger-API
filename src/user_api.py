from flask_restful import Resource, reqparse
from models import db, User

class UserListResource(Resource):
    def get(self):
        """Retrieve all users."""
        users = User.query.all()
        return [{"username": user.username} for user in users], 200

    def post(self):
        """Create a new user."""
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
        return {"username": user.username}, 200

    def put(self, username):
        """Update a user's password."""
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
