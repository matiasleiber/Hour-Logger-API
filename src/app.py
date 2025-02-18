from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from activity_api import activity_bp
from category_api import category_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register Blueprints for each resource
app.register_blueprint(activity_bp, url_prefix="/activities")
app.register_blueprint(category_bp, url_prefix="/categories")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
