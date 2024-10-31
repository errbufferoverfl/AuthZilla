from marshmallow import Schema, fields, validate


class UpdateURIsSchema(Schema):
    app_login_uri = fields.Url(required=False, schemes=["https"])
    redirect_uris = fields.List(fields.Url(schemes=["https"]), required=False)
    logout_uris = fields.List(fields.Url(schemes=["https"]), required=False)
    web_origins = fields.List(fields.Url(schemes=["https"]), required=False)


class UpdateCORSConfigSchema(Schema):
    is_enabled = fields.Bool(required=False)
    allowed_origins = fields.List(fields.Url(schemes=["https"]), required=False)
    fallback_url = fields.Url(required=False, schemes=["https"])


class UpdateRefreshTokenSettingsSchema(Schema):
    refresh_token_rotation_enabled = fields.Bool(required=False)
    rotation_overlap_period = fields.Integer(required=False)
    idle_refresh_token_lifetime_enabled = fields.Bool(required=False)
    idle_refresh_token_lifetime = fields.Integer(required=False)
    maximum_refresh_token_lifetime_enabled = fields.Bool(required=False)
    maximum_refresh_token_lifetime = fields.Integer(required=False)


class UpdateJWTSettingsSchema(Schema):
    algorithm = fields.Str(required=False)


class UpdateConfigurationBlobSchema(Schema):
    oidc_conformant = fields.Bool(required=False)
    sender_constrained = fields.Bool(required=False)
    token_endpoint_auth_method = fields.Str(required=False)
    uris = fields.Nested(UpdateURIsSchema, required=False)
    cors = fields.Nested(UpdateCORSConfigSchema, required=False)
    refresh = fields.Nested(UpdateRefreshTokenSettingsSchema, required=False)
    jwt = fields.Nested(UpdateJWTSettingsSchema, required=False)


class UpdateMetadataSchema(Schema):
    description = fields.Str(required=False, validate=validate.Length(max=250))
    logo = fields.Str(required=False)
    tos = fields.Url(required=False, schemes=["https"])
    privacy_policy = fields.Url(required=False, schemes=["https"])
    security_contact = fields.Str(required=False)
    privacy_contact = fields.Str(required=False)


class UpdateClientRequest(Schema):
    name = fields.Str(required=False)
    metadata_blob = fields.Nested(UpdateMetadataSchema, required=False)
    configuration_blob = fields.Nested(UpdateConfigurationBlobSchema, required=False)
