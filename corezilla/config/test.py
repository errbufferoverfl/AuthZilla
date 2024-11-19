from corezilla.config.default import Configuration, APP_DIR


class TestConfiguration(Configuration):
    """
    The development configuration for this Flask application.
    """

    """
    Project Details
    These are used to pre-fill the Jinja templates.
    """
    TITLE = "AuthZilla - Testing"
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing

    """SQLAlchemy Configuration"""
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Use an in-memory database for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    """Flask Configuration"""
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = True

    """Flask-Security Configuration"""
    SECURITY_PASSWORD_HASH = "plaintext"  # Store passwords as plain text in development
    SECURITY_PASSWORD_SALT = None  # No salt needed for plain text storage