import json
import secrets
from flask import Response, request, url_for
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.routing import BaseConverter

from constants import *
from models import *

class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class HourLoggerBuilder(MasonBuilder):

    def add_control_delete_category(self, name):
        self.add_control(
            "hlog:delete-category",
            url_for("categoryresource", name=name),
            method="DELETE",
            title="Delete this category"
        )
        
    def add_control_delete_activity(self, name, category):
        self.add_control(
            "hlog:delete-activity",
            url_for("activityresource", name=name, category=category),
            method="DELETE",
            title="Delete this activity"
        )
        
    def add_control_delete_user(self, username):
        self.add_control(
            "hlog:delete-user",
            url_for("userresource", username=username),
            method="DELETE",
            title="Delete user"
        )
        
    def add_control_delete_log(self, rid):
        self.add_control(
            "hlog:delete-log",
            url_for("logresource", rid=rid),
            method="DELETE",
            title="Delete log with certain rid"
        )
        
    def add_control_delete_report(self, rid):
        self.add_control(
            "hlog:delete-report",
            url_for("reportresource", rid=rid),
            method="DELETE",
            title="Delete report with certain rid"
        )

    def add_control_add_category(self):
        self.add_control(
            "hlog:add-category",
            url_for("categorylistresource"),
            method="POST",
            encoding="json",
            title="Add a new category",
            schema=Category.get_schema()
        )

    def add_control_add_activity(self, category):
        self.add_control(
            "hlog:add-activity",
            url_for("activitylistresource", category=category),
            method="POST",
            encoding="json",
            title="Add a new activity for this category",
            schema=Activity.get_schema()
        )
        
    def add_control_add_user(self):
        self.add_control(
            "hlog:add-user",
            url_for("userlistresource"),
            method="POST",
            encoding="json",
            title="Add a new user",
            schema=User.get_schema()
        )
    
    def add_control_add_log(self, username):
        self.add_control(
            "hlog:add-log",
            url_for("loglistresource", username=username),
            method="POST",
            encoding="json",
            title="Add a new log for this user",
            schema=Log.get_schema()
        )
    
    def add_control_add_report(self, username):
        self.add_control(
            "hlog:add-report",
            url_for("reportlistresource", username=username),
            method="POST",
            encoding="json",
            title="Add a new report for this user",
            schema=Report.get_schema()
        )

    def add_control_modify_category(self, name):
        self.add_control(
            "hlog:edit-category",
            url_for("categoryresource", name=name),
            method="PUT",
            encoding="json",
            title="Edit this category",
            schema=Category.get_schema()
        )
        
    def add_control_modify_activity(self, name, category):
        self.add_control(
            "hlog:edit-activity",
            url_for("activityresource", name=name, category=category),
            method="PUT",
            encoding="json",
            title="Edit activity from category",
            schema=Activity.get_schema()
        )
        
    def add_control_modify_user(self, username):
        self.add_control(
            "hlog:edit-user",
            url_for("userresource", username=username),
            method="PUT",
            encoding="json",
            title="Edit this user",
            schema=User.get_schema()
        )

    """
    def add_control_get_measurements(self, sensor):
        base_uri = url_for("api.measurementcollection", sensor=sensor)
        uri = base_uri + "?start={index}"
        self.add_control(
            "senhub:measurements",
            uri,
            isHrefTemplate=True,
            schema=self._paginator_schema()
        )

    @staticmethod
    def _paginator_schema():
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        props = schema["properties"]
        props["index"] = {
            "description": "Starting index for pagination",
            "type": "integer",
            "default": "0"
        }
        return schema
    """

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)

def page_key(*args, **kwargs):
    start = request.args.get("start", 0)
    return request.path + f"[start_{start}]"
    
def require_admin(func):
    def wrapper(*args, **kwargs):
        key_hash = ApiKey.key_hash(request.headers.get("Sensorhub-Api-Key", "").strip())
        db_key = ApiKey.query.filter_by(admin=True).first()
        if secrets.compare_digest(key_hash, db_key.key):
            return func(*args, **kwargs)
        raise Forbidden
    return wrapper

def require_sensor_key(func):
    def wrapper(self, sensor, *args, **kwargs):
        key_hash = ApiKey.key_hash(request.headers.get("Sensorhub-Api-Key").strip())
        db_key = ApiKey.query.filter_by(sensor=sensor).first()
        if db_key is not None and secrets.compare_digest(key_hash, db_key.key):
            return func(*args, **kwargs)
        raise Forbidden
    return wrapper


class SensorConverter(BaseConverter):
    
    def to_python(self, sensor_name):
        db_sensor = Sensor.query.filter_by(name=sensor_name).first()
        if db_sensor is None:
            raise NotFound
        return db_sensor
        
    def to_url(self, db_sensor):
        return db_sensor.name