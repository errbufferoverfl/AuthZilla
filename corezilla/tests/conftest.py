import http
import secrets
from pydoc import describe

import flask_login
import pytest
from flask import url_for

from corezilla.app import create_app, db, login_manager
from corezilla.app.models import Client, ClientMetadata, ClientConfiguration
from corezilla.app.models.User import User
from corezilla.config.test import TestConfiguration


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfiguration)
    with app.app_context():
        db.create_all()  # Create tables in the test database
        yield app
        db.drop_all()  # Drop all tables after the test


@pytest.fixture
def db_session(app):
    """Create a new database session for a test."""
    with app.app_context():
        yield db.session
        db.session.rollback()  # Roll back any changes after the test


@pytest.fixture
def user(db_session):
    """A fixture that creates and returns a test user object."""
    user = User(username='test_user', email='user@example.invalid', password='password')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def oauth_client(db_session, user):
    """A fixture that creates and returns a test client object."""
    client = Client(owner=user, name="Test Client")
    db_session.add(client)
    db_session.commit()

    client_metadata = ClientMetadata(
        client_id=client.id,
        metadata_blob={"description": "A client created for testing."}
    )

    client_configuration = ClientConfiguration(
        client_id=client.id,
        configuration_blob={"oidc_conformant": True,
                            "sender_constrained": True,
                            "token_endpoint_auth_method": "authorization_code",
                            "uris": {
                                "app_login_uri": "https://example.com",
                                "redirect_uris": ["https://example.com", "https://login.example.com"],
                                "logout_uris": ["https://example.com/logout", "https://login.example.com/logout"],
                                "web_origins": ["https://example.com", "https://resources.example.com"]
                            },
                            "cors": {
                                "is_enabled": True,
                                "allowed_origins": ["https://example.com", "https://anotherexample.invalid"],
                                "fallback_url": "https://example.com"
                            },
                            "refresh": {
                                "refresh_token_rotation_enabled": False,
                                "rotation_overlap_period": 0,
                                "idle_refresh_token_lifetime_enabled": False,
                                "idle_refresh_token_lifetime": 1296000,
                                "maximum_refresh_token_lifetime_enabled": False,
                                "maximum_refresh_token_lifetime": 2592000
                            },
                            "jwt": {
                                "algorithm": "RS256"
                            }}
    )

    db_session.add_all([client_metadata, client_configuration])
    db_session.commit()
    return client


@pytest.fixture
def auth_config(app):
    """Mock Flask app configuration for authorization codes."""
    app.config["ISSUER_NAME"] = "https://authzilla.example.com"
    app.config["AUDIENCE"] = "https://example.invalid"
    app.config["AUTH_CODE_EXPIRY_SECONDS"] = 600  # 10 minutes
    app.config["AUTH_CODE_SECRET_KEY"] = secrets.token_bytes(32)  # Secure key
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config["ACCESS_TOKEN_EXPIRE_MINUTES"] = 60
    app.config["REFRESH_TOKEN_EXPIRE_MINUTES"] = 43200
    app.config["SECRET_KEY"] = "super-secret-key"  # Secure in production
    return app.config