import datetime as dt

from sqlalchemy.ext.mutable import MutableDict
from xid import Xid

from corezilla.app import db


class AuthenticationConnectionMetadata(db.Model):
    """A model representing metadata for an authentication connection.

    This model stores metadata such as SAML metadata XML or OIDC discovery documents.

    Attributes:
     - id (int): The primary key identifier for the metadata entry.
     - connection_id (str): Foreign key linking to the `authentication_connection` table.
     - metadata_blob (dict): A JSON field containing metadata.
     - created_at (datetime): Timestamp indicating when the metadata entry was created.
    """

    __tablename__ = "authentication_connection_metadata"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    connection_id = db.Column(db.String(64), db.ForeignKey("authentication_connection.connection_id"), nullable=False, index=True)
    metadata_blob = db.Column(MutableDict.as_mutable(db.JSON), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.now(dt.UTC), nullable=False)

    def __init__(self, connection_id, metadata_blob=None):
        """Initializes metadata for an authentication connection.

        Args:
            connection_id (str): The authentication connection ID.
            metadata_blob (dict): JSON object containing metadata.
        """
        self.connection_id = connection_id

        # Default metadata structure
        default_metadata = {
            "SAML": {
                "entity_id": "",
                "metadata_xml": "",
                "signing_certificate": "",
            },
            "OIDC": {
                "issuer": "",
                "jwks_uri": "",
                "authorization_endpoint": "",
                "token_endpoint": "",
                "userinfo_endpoint": "",
            }
        }

        connection = db.session.query(AuthenticationConnection).filter_by(connection_id=connection_id).first()
        connection_type = connection.type if connection else "OIDC"

        if metadata_blob is None:
            metadata_blob = {}

        self.metadata_blob = {**default_metadata.get(connection_type, {}), **metadata_blob}


class AuthenticationConnectionConfiguration(db.Model):
    """
    A model representing configuration settings for an authentication connection.

    This model stores configuration settings for an authentication connection,
    including protocol-specific configurations.

    Attributes:
     - id (int): The primary key identifier for the configuration.
     - connection_id (str): Foreign key linking to the `authentication_connection` table.
     - version (int): Version number of the configuration.
     - configuration_blob (dict): JSON field containing the connection configuration.
     - created_at (datetime): Timestamp when the configuration was created.
    """

    __tablename__ = "authentication_connection_configuration"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    connection_id = db.Column(db.String(64), db.ForeignKey("authentication_connection.connection_id"), nullable=False, index=True)
    version = db.Column(db.Integer, nullable=False)
    configuration_blob = db.Column(MutableDict.as_mutable(db.JSON), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.now(dt.UTC), nullable=False)

    def __init__(self, connection_id, configuration_blob=None):
        """Initializes a new authentication connection configuration entry.

        Args:
            connection_id (str): The connection ID associated with this configuration.
            configuration_blob (dict): The JSON object containing configuration settings.
        """
        self.connection_id = connection_id

        # Default configuration depending on the type
        default_configuration = {
            "SAML": {
                "idp_entity_id": "",
                "sso_url": "",
                "slo_url": "",
                "certificate": "",
                "signature_algorithm": "RSA-SHA256",
            },
            "OIDC": {
                "issuer": "",
                "authorization_endpoint": "",
                "token_endpoint": "",
                "userinfo_endpoint": "",
                "client_id": "",
                "client_secret": "",
                "scopes": ["openid", "profile", "email"],
            }
        }

        connection = db.session.query(AuthenticationConnection).filter_by(connection_id=connection_id).first()
        connection_type = connection.type if connection else "OIDC"

        if configuration_blob is None:
            configuration_blob = {}

        self.configuration_blob = {**default_configuration.get(connection_type, {}), **configuration_blob}

        max_version = db.session.query(db.func.max(AuthenticationConnection.version)).filter_by(connection_id=connection_id).scalar()
        self.version = (max_version or 0) + 1


class AuthenticationConnection(db.Model):
    """A model representing an authentication connection.

        This table stores identity providers used for authentication, such as
        SAML IdPs and OIDC providers.

        Attributes:
        - id (int): The primary key identifier for the connection.
        - connection_id (str): A unique identifier for the connection.
        - name (str): A user-friendly name for the authentication provider.
        - type (str): The authentication type (e.g., 'SAML', 'OIDC').
        - enabled (bool): Whether the connection is active and available for authentication.
        - created_at (datetime): The timestamp when the connection was created.
    """
    __tablename__ = "authentication_connection"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    connection_id = db.Column(db.String(64), unique=True, nullable=False, index=True, default=lambda: f"auth-{Xid().string()}")
    name = db.Column(db.String(255), nullable=False)
    protocol = db.Column(db.String(10), nullable=False)  # "SAML" or "OIDC"
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=dt.datetime.now(dt.UTC), nullable=False)

    # Foreign key to the User model
    user_id = db.Column(db.Integer, db.ForeignKey("user.fs_uniquifier"), nullable=False)

    # Relationship with the User model (one-to-many)
    owner = db.relationship("User", back_populates="connections")

    authn_configurations = db.relationship("AuthenticationConnectionConfiguration", lazy=True, backref="connection", cascade="all, delete-orphan")
    authn_metadata = db.relationship("AuthenticationConnectionMetadata", uselist=False, backref="connection", cascade="all, delete-orphan")

    def __init__(self, owner, protocol, name=None):
        # Generate public `client_id` in the format `CLIENT-$XID`
        self.connection_id = f"co-{Xid().string()}"
        self.name = name or "New Connection"

        self.protocol = protocol
        self.owner = owner