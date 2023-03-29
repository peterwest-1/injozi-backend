import datetime
import os


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
}

db = MongoEngine(app)


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


jwt = JWTManager(app)

app.config["JWT_SECRET_KEY"] = jwt_secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)


@app.route("/")
def hello_world():
    return "Injozi Backend"


@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    user = request.get_json()
    user["password"] = ph.hash(user["password"])

    user_found = User.objects(email=user["email"]).first()

    if user_found:
        return jsonify({"message": "Email already exists"}), 409
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


@app.route("/api/v1/profiles", methods=["POST"])
@jwt_required()
def create_profile():
    profile_information = request.get_json()
    user_id = get_jwt_identity()
    new_profile = Profile(
        id_user=user_id,
        name=profile_information["name"],
        surname=profile_information["surname"],
        phone=profile_information["phone"],
    )
    new_profile.save()
    return jsonify({"message": "Profile created successfully"}), 201


@app.route("/api/v1/profiles", methods=["GET"])
def get_profiles():
    profiles = Profile.objects()
    return jsonify(profiles), 200


@app.route("/api/v1/profiles/<id>", methods=["GET"])
def get_profile_by_id(id):
    profile = Profile.objects(id=id).first()
    return jsonify(profile), 200


# MARK: PUT or PATCH
@app.route("/api/v1/users/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "You are not authorized to update this user"}), 401

    user = User.objects(id=user_id).first()
    user.update(**request.get_json())
    return jsonify({"message": "User updated successfully"}), 200


@app.route("/api/v1/users/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "You are not authorized to delete this user"}), 401

    user = User.objects(id=user_id).first()
    user.delete()
    return jsonify({"message": "User deleted successfully"}), 200
