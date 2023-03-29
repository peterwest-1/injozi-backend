import datetime

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
from pymongo import MongoClient

with open("./config.yaml", "r") as file:
    config = yaml.safe_load(file)

# access values from the configuration file
database_username = config["database"]["username"]
database_password = config["database"]["password"]

jwt_secret = config["jwt"]["secret"]


client = MongoClient(
    f"mongodb+srv://{database_username}:{database_password}@injozi-cluster.t2ykxiu.mongodb.net/?retryWrites=true&w=majority"
)
db = client["injozi"]
users_collection = db["users"]

ph = PasswordHasher()

app = Flask(__name__)
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

    doc = users_collection.find_one({"email": user["email"]})
    if not doc:
        users_collection.insert_one(
            {
                "email": user["email"],
                "password": user["password"],
                "created": datetime.datetime.now(),
                "updated": datetime.datetime.now(),
            }
        )
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"message": "email already exists"}), 409


@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    login_user = request.get_json()
    user_from_db = users_collection.find_one({"email": login_user["email"]})

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
