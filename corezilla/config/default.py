import secrets
from pathlib import Path

# Set BASEDIR using PathLib
BASEDIR = Path(__file__).resolve().parent

# Set TEMPLATES_DIR and STATIC_DIR using PathLib
APP_DIR = BASEDIR.parent
TEMPLATES_DIR = BASEDIR.parent / 'app' / 'views' / 'templates'
STATIC_DIR = BASEDIR.parent / 'app' / 'views' / 'static'


class Configuration(object):
    """
    The default configuration for this Flask application.
    """

    """Project Details (used in Jinja templates)"""
    TITLE = "AuthZilla"
    DESCRIPTION = "A not very good OAuth2.1 authorisation server."
    AUTHORS = ["errbufferoverfl", ]
    TAGS = ["development", "security"]
    LANG = "en"

    """Flask Configuration"""
    DEBUG = False
    TESTING = False
    THREADS_PER_PAGE = 8

    # Set the template and static directories
    TEMPLATE_FOLDER = TEMPLATES_DIR
    STATIC_FOLDER = STATIC_DIR

    """Security Configuration"""
    ADMINS = frozenset()
    SECURITY_PASSWORD_SALT = secrets.token_bytes(128)
    SECRET_KEY = secrets.token_bytes(128)
    SESSION_COOKIE_SAMESITE = "strict"
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False

    """Database Configuration"""
    DATABASE_NAME = APP_DIR / "app.db"

    @property
    def SQLALCHEMY_DATABASE_URI(self):  # noqa
        return f"sqlite:///{self.DATABASE_NAME}"

    """API Meta Configuration"""
    API_TITLE = f"{TITLE} - API Reference"
    API_VERSION = "1.0"

    """Open API Configuration"""
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_JSON_PATH = "api-spec.json"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = (
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    OPENAPI_RAPIDOC_PATH = "/rapidoc"
    OPENAPI_RAPIDOC_URL = "https://unpkg.com/rapidoc/dist/rapidoc-min.js"
    OPENAPI_RAPIDOC_CONFIG = {
        "theme": "light",
        "layout": "column",
        "schema-style": "table",
        "schema-hide-read-only": "never",
        "default-schema-tab": "example",
    }
