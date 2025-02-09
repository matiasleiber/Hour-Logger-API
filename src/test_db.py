import os
import pytest
import tempfile
import time
from datetime import datetime
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from models import User, Log, Activity, Category, TimeReport
from models import app, db

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True
    
    ctx = app.app_context()
    ctx.push()
    db.create_all()
        
    yield db
    
    db.session.rollback()
    db.drop_all()
    db.session.remove()
    ctx.pop()
    os.close(db_fd)
    os.unlink(db_fname)

def _get_user():
    return User(
        username="test1",
        password="password1"
    )

def _get_log():
    return Log(
        user_id="test1", 
        activity_name="Coding", 
        activity_category="Work",
        start_time=datetime.strptime("2024-02-07 10:00:00", "%Y-%m-%d %H:%M:%S"), 
        end_time=datetime.strptime("2024-02-07 12:00:00", "%Y-%m-%d %H:%M:%S"), 
        comments="Worked on project X"
    )
    
def _get_category():
    return Category(
        name="Work",
        description="Work-related activities"
    )
    
def _get_activity():
    return Activity(
        name="Coding",
        category_name="Work",
        description="Software development"
    )
        
def _get_timereport():
    return TimeReport(
        user_id="test1", 
        start_time=datetime.strptime("2024-02-07 09:00:00", "%Y-%m-%d %H:%M:%S"), 
        end_time=datetime.strptime("2024-02-07 17:00:00", "%Y-%m-%d %H:%M:%S")
    )

def test_create_instances(db_handle):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that 
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    # Create everything
    user = _get_user()
    log = _get_log()
    category = _get_category()
    activity = _get_activity()
    timereport = _get_timereport()
    timereport.user = user
    log.user = user
    log.activity = activity
    activity.category = category
    db_handle.session.add(user)
    db_handle.session.add(log)
    db_handle.session.add(category)
    db_handle.session.add(activity)
    db_handle.session.add(timereport)
    db_handle.session.commit()
    
    # Check that everything exists
    assert User.query.count() == 1
    assert Log.query.count() == 1
    assert Category.query.count() == 1
    assert Activity.query.count() == 1
    assert TimeReport.query.count() == 1
    db_user = User.query.first()
    db_log = Log.query.first()
    db_category = Category.query.first()
    db_activity = Activity.query.first()
    db_timereport = TimeReport.query.first()
    
    # Check all relationships (both sides)
    assert db_log.user == db_user
    assert db_log.activity == db_activity
    assert db_activity.category == db_category
    assert db_timereport.user == db_user
    assert db_timereport in db_user.time_reports
    assert db_log in db_user.logs
    assert db_activity in db_category.activities
    assert db_log in db_activity.logs
    
def test_log_ondelete_user(db_handle):
    """
    Tests that log user is null after user is deleted
    """
    
    user = _get_user()
    log = _get_log()
    category = _get_category()
    activity = _get_activity()
    log.user = user
    log.activity = activity
    activity.category = category
    db_handle.session.add(log)
    db_handle.session.commit()
    db_handle.session.delete(user)
    db_handle.session.delete(activity)
    db_handle.session.commit()
    assert log.user is None
    assert log.activity is None
    
def test_activity_ondelete_category(db_handle):
    """
    Tests that if category is deleted, activity is also deleted
    """
    
    category = _get_category()
    activity = _get_activity()
    activity.category = category
    db_handle.session.add(activity)
    db_handle.session.commit()
    assert Activity.query.count() == 1
    db_handle.session.delete(category)
    db_handle.session.commit()
    assert Activity.query.count() == 0
    
def test_timereport_ondelete_user(db_handle):
    """
    Tests that if user is deleted, timereport is also deleted
    """
    
    user = _get_user()
    timereport = _get_timereport()
    timereport.user = user
    db_handle.session.add(timereport)
    db_handle.session.commit()
    assert TimeReport.query.count() == 1
    db_handle.session.delete(user)
    db_handle.session.commit()
    assert TimeReport.query.count() == 0
    
def test_user_columns(db_handle):
    """
    Tests the types and restrictions of user columns. Username must be unique and username and password are mandatory.
    """
    
    user_1 = _get_user()
    user_2 = _get_user()
    db_handle.session.add(user_1)
    db_handle.session.add(user_2)    
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    user = _get_user()
    user.username = None
    db_handle.session.add(user)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    user = _get_user()
    user.password = None
    db_handle.session.add(user)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
        
def test_log_columns(db_handle):
    """
    Tests the types and restrictions of log columns. Starttime and endtime are mandatory and they must be DateTime.
    """
    
    log = _get_log()
    log.start_time = None
    db_handle.session.add(log)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    log = _get_log()
    log.end_time = None
    db_handle.session.add(log)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    log = _get_log()
    log.start_time = time.time()
    db_handle.session.add(log)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    log = _get_log()
    log.end_time = time.time()
    db_handle.session.add(log)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
def test_category_columns(db_handle):
    """
    Tests the types and restrictions of category columns. Name must be unique.
    """
    
    category_1 = _get_category()
    category_2 = _get_category()
    db_handle.session.add(category_1)
    db_handle.session.add(category_2)    
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
def test_activity_columns(db_handle):
    """
    Tests the types and restrictions of activity columns. Name and category combination must be unique.
    """
    
    activity_1 = _get_activity()
    activity_2 = _get_activity()
    db_handle.session.add(activity_1)
    db_handle.session.add(activity_2)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
def test_timereport_columns(db_handle):
    """
    Tests the types and restrictions of activity columns. Starttime and endtime are mandatory and they must be DateTime. User_id is mandatory.
    """
    
    timereport = _get_timereport()
    timereport.user_id = None
    db_handle.session.add(timereport)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    timereport = _get_timereport()
    timereport.start_time = None
    db_handle.session.add(timereport)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    timereport = _get_timereport()
    timereport.end_time = None
    db_handle.session.add(timereport)
    with pytest.raises(IntegrityError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    timereport = _get_timereport()
    timereport.start_time = time.time()
    db_handle.session.add(timereport)
    with pytest.raises(StatementError):
        db_handle.session.commit()
    
    db_handle.session.rollback()
    
    timereport = _get_timereport()
    timereport.end_time = time.time()
    db_handle.session.add(timereport)
    with pytest.raises(StatementError):
        db_handle.session.commit()