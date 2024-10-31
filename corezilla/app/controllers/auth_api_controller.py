import http

from flask.views import MethodView
from flask_security import login_user
from flask_smorest import Blueprint
from flask_smorest.error_handler import ErrorSchema

from corezilla.app import db
from corezilla.app.models.User import User
from corezilla.app.schemas.user_schema import LoginUserRequest, RegisterUserRequest, UserResponseSchema

auth_api = Blueprint("auth", "auth", url_prefix="/api/auth", description="User authentication endpoints")


@auth_api.route("/login")
class AuthenticationApi(MethodView):
    @auth_api.arguments(LoginUserRequest, location="json", examples={
        "Login with Username": {
            "value": {
                "username": "leetify",
                "password": "hunter2!",
            },
        },
        "Login with Email": {
            "value": {
                "username": "user@example.invalid",
                "password": "hunter2!",
            }
        }
    })
    @auth_api.response(status_code=http.HTTPStatus.OK, schema=UserResponseSchema, example={"message":"Login successful"})
    @auth_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    @auth_api.alt_response(status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY, schema=ErrorSchema, success=False)
    def post(self, args):
        """
        Login a user with their username or email.

        Authenticate a user by their username or email, along with their password.
        """
        email_or_username = args.get("username_or_email")
        password = args.get("password")

        # Assuming User has 'username' and 'email' fields
        user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()

        if user and user.verify_password(password):
            login_user(user)
            return {'message': 'Login successful'}, http.HTTPStatus.OK
        return {
            'code': 400,
            'status': 'Bad Request',
            'message': 'Invalid credentials',
            'errors': {}
        }, http.HTTPStatus.BAD_REQUEST


@auth_api.route('/register')
class RegisterApi(MethodView):
    @auth_api.arguments(RegisterUserRequest, location="json", example={
        "username": "leetify",
        "email": "user@example.invalid",
        "password": "hunter2!",
        "confirm_password": "hunter2!",
    })
    @auth_api.response(status_code=http.HTTPStatus.CREATED, schema=UserResponseSchema, example = {"message": "User registered successfully"})
    @auth_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    @auth_api.alt_response(status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY, schema=ErrorSchema, success=False)
    def post(self, args):
        """
        Register a new user account.

        Create a new user account by providing the necessary details.
        """
        username = args.get("username")
        email = args.get("email")
        password = args.get("password")
        password_confirm = args.get("password_confirm")

        if password != password_confirm:
            return {
                'code': 400,
                'status': 'Bad Request',
                'message': 'Passwords do not match',
                'errors': {}
            }, http.HTTPStatus.BAD_REQUEST

        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            return {
                'code': 400,
                'status': 'Bad Request',
                'message': 'User already exists',
                'errors': {}
            }, http.HTTPStatus.BAD_REQUEST
        new_user = User(username=username, email=email, password=password)

        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User registered successfully'}, http.HTTPStatus.CREATED
