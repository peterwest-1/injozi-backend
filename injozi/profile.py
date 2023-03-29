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

profile = Blueprint(
    "profile",
    __name__,
)
profile_logger = get_logger(__name__)
from injozi.models import Profile, User


@profile.route("/api/v1/profiles", methods=["POST"])
@jwt_required()
def create_profile():
    """
    Creates a new profile for a user.
    """

    # TODO: Validate the profile information
    profile_information = request.get_json()
    user_id = get_jwt_identity()

    new_profile = Profile(
        id_user=user_id,
        name=profile_information["name"],
        surname=profile_information["surname"],
        phone=profile_information["phone"],
    )
    new_profile.save()
    profile_logger.info(f"Profile for user {user_id} created successfully")
    return jsonify({"message": "Profile created successfully"}), 201


@profile.route("/api/v1/profiles", methods=["GET"])
def get_profiles():
    """
    Retrieves all profiles from the database.
    """

    profiles = Profile.objects()
    return jsonify(profiles), 200


@profile.route("/api/v1/profiles/<id>", methods=["GET"])
def get_profile_by_id(id):
    """
    Retrieves a profile with a specific ID from the database.
    """
    profile = Profile.objects(id=id).first()
    return jsonify(profile), 200


@profile.route("/api/v1/users/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """
    Updates a user's information.
    """
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "You are not authorized to update this user"}), 401

    user = User.objects(id=user_id).first()
    user.update(**request.get_json())
    profile_logger.info(f"User {user_id} updated successfully")
    return jsonify({"message": "User updated successfully"}), 200


@profile.route("/api/v1/users/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    """
    Deletes a user from the database.
    """
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "You are not authorized to delete this user"}), 401

    user = User.objects(id=user_id).first()
    user.delete()
    profile_logger.info(f"User {user_id} deleted successfully")
    return jsonify({"message": "User deleted successfully"}), 200
