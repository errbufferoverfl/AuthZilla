from marshmallow import Schema, fields, validate


class URIsSchema(Schema):
    app_login_uri = fields.Url(
        schemes=["https"],
        description="The URI for the application's login page."
    )
    redirect_uris = fields.List(
        fields.Url(schemes=["https"]),
        description="List of URIs for redirection after authentication."
    )
    logout_uris = fields.List(
        fields.Url(schemes=["https"]),
        description="List of URIs for redirection after logout."
    )
    web_origins = fields.List(
        fields.Url(schemes=["https"]),
        description="List of allowed web origins for CORS requests."
    )


class CORSConfigSchema(Schema):
    is_enabled = fields.Bool(
        description="Indicates if Cross-Origin Resource Sharing (CORS) is enabled."
    )
    allowed_origins = fields.List(
        fields.Url(schemes=["https"]),
        description="List of allowed origins for CORS requests."
    )
    fallback_url = fields.Url(
        schemes=["https"],
        description="Fallback URL for CORS requests when an origin is not explicitly allowed."
    )


class RefreshTokenSettingsSchema(Schema):
    refresh_token_rotation_enabled = fields.Bool(
        description="Whether refresh token rotation is enabled."
    )
    rotation_overlap_period = fields.Integer(
        description="Period, in seconds, for which an old refresh token remains valid during rotation."
    )
    idle_refresh_token_lifetime_enabled = fields.Bool(
        description="Indicates if idle refresh token lifetime is enforced."
    )
    idle_refresh_token_lifetime = fields.Integer(
        description="Lifetime of an idle refresh token in seconds."
    )
    maximum_refresh_token_lifetime_enabled = fields.Bool(
        description="Indicates if a maximum lifetime for refresh tokens is enforced."
    )
    maximum_refresh_token_lifetime = fields.Integer(
        description="Maximum allowed lifetime of a refresh token in seconds."
    )


class JWTSettingsSchema(Schema):
    algorithm = fields.Str(
        description="Algorithm used for signing JWT tokens."
    )


class ConfigurationBlobSchema(Schema):
    oidc_conformant = fields.Bool(
        description="Specifies if the client conforms to OpenID Connect standards."
    )
    sender_constrained = fields.Bool(
        description="Indicates if tokens are constrained to the sender."
    )
    token_endpoint_auth_method = fields.Str(
        description="Method of authentication at the token endpoint."
    )
    uris = fields.Nested(
        URIsSchema(),
        description="Configuration of URIs used in client interactions."
    )
    cors = fields.Nested(
        CORSConfigSchema(),
        description="Configuration for Cross-Origin Resource Sharing (CORS) settings."
    )
    refresh = fields.Nested(
        RefreshTokenSettingsSchema(),
        description="Settings related to refresh token configuration."
    )
    jwt = fields.Nested(
        JWTSettingsSchema(),
        description="Settings related to JSON Web Tokens (JWT)."
    )


class CreateClientRequest(Schema):
    metadata_blob = fields.Dict(
        description="Metadata associated with the client."
    )
    configuration_blob = fields.Nested(
        ConfigurationBlobSchema(),
        description="Configuration settings for the client."
    )


class ReadClientRequest(Schema):
    """Schema for reading client requests with pagination parameters."""
    page = fields.Int(
        validate=validate.Range(min=1),
        description="Page number to retrieve, defaults to 1"
    )
    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        description="Number of items per page, defaults to 50, maximum 100"
    )