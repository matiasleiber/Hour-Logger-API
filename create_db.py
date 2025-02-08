from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from datetime import datetime

from src.models import populate_db
from src.models import app, db
from src.models import Category

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        populate_db()
        
    print("Database tables created and populated successfully.")
