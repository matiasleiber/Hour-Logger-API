from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKeyConstraint
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    username = db.Column(db.String(32), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    
    logs = db.relationship("Log", back_populates="user")
    time_reports = db.relationship("TimeReport", back_populates="user", passive_deletes=True)

class Category(db.Model):
    name = db.Column(db.String(32), primary_key=True, unique=True, nullable=False)
    description = db.Column(db.String(128), nullable=True)
    
    activities = db.relationship("Activity", back_populates="category", passive_deletes=True)

class Activity(db.Model):
    name = db.Column(db.String(32), primary_key=True, nullable=False)
    category_name = db.Column(db.String(32), db.ForeignKey("category.name", ondelete="CASCADE"), primary_key=True, nullable=False)
    description = db.Column(db.String(128), nullable=True)
    
    category = db.relationship("Category", back_populates="activities")
    logs = db.relationship("Log", back_populates="activity")

class Log(db.Model):
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.String(32), db.ForeignKey("user.username", ondelete="SET NULL"), nullable=True)
    activity_name = db.Column(db.String(32), nullable=True)
    activity_category = db.Column(db.String(32), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    comments = db.Column(db.String(128), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(
            ['activity_name', 'activity_category'],
            ['activity.name', 'activity.category_name'],
            ondelete="SET NULL"
        ), {}
    )
    
    user = db.relationship("User", back_populates="logs")
    activity = db.relationship("Activity", back_populates="logs")

class TimeReport(db.Model):
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.String(32), db.ForeignKey("user.username", ondelete="CASCADE"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship("User", back_populates="time_reports")
    
def populate_db():
    # Populate the database with sample data
    user1 = User(username="test1", password="password")
    user2 = User(username="test2", password="anotherpassword")
    
    category1 = Category(name="Work", description="Work-related activities")
    category2 = Category(name="Exercise", description="Exercising activities")
    
    activity1 = Activity(name="Coding", category_name="Work", description="Software development")
    activity2 = Activity(name="Gym", category_name="Exercise", description="Going to the gym")
    
    log1 = Log(
        user_id="test1", 
        activity_name="Coding", 
        activity_category="Work",
        start_time=datetime.strptime("2024-02-07 10:00:00", "%Y-%m-%d %H:%M:%S"), 
        end_time=datetime.strptime("2024-02-07 12:00:00", "%Y-%m-%d %H:%M:%S"), 
        comments="Worked on project X"
    )

    log2 = Log(
        user_id="test2", 
        activity_name="Gym", 
        activity_category="Exercise",
        start_time=datetime.strptime("2024-02-07 15:00:00", "%Y-%m-%d %H:%M:%S"), 
        end_time=datetime.strptime("2024-02-07 16:00:00", "%Y-%m-%d %H:%M:%S"), 
        comments="Went to the gym"
    )

    time_report1 = TimeReport(
        user_id="test1", 
        start_time=datetime.strptime("2024-02-07 09:00:00", "%Y-%m-%d %H:%M:%S"), 
        end_time=datetime.strptime("2024-02-07 17:00:00", "%Y-%m-%d %H:%M:%S")
    )

    time_report2 = TimeReport(
        user_id="test2", 
        start_time=datetime.strptime("2024-02-07 14:00:00", "%Y-%m-%d %H:%M:%S"), 
        end_time=datetime.strptime("2024-02-07 18:00:00", "%Y-%m-%d %H:%M:%S")
    )
    
    db.session.add_all([
        user1, user2, category1, category2,
        activity1, activity2, log1, log2, time_report1, time_report2
    ])
    db.session.commit()