import datetime
import datetime as dt
import secrets
import zlib

from sqlalchemy.ext.mutable import MutableDict
from xid import Xid

from corezilla.app import db


class ClientMetadata(db.Model):
    """A model representing metadata information for a client application.

    This model stores metadata that provides descriptive details about a client.
    The `metadata_blob` field is a JSO`N object that includes key
    attributes like the description, logo, terms of service (TOS), and various
    contact URLs relevant to the app's policies and contacts.

    Attributes:
        id (int): The primary key identifier for the metadata entry.
        client_id (str): Foreign key that associates this metadata entry with a
            specific client in the `client` table.
        metadata_blob (dict): A JSON object containing metadata fields that
            describe the application.

    The `metadata_blob` JSON structure provides the following fields:
        - "description" (str): A brief description of the application.
        - "logo" (str): The URL path to the application’s logo image.
        - "tos" (str): The URL to the application’s Terms of Service (TOS).
        - "privacy_policy" (str): The URL to the application’s Privacy Policy.
        - "security_contact" (str): The email address for security-related inquiries.
        - "privacy_contact" (str): The email address for privacy-related inquiries.

    Example:
        The `metadata_blob` JSON may look like the following:
        ```json
        {
            "description": "A sample app providing example services",
            "logo": "/images/sample_logo.png",
            "tos": "https://example.com/terms",
            "privacy_policy": "https://example.com/privacy",
            "security_contact": "security@example.com",
            "privacy_contact": "privacy@example.com"
        }
        ```
    Table:
        client_metadata

    Columns:
        id (Integer): Autoincrementing primary key for metadata entries.
        client_id (String): Foreign key linking to the `client` table.
        metadata_blob (JSON): A JSON field containing application metadata.
    """

    __tablename__ = "client_metadata"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    client_id = db.Column(db.String, db.ForeignKey("client.id"), nullable=False)
    metadata_blob = db.Column(MutableDict.as_mutable(db.JSON), nullable=False)


class ClientConfiguration(db.Model):
    """A model representing the technical configuration details for a client.

    This model stores configuration data that defines the technical setup of
    a client application, including OpenID Connect (OIDC) compliance, CORS settings,
    token handling, and URI specifications. The configuration is versioned,
    allowing each client to have multiple configurations over time, with new
    versions automatically incremented for each client.

    Attributes:
        id (int): The primary key identifier for the configuration entry.
        client_id (str): Foreign key that associates this configuration entry with a
            specific client in the `client` table.
        version (int): An automatically incremented version number for each
            configuration specific to the client.
        configuration_blob (dict): A JSON object containing configuration fields
            that outline the technical setup of the client.
        created_at (datetime): The timestamp when the configuration entry was created.

    The `configuration_blob` JSON structure provides the following fields:
        - "oidc_conformant" (bool): Indicates if the client conforms to OpenID Connect (OIDC) standards.
        - "sender_constrained" (bool): Specifies if sender-constraining is enabled for the client.
        - "token_endpoint_auth_method" (str): The method used for token endpoint authentication.
        - "uris" (dict): A nested JSON object defining URIs used in client interactions:
            - "app_login_uri" (str): The URI where the app’s login page is located.
            - "redirect_uris" (list): List of URIs where the client can be redirected after login.
            - "logout_uris" (list): List of URIs where the client can be redirected after logout.
            - "web_origins" (list): List of allowed web origins for client operations.
        - "cors" (dict): Cross-Origin Resource Sharing (CORS) configuration for the client:
            - "is_enabled" (bool): Whether CORS is enabled for the client.
            - "allowed_origins" (list): List of allowed origins for cross-origin requests.
            - "fallback_url" (str): The fallback URL for CORS requests.
        - "refresh" (dict): Settings related to the client’s refresh token configuration:
            - "refresh_token_rotation_enabled" (bool): Indicates if token rotation is enabled.
            - "rotation_overlap_period" (int): Duration of overlap period for token rotation.
            - "idle_refresh_token_lifetime_enabled" (bool): Indicates if idle lifetime is enforced.
            - "idle_refresh_token_lifetime" (int): The lifetime in seconds for an idle refresh token.
            - "maximum_refresh_token_lifetime_enabled" (bool): Indicates if max lifetime is enforced.
            - "maximum_refresh_token_lifetime" (int): The maximum lifetime in seconds for a refresh token.
        - "jwt" (dict): JSON Web Token (JWT) settings:
            - "algorithm" (str): Algorithm used for signing JWT tokens, typically "RS256".

    Example:
        The `configuration_blob` JSON might look like the following:
        ```json
        {
            "oidc_conformant": true,
            "sender_constrained": true,
            "token_endpoint_auth_method": "authorization_code",
            "uris": {
                "app_login_uri": "https://example.com",
                "redirect_uris": ["https://example.com", "https://login.example.com"],
                "logout_uris": ["https://example.com/logout", "https://login.example.com/logout"],
                "web_origins": ["https://example.com", "https://resources.example.com"]
            },
            "cors": {
                "is_enabled": true,
                "allowed_origins": ["https://example.com", "https://anotherexample.invalid"],
                "fallback_url": "https://example.com"
            },
            "refresh": {
                "refresh_token_rotation_enabled": false,
                "rotation_overlap_period": 0,
                "idle_refresh_token_lifetime_enabled": false,
                "idle_refresh_token_lifetime": 1296000,
                "maximum_refresh_token_lifetime_enabled": false,
                "maximum_refresh_token_lifetime": 2592000
            },
            "jwt": {
                "algorithm": "RS256"
            }
        }
        ```

    Table:
        client_configuration

    Columns:
        id (Integer): Autoincrementing primary key for configuration entries.
        client_id (String): Foreign key linking to the `client` table.
        version (Integer): Version number for the client configuration.
        configuration_blob (JSON): A JSON field containing configuration details.
        created_at (DateTime): Timestamp indicating when the configuration was created.
    """

    __tablename__ = "client_configuration"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    client_id = db.Column(db.String, db.ForeignKey("client.id"), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    configuration_blob = db.Column(MutableDict.as_mutable(db.JSON), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.now(dt.UTC), nullable=False)

    def __init__(self, client_id, configuration_blob):
        """Initializes a new client configuration entry with an auto-incremented version.

        Args:
            client_id (str): The client ID to associate with this configuration entry.
            configuration_blob (dict): The JSON object containing configuration settings.

        This initializer queries the maximum existing version for the client and sets
        the new entry to one version higher.
        """
        self.client_id = client_id

        # Define default configuration settings
        default_configuration = {
            "oidc_conformant": True,
            "sender_constrained": False,
            "token_endpoint_auth_method": "client_secret_basic",
            "cors": {
                "is_enabled": False
            },
            "jwt": {
                "algorithm": "RS256"
            },
        }
        # Merge provided configuration with defaults
        if configuration_blob is None:
            configuration_blob = {}
        self.configuration_blob = {**default_configuration, **configuration_blob}

        self.configuration_blob = configuration_blob

        max_version = db.session.query(db.func.max(ClientConfiguration.version)).filter_by(client_id=client_id).scalar()
        self.version = (max_version or 0) + 1


class Client(db.Model):
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Internal auto-incrementing ID
    client_id = db.Column(db.String(30), unique=True, nullable=False, index=True)  # Public client ID
    client_name = db.Column(db.String(255), nullable=True, default="New Client")
    client_uri = db.Column(db.String, nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    app_type = db.Column(db.String, nullable=False, default="web")

    _client_secret = db.Column(db.String, nullable=True)

    # Foreign key to the User model
    user_id = db.Column(db.Integer, db.ForeignKey("user.fs_uniquifier"), nullable=False)

    # Relationship with the User model (one-to-many)
    owner = db.relationship("User", back_populates="clients")

    # One-to-many relationship with InstallationRecords
    installation_records = db.relationship(
        "InstallationRecords",
        back_populates="client",
        cascade="all, delete-orphan"
    )

    client_configurations = db.relationship("ClientConfiguration", lazy=True, backref="client")
    client_metadata = db.relationship("ClientMetadata", uselist=False, backref="client")

    def __init__(self, owner, name=None, app_type="web", is_public=False):
        # Generate public `client_id` in the format `CLIENT-$XID`
        self.client_id = f"cl-{Xid().string()}"
        self.client_name = name or "New Client"

        self.is_public = is_public
        self.app_type = app_type
        self.owner = owner

    @property
    def client_secret(self):
        if self._client_secret is None:
            # Generate and set the client_secret if it has not been initialized
            self._client_secret = self._generate_client_secret()
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value):
        # Allows setting client_secret explicitly if needed
        self._client_secret = value

    @staticmethod
    def _generate_client_secret():
        prefix = "AZL-CS"

        # Generate a high-entropy random string (e.g., 32 characters)
        random_part = secrets.token_urlsafe(128)

        # Create a checksum of the prefix and random part
        checksum_input = f"{prefix}_{random_part}".encode('utf-8')
        checksum = zlib.crc32(checksum_input) & 0xffffffff

        # Format the client secret with the prefix, random part, and checksum
        client_secret = f"{prefix}-{random_part}-{checksum:08x}"  # Hexadecimal format for checksum
        return client_secret

