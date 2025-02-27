from marshmallow import Schema, fields, validates_schema, ValidationError
from marshmallow.validate import URL


class UpdateURIsSchema(Schema):
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


class UpdateCORSConfigSchema(Schema):
    is_enabled = fields.Bool(
        description="Indicates if Cross-Origin Resource Sharing (CORS) is enabled."
    )
    allowed_origins = fields.List(
        fields.Url(schemes=["https"]),
        description="List of allowed origins for CORS requests.",
        required=False
    )
    fallback_url = fields.Url(
        schemes=["https"],
        description="Fallback URL for CORS requests when an origin is not explicitly allowed.",
        required=False
    )

    @validates_schema
    def validate_fields_when_enabled(self, data, **kwargs):
        if data.get("is_enabled"):
            # Validate allowed_origins
            if not data.get("allowed_origins"):
                raise ValidationError(
                    {"allowed_origins": "This field must be populated when CORS is enabled."}
                )
            # Validate fallback_url
            if not data.get("fallback_url"):
                raise ValidationError(
                    {"fallback_url": "This field must be populated when CORS is enabled."}
                )


class UpdateRefreshTokenSettingsSchema(Schema):
    refresh_token_rotation_enabled = fields.Bool(
        description="Whether refresh token rotation is enabled."
    )
    rotation_overlap_period = fields.Integer(
        description="Period, in seconds, for which an old refresh token remains valid during rotation.",
        allow_none=True,
    )
    idle_refresh_token_lifetime_enabled = fields.Bool(
        description="Indicates if idle refresh token lifetime is enforced."
    )
    idle_refresh_token_lifetime = fields.Integer(
        description="Lifetime of an idle refresh token in seconds.",
        allow_none=True,
    )
    maximum_refresh_token_lifetime_enabled = fields.Bool(
        description="Indicates if a maximum lifetime for refresh tokens is enforced."
    )
    maximum_refresh_token_lifetime = fields.Integer(
        description="Maximum allowed lifetime of a refresh token in seconds.",
        allow_none=True,
    )

    @validates_schema
    def validate_fields(self, data, **kwargs):
        # Validate rotation_overlap_period if refresh_token_rotation_enabled is True
        if data.get("refresh_token_rotation_enabled") and data.get("rotation_overlap_period") is None:
            raise ValidationError(
                {"rotation_overlap_period": "This field must be populated when rotation is enabled."}
            )

        # Validate idle_refresh_token_lifetime if idle_refresh_token_lifetime_enabled is True
        if data.get("idle_refresh_token_lifetime_enabled") and data.get("idle_refresh_token_lifetime") is None:
            raise ValidationError(
                {"idle_refresh_token_lifetime": "This field must be populated when idle lifetime enforcement is enabled."}
            )

        # Validate maximum_refresh_token_lifetime if maximum_refresh_token_lifetime_enabled is True
        if data.get("maximum_refresh_token_lifetime_enabled") and data.get("maximum_refresh_token_lifetime") is None:
            raise ValidationError(
                {"maximum_refresh_token_lifetime": "This field must be populated when maximum lifetime enforcement is enabled."}
            )


class UpdateJWTSettingsSchema(Schema):
    algorithm = fields.String(
        description="Algorithm used for signing JWT tokens."
    )


# Metadata schema for client information
class UpdateClientMetadataResponseSchema(Schema):
    description = fields.String(allow_none=True)
    logo = fields.String(allow_none=True)
    tos = fields.String(allow_none=True)
    privacy_policy = fields.String(data_key="privacy_policy", allow_none=True)
    security_contact = fields.String(data_key="security_contact", allow_none=True)
    privacy_contact = fields.String(data_key="privacy_contact", allow_none=True)


class UpdateClientConfigurationResponseSchema(Schema):
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
        UpdateURIsSchema(),
        description="Configuration of URIs used in client interactions."
    )
    cors = fields.Nested(
        UpdateCORSConfigSchema(),
        description="Configuration for Cross-Origin Resource Sharing (CORS) settings."
    )
    refresh = fields.Nested(
        UpdateRefreshTokenSettingsSchema(),
        description="Settings related to refresh token configuration."
    )
    jwt = fields.Nested(
        UpdateJWTSettingsSchema(),
        description="Settings related to JSON Web Tokens (JWT)."
    )


class UpdateClientRequest(Schema):
    name = fields.Str(required=False)

    metadata = fields.Nested(UpdateClientMetadataResponseSchema(), attribute="metadata")
    configuration = fields.Nested(UpdateClientConfigurationResponseSchema(), attribute="configuration")
