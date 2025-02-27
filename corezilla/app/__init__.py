import logging
from uuid import uuid4

from flask import Flask, g
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_principal import Principal, Identity, AnonymousIdentity, RoleNeed, Permission, identity_loaded, UserNeed
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions without app context
api = Api()
db = SQLAlchemy()
marshmallow = Marshmallow()
migrate = Migrate()
security = Security()
principals = Principal()
login_manager = LoginManager()

# Define permissions
user_role_permission = Permission(RoleNeed("User"))


def create_app(config_object) -> Flask:
    """
    Flask application factory pattern that configures and returns the app.

    Args:
        config_object (Config): The configuration object to use

    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__.split('.')[0], template_folder=config_object.TEMPLATE_FOLDER, static_folder=config_object.STATIC_FOLDER)
    app.config.from_object(config_object)
    app.url_map.strict_slashes = True

    @app.context_processor
    def inject_html_metadata():
        return {
            "title": config_object.TITLE,
            "description": config_object.DESCRIPTION,
            "authors": config_object.AUTHORS,
            "tags": config_object.TAGS,
            "lang": config_object.LANG,
        }

    # Register extensions and blueprints
    with app.app_context():
        register_extensions(app)
        register_blueprints(app)

    # Set request id for each request
    app.before_request(before_request_handler)

    # Set up identity loaded signals for role-based permissions
    identity_loaded.connect_via(app)(on_identity_loaded)

    return app


def on_identity_loaded(sender, identity):
    """
    Assign user roles and needs when the identity is loaded.
    Args:
        sender (Flask): The application instance
        identity (Identity): The identity of the current user
    """
    if not isinstance(identity, AnonymousIdentity) and hasattr(identity, 'id') and identity.id is not None:
        identity.provides.add(UserNeed(identity.id))

        # Assign roles to the current user, if any
        if hasattr(current_user, 'roles') and current_user.roles:
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role._name))

        logging.debug(f"Identity loaded for user: {identity.id}")


def register_extensions(app: Flask) -> None:
    """
    Initialize Flask extensions.

    Args:
        app (Flask): The Flask application instance
    """

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    marshmallow.init_app(app)
    api.init_app(app)

    # Flask-Security initialization
    from corezilla.app.models.User import User
    from corezilla.app.models.User import Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore, register_blueprint=True)

    # LoginManager setup
    login_manager.init_app(app)

    # Principal setup
    principals.init_app(app)

    logging.info("Extensions registered successfully")


def register_blueprints(app: Flask):
    """
    Register Flask blueprints (API and web routes).

    Args:
        app (Flask): The Flask application instance
    """
    from corezilla.app.controllers.AuthenticationApi import auth_api
    from corezilla.app.controllers.AuthorizationApi import oauth_api
    from corezilla.app.controllers.UserAPI import user_api
    from corezilla.app.controllers.ClientsApi import client_api

    from corezilla.app.controllers.WebController import core_web

    # Register core, user, and auth blueprints
    api.register_blueprint(auth_api)
    api.register_blueprint(oauth_api)

    if app.config.get("ENABLE_SAML"):
        pass

    if app.config.get("ENABLE_OIDC"):
        pass

    api.register_blueprint(user_api)
    api.register_blueprint(client_api)

    app.register_blueprint(core_web)

    logging.info("Blueprints registered successfully")


@login_manager.user_loader
def load_user(user_id):
    """
    Load the user from the database by their user ID.

    Args:
        user_id (str): The user's ID

    Returns:
        User: The user object
    """
    from corezilla.app.models.User import User
    return User.query.get(user_id)


def before_request_handler():
    """
    Assign a unique request ID for every request.
    """
    g.request_id = uuid4()
    logging.debug(f"Request ID: {g.request_id}")
