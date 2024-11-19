from marshmallow import Schema, fields, validate


class URIsSchema(Schema):
    app_login_uri = fields.Url(
        schemes=["https"],
        missing="https://example.com/login",
        description="The URI for the application's login page.",
    )
    redirect_uris = fields.List(
        fields.Url(schemes=["https"]),
        missing=["https://example.com/callback"],
        description="List of URIs for redirection after authentication."
    )
    logout_uris = fields.List(
        fields.Url(schemes=["https"]),
        missing=["https://example.com/logout"],
        description="List of URIs for redirection after logout."
    )
    web_origins = fields.List(
        fields.Url(schemes=["https"]),
        missing=["https://example.com"],
        description="List of allowed web origins for CORS requests."
    )


class CORSConfigSchema(Schema):
    is_enabled = fields.Bool(
        missing=False,
        description="Indicates if Cross-Origin Resource Sharing (CORS) is enabled."
    )
    allowed_origins = fields.List(
        fields.Url(schemes=["https"]),
        missing=["https://example.com"],
        description="List of allowed origins for CORS requests."
    )
    fallback_url = fields.Url(
        schemes=["https"],
        missing="https://example.com/fallback",
        description="Fallback URL for CORS requests when an origin is not explicitly allowed."
    )


class RefreshTokenSettingsSchema(Schema):
    refresh_token_rotation_enabled = fields.Bool(
        missing=False,
        description="Whether refresh token rotation is enabled."
    )
    rotation_overlap_period = fields.Integer(
        missing=0,
        description="Period, in seconds, for which an old refresh token remains valid during rotation."
    )
    idle_refresh_token_lifetime_enabled = fields.Bool(
        missing=False,
        description="Indicates if idle refresh token lifetime is enforced."
    )
    idle_refresh_token_lifetime = fields.Integer(
        missing=1296000,
        description="Lifetime of an idle refresh token in seconds."
    )
    maximum_refresh_token_lifetime_enabled = fields.Bool(
        missing=False,
        description="Indicates if a maximum lifetime for refresh tokens is enforced."
    )
    maximum_refresh_token_lifetime = fields.Integer(
        missing=2592000,
        description="Maximum allowed lifetime of a refresh token in seconds."
    )


class JWTSettingsSchema(Schema):
    algorithm = fields.Str(
        missing="RS256",
        description="Algorithm used for signing JWT tokens."
    )


class ConfigurationBlobSchema(Schema):
    oidc_conformant = fields.Bool(
        missing=True,
        description="Specifies if the client conforms to OpenID Connect standards."
    )
    sender_constrained = fields.Bool(
        missing=False,
        description="Indicates if tokens are constrained to the sender."
    )
    token_endpoint_auth_method = fields.Str(
        missing="client_secret_basic",
        description="Method of authentication at the token endpoint."
    )
    uris = fields.Nested(
        URIsSchema(),
        missing=lambda: URIsSchema().load({}),
        description="Configuration of URIs used in client interactions."
    )
    cors = fields.Nested(
        CORSConfigSchema(),
        missing=lambda: CORSConfigSchema().load({}),
        description="Configuration for Cross-Origin Resource Sharing (CORS) settings."
    )
    refresh = fields.Nested(
        RefreshTokenSettingsSchema(),
        missing=lambda: RefreshTokenSettingsSchema().load({}),
        description="Settings related to refresh token configuration."
    )
    jwt = fields.Nested(
        JWTSettingsSchema(),
        missing=lambda: JWTSettingsSchema().load({}),
        description="Settings related to JSON Web Tokens (JWT)."
    )

class CreateClientRequest(Schema):
    metadata_blob = fields.Dict(missing=lambda: {
        "description": "",
        "logo": "https://example.com/logo.png",
        "tos": "https://example.com/tos",
        "privacy_policy": "https://example.com/privacy",
        "security_contact": "security@example.com",
        "privacy_contact": "privacy@example.com"
    })
    configuration_blob = fields.Nested(ConfigurationBlobSchema(), missing=lambda: ConfigurationBlobSchema().load({}))


class ReadClientRequest(Schema):
    """Schema for reading client requests with pagination parameters."""

    page = fields.Int(
        missing=1,
        validate=validate.Range(min=1),
        description="Page number to retrieve, defaults to 1"
    )
    per_page = fields.Int(
        missing=50,
        validate=validate.Range(min=1, max=100),
        description="Number of items per page, defaults to 50, maximum 100"
    )