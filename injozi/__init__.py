import datetime
import os

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_mongoengine import MongoEngine

from injozi.logger import get_logger


# Create the Flask application
app = Flask(__name__)

# Get the environment variables
database_host = os.environ.get("DATABASE_HOST", False)
database_name = os.environ.get("DATABASE_NAME", False)

app.config["MONGODB_SETTINGS"] = {
    "host": database_host,
}

# Initialize the database
db = MongoEngine(app)

from injozi.models import User, Profile

# Initialize the JWT manager
jwt = JWTManager(app)
jwt_secret = os.environ.get("JWT_SECRET", False)

app.config["JWT_SECRET_KEY"] = jwt_secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)


# Register the routes
from injozi.auth import authentication
from injozi.profile import profile

app.register_blueprint(authentication)
app.register_blueprint(profile)


# Index route
@app.route("/")
def hello_world():
    return "Injozi Backend"
