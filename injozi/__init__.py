import datetime
import os

import yaml
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_mongoengine import MongoEngine

database_host = os.environ.get("DATABASE_HOST", False)
database_name = os.environ.get("DATABASE_NAME", False)

jwt_secret = os.environ.get("JWT_SECRET", False)

ph = PasswordHasher()

app = Flask(__name__)

app.config["MONGODB_SETTINGS"] = {
    "host": database_host,
    "db": database_name,
}

db = MongoEngine(app)

jwt = JWTManager(app)

app.config["JWT_SECRET_KEY"] = jwt_secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)


class Profile(db.Document):
    id_user = db.StringField(required=True)
    name = db.StringField()
    surname = db.StringField()
    phone = db.StringField()
    created = db.DateTimeField(default=datetime.datetime.now())
    updated = db.DateTimeField(default=datetime.datetime.now())


class User(db.Document):
    email = db.StringField(required=True, unique=True)
    password = db.StringField(required=True, min_length=6)
    created = db.DateTimeField(default=datetime.datetime.now())
    updated = db.DateTimeField(default=datetime.datetime.now())


@app.route("/")
def hello_world():
    return "Injozi Backend"


@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    user = request.get_json()
    user["password"] = ph.hash(user["password"])

    user_found = User.objects(email=user["email"]).first()

    if user_found:
        return jsonify({"message": "email already exists"}), 409
    else:
        new_user = User(
            email=user["email"],
            password=user["password"],
        )
        new_user.save()
        return jsonify({"message": "User created successfully"}), 201


@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    login_user = request.get_json()
    user_from_db = User.objects(email=login_user["email"]).first()

    if user_from_db:
        try:
            isValid = ph.verify(user_from_db["password"], login_user["password"])
        except VerifyMismatchError:
            isValid = False

        if isValid:
            access_token = create_access_token(identity=user_from_db["email"])
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"message": "The email or password is incorrect"}), 401
    return jsonify({"message": "The email or password is incorrect"}), 401
