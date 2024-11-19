from marshmallow import Schema, fields, post_dump

from corezilla.app.schemas.create_client_request_schema import (
    URIsSchema, CORSConfigSchema, RefreshTokenSettingsSchema, JWTSettingsSchema
)


# Metadata schema for client information
class ClientMetadataResponseSchema(Schema):
    description = fields.String()
    logo = fields.String()
    tos = fields.Url()
    privacy_policy = fields.Url(data_key="privacy_policy")
    security_contact = fields.Str(data_key="security_contact")
    privacy_contact = fields.Str(data_key="privacy_contact")


# Configuration schema for client settings
class ClientConfigurationResponseSchema(Schema):
    oidc_conformant = fields.Bool()
    sender_constrained = fields.Bool()
    token_endpoint_auth_method = fields.String()
    uris = fields.Nested(URIsSchema())
    cors = fields.Nested(CORSConfigSchema())
    refresh = fields.Nested(RefreshTokenSettingsSchema())
    jwt = fields.Nested(JWTSettingsSchema())


# Client secret schema with visibility settings
class ClientSecretSchema(Schema):
    value = fields.Str(required=True)
    visibility = fields.Str(required=True, default="private")


# Links schema to add hypermedia controls
class LinksSchema(Schema):
    self = fields.Url(required=True)


# Primary response schema for client details
class CreateClientResponseSchema(Schema):
    client_id = fields.String()
    name = fields.String()
    client_secret = fields.String()
    is_public = fields.Bool()
    client_type = fields.String()
    client_uri = fields.String(allow_none=True)

    metadata = fields.Nested(ClientMetadataResponseSchema(), attribute="metadata")
    configuration = fields.Nested(ClientConfigurationResponseSchema(), attribute="configuration")
    _links = fields.Nested(LinksSchema())

    @post_dump
    def add_links(self, data, many=True):
        """Adds a self link based on client_id."""
        if "client_id" in data:
            data["_links"] = {"self": f"/api/clients/{data['client_id']}"}
        return data


# Wrapper schema for paginated client responses
class GetClientResponseSchema(Schema):
    clients = fields.List(fields.Nested(CreateClientResponseSchema()))
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()

    @post_dump
    def add_pagination(self, data, many=True):
        """Wraps the response with pagination details."""
        return {
            "clients": data.get("clients"),
            "total": data.get("total"),
            "page": data.get("page"),
            "per_page": data.get("per_page"),
        }
