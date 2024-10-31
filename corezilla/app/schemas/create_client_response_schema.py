from marshmallow import Schema, fields, post_dump

from corezilla.app.schemas.create_client_request_schema import URIsSchema, CORSConfigSchema, RefreshTokenSettingsSchema, JWTSettingsSchema


class MetadataResponseSchema(Schema):
    description = fields.Str(dump_only=True)
    logo = fields.Str(dump_only=True)
    tos = fields.Url(dump_only=True)
    privacy_policy = fields.Url(dump_only=True)
    security_contact = fields.Str(dump_only=True)
    privacy_contact = fields.Str(dump_only=True)


class ClientConfigurationResponseSchema(Schema):
    oidc_conformant = fields.Bool(dump_only=True)
    sender_constrained = fields.Bool(dump_only=True)
    token_endpoint_auth_method = fields.Str(dump_only=True)
    uris = fields.Nested(URIsSchema, dump_only=True)
    cors = fields.Nested(CORSConfigSchema, dump_only=True)
    refresh = fields.Nested(RefreshTokenSettingsSchema, dump_only=True)
    jwt = fields.Nested(JWTSettingsSchema, dump_only=True)


class ClientSecretSchema(Schema):
    value = fields.Str(required=True)
    visibility = fields.Str(required=True, default="private")


class LinksSchema(Schema):
    self = fields.Url(required=True)


class ClientResponse(Schema):
    client_id = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)
    client_secret = fields.Str(dump_only=True)
    is_public = fields.Bool(dump_only=True)
    client_type = fields.Str(dump_only=True)
    client_uri = fields.Url(missing="")
    metadata = fields.Nested(MetadataResponseSchema, attribute="metadata_blob", dump_only=True)
    configuration = fields.Nested(ClientConfigurationResponseSchema, attribute="configuration_blob", dump_only=True)

    _links = fields.Nested(LinksSchema, dump_only=True)

    @post_dump
    def add_links(self, data, **kwargs):
        """Dynamically adds the self link based on client_id."""
        if "client_id" in data:
            data["_links"] = {
                "self": f"/api/clients/{data['client_id']}"
            }
        return data


class ClientResponseWrapperSchema(Schema):
    client = fields.Nested(ClientResponse, dump_only=True)