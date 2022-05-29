from flask import jsonify
from flaskr.models import User
from flask_jwt_extended import (
    create_access_token,
    current_user,
    jwt_required,
    JWTManager,
)

jwt = JWTManager()

# Register a callback function that takes whatever object is passed
# as identity when creating JWTs and convert it to JSON serializable object
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


# Register a callback function that loads user from db when successful route
# is accessed.
#
# Returns Python object for successful lookup, or None if lookup failed!
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


# Register a callback function when token is unauthorized
@jwt.unauthorized_loader
def invalid_token_callback(expired_token):
    return jsonify(error="Gotta /login and get a new token, dude"), 500


def init_app(app):
    app.config[
        "JWT_SECRET_KEY"
    ] = "this is the config for jwt secret keyyyyy"  # Change this!
    jwt.init_app(app)
