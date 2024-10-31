from marshmallow import Schema, fields, validates, ValidationError


class URIsSchema(Schema):
    app_login_uri = fields.Url(schemes=["https"], missing="https://example.com/login")
    redirect_uris = fields.List(fields.Url(schemes=["https"]), missing=["https://example.com/callback"])
    logout_uris = fields.List(fields.Url(schemes=["https"]), missing=["https://example.com/logout"])
    web_origins = fields.List(fields.Url(schemes=["https"]), missing=["https://example.com"])


class CORSConfigSchema(Schema):
    is_enabled = fields.Bool(missing=False)
    allowed_origins = fields.List(fields.Url(schemes=["https"]), missing=["https://example.com"])
    fallback_url = fields.Url(schemes=["https"], missing="https://example.com/fallback")


class RefreshTokenSettingsSchema(Schema):
    refresh_token_rotation_enabled = fields.Bool(missing=False)
    rotation_overlap_period = fields.Integer(missing=0)
    idle_refresh_token_lifetime_enabled = fields.Bool(missing=False)
    idle_refresh_token_lifetime = fields.Integer(missing=1296000)
    maximum_refresh_token_lifetime_enabled = fields.Bool(missing=False)
    maximum_refresh_token_lifetime = fields.Integer(missing=2592000)


class JWTSettingsSchema(Schema):
    algorithm = fields.Str(missing="RS256")


class ConfigurationBlobSchema(Schema):
    oidc_conformant = fields.Bool(missing=True)
    sender_constrained = fields.Bool(missing=False)
    token_endpoint_auth_method = fields.Str(missing="client_secret_basic")
    uris = fields.Nested(URIsSchema, missing=lambda: URIsSchema().load({}))
    cors = fields.Nested(CORSConfigSchema, missing=lambda: CORSConfigSchema().load({}))
    refresh = fields.Nested(RefreshTokenSettingsSchema, missing=lambda: RefreshTokenSettingsSchema().load({}))
    jwt = fields.Nested(JWTSettingsSchema, missing=lambda: JWTSettingsSchema().load({}))


class CreateClientRequest(Schema):
    metadata_blob = fields.Dict(missing=lambda: {
        "description": "",
        "logo": "https://example.com/logo.png",
        "tos": "https://example.com/tos",
        "privacy policy": "https://example.com/privacy",
        "security contact": "security@example.com",
        "privacy contact": "privacy@example.com"
    })
    configuration_blob = fields.Nested(ConfigurationBlobSchema, missing=lambda: ConfigurationBlobSchema().load({}))

    @validates("metadata_blob")
    def validate_metadata_blob(self, data):
        required_fields = ["description", "logo", "tos", "privacy policy", "security contact", "privacy contact"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"'{field}' is a required field in metadata_blob.")
