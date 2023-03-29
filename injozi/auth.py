from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import Blueprint, Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_mongoengine import MongoEngine

from injozi.logger import get_logger

authentication = Blueprint(
    "authentication",
    __name__,
)

authentication_logger = get_logger(__name__)
from injozi.models import Profile, User

ph = PasswordHasher()


@authentication.route("/api/v1/auth/register", methods=["POST"])
def register():
    """
    Registers a new user.
    """
    user = request.get_json()

    authentication_logger.info(f'Registering user {user["email"]}')

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
        authentication_logger.info(f'User {user["email"]} created successfully')
        return jsonify({"message": "User created successfully"}), 201


@authentication.route("/api/v1/auth/login", methods=["POST"])
def login():
    """
    Logs in a user.
    """

    login_user = request.get_json()

    user_from_db = User.objects(email=login_user["email"]).first()

    if user_from_db:
        try:
            isValid = ph.verify(user_from_db["password"], login_user["password"])
        except VerifyMismatchError:
            isValid = False

        if isValid:
            authentication_logger.info(
                f'User {login_user["email"]} logged in successfully'
            )
            access_token = create_access_token(identity=user_from_db["email"])
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"message": "The email or password is incorrect"}), 401
    return jsonify({"message": "The email or password is incorrect"}), 401
