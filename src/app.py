from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from activity_api import activity_bp
from category_api import category_bp
from user_api import user_bp
from log_api import log_bp
from report_api import report_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register Blueprints for each resource
app.register_blueprint(activity_bp, url_prefix="/activities")
app.register_blueprint(category_bp, url_prefix="/categories")
app.register_blueprint(user_bp, url_prefix="/users")
app.register_blueprint(log_bp, url_prefix="/logs")
app.register_blueprint(report_bp, url_prefix="/reports")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
