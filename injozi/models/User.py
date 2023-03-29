import datetime
from flask_mongoengine import MongoEngine as db


class User(db.Document):
    email = db.StringField(required=True, unique=True)
    password = db.StringField(required=True, min_length=6)
    created = db.DateTimeField(default=datetime.datetime.now())
    updated = db.DateTimeField(default=datetime.datetime.now())
