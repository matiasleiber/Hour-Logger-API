from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from models import db
from activity_api import ActivityResource, ActivityListResource
from category_api import CategoryResource, CategoryListResource
from user_api import UserResource, UserListResource
from log_api import LogResource, LogListResource
from report_api import ReportResource, ReportListResource

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
api = Api(app)

# Registering API resources
api.add_resource(ActivityListResource, "/activities/")
api.add_resource(ActivityResource, "/activities/<string:name>/<string:category>")

api.add_resource(CategoryListResource, "/categories/")
api.add_resource(CategoryResource, "/categories/<string:name>")

api.add_resource(UserListResource, "/users/")
api.add_resource(UserResource, "/users/<string:username>")

api.add_resource(LogListResource, "/logs/")
api.add_resource(LogResource, "/logs/<int:rid>")

api.add_resource(ReportListResource, "/reports/")
api.add_resource(ReportResource, "/reports/<int:rid>")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
