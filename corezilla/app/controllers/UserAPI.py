import http

import flask_security
from flask.views import MethodView
from flask_login import current_user
from flask_security.utils import verify_and_update_password, login_user
from flask_smorest import Blueprint
from flask_smorest.error_handler import ErrorSchema

from corezilla.app import db
from corezilla.app.models.User import User
from corezilla.app.schemas.user_schema import UserSchema, UserSessionSchema

user_api = Blueprint("user", "user", url_prefix="/api/users", description="User operations")


@user_api.route("/")
class UserAPI(MethodView):
    @user_api.arguments(UserSessionSchema, as_kwargs=True)
    @user_api.response(http.HTTPStatus.CREATED, schema=UserSchema)
    @user_api.alt_response(http.HTTPStatus.FOUND, schema=UserSchema, success=True)
    @user_api.alt_response(http.HTTPStatus.CONFLICT, schema=ErrorSchema, success=False)
    def put(self, **kwargs):
        if current_user.is_authenticated:
            # If the user is already logged in, return their details
            user = User.query.get(current_user.user_id)
            if not user:
                return {
                    "code": http.HTTPStatus.NOT_FOUND,
                    "status": "error",
                    "message": "User not found",
                    "errors": {}
                }, http.HTTPStatus.NOT_FOUND
            return user, http.HTTPStatus.FOUND
        else:
            # Check if the username already exists
            existing_user = User.query.filter_by(username=kwargs.get("username")).first()
            if existing_user:
                return {
                    "code": http.HTTPStatus.CONFLICT,
                    "status": "error",
                    "message": "Username already exists",
                    "errors": {"username": "already exists"}
                }, http.HTTPStatus.CONFLICT

            # Create a new user with username and password
            user = User(username=kwargs.get("username"))
            user.set_password(kwargs.get("password"))  # Assuming `set_password` hashes the password
            db.session.add(user)
            db.session.commit()
            return user, http.HTTPStatus.CREATED


@user_api.route("/session")
class Session(MethodView):

    @user_api.arguments(UserSessionSchema, as_kwargs=True)
    @user_api.response(http.HTTPStatus.CREATED, schema=UserSchema)
    @user_api.alt_response(http.HTTPStatus.NO_CONTENT, schema=ErrorSchema, success=False)
    @user_api.alt_response(http.HTTPStatus.FOUND, schema=UserSchema, success=True)
    def put(self, **kwargs):
        """
        Create a new user session or return logged-in user details.
        """
        if current_user.is_authenticated:
            return current_user, http.HTTPStatus.FOUND
        else:
            # Authenticate user by username or email
            user = User.query.filter(
                (User.username == kwargs.get("username")) |
                (User.email == kwargs.get("username"))
            ).first()

            if user and verify_and_update_password(kwargs.get("password"), user):
                login_user(user)
                return user, http.HTTPStatus.CREATED
            else:
                return {
                    "code": http.HTTPStatus.NO_CONTENT,
                    "status": "error",
                    "message": "Invalid credentials",
                    "errors": {}
                }, http.HTTPStatus.NO_CONTENT


@user_api.route("/session/me")
class UserSession(MethodView):

    @user_api.response(http.HTTPStatus.FOUND, UserSchema)
    @user_api.alt_response(http.HTTPStatus.UNAUTHORIZED, schema=ErrorSchema, success=False)
    def get(self):
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
            if not user:
                return {
                    "code": http.HTTPStatus.NOT_FOUND,
                    "status": "error",
                    "message": "User not found",
                    "errors": {}
                }, http.HTTPStatus.NOT_FOUND
            return user, http.HTTPStatus.FOUND
        else:
            return {
                "code": http.HTTPStatus.UNAUTHORIZED,
                "status": "error",
                "message": "Unauthorized access",
                "errors": {}
            }, http.HTTPStatus.UNAUTHORIZED

    @user_api.response(http.HTTPStatus.NO_CONTENT)
    @user_api.alt_response(http.HTTPStatus.UNAUTHORIZED, schema=ErrorSchema, success=False)
    def delete(self):
        if current_user.is_authenticated:
            flask_security.logout_user()
            return '', http.HTTPStatus.NO_CONTENT
        else:
            return {
                "code": http.HTTPStatus.UNAUTHORIZED,
                "status": "error",
                "message": "Unauthorized access",
                "errors": {}
            }, http.HTTPStatus.UNAUTHORIZED
