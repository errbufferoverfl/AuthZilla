from corezilla.config.default import Configuration, APP_DIR


class DevConfiguration(Configuration):
    """
    The development configuration for this Flask application.
    """

    """
    Project Details
    These are used to pre-fill the Jinja templates.
    """
    TITLE = "AuthZilla - Development"
    DATABASE_NAME = APP_DIR / "dev.db"

    @property
    def SQLALCHEMY_DATABASE_URI(self):  # noqa
        return f"sqlite:///{self.DATABASE_NAME}"

    """Flask Configuration"""
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = True

    """Flask-Security Configuration"""
    SECURITY_PASSWORD_HASH = "plaintext"  # Store passwords as plain text in development
    SECURITY_PASSWORD_SALT = None  # No salt needed for plain text storage
