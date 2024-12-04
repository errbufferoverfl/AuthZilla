from marshmallow import Schema, fields, post_dump

from corezilla.app.schemas.create_client_request_schema import (
    RefreshTokenSettingsSchema, JWTSettingsSchema
)


class URIResponseSchema(Schema):
    app_login_uri = fields.String(
        description="The URI for the application's login page."
    )
    redirect_uris = fields.List(
        fields.String(),
        description="List of URIs for redirection after authentication."
    )
    logout_uris = fields.List(
        fields.String(),
        description="List of URIs for redirection after logout."
    )
    web_origins = fields.List(
        fields.String(),
        description="List of allowed web origins for CORS requests."
    )


class CORSConfigResponseSchema(Schema):
    is_enabled = fields.Bool(
        description="Indicates if Cross-Origin Resource Sharing (CORS) is enabled."
    )
    allowed_origins = fields.List(
        fields.String(),
        description="List of allowed origins for CORS requests."
    )
    fallback_url = fields.String(
        description="Fallback URL for CORS requests when an origin is not explicitly allowed."
    )


# Metadata schema for client information
class ClientMetadataResponseSchema(Schema):
    description = fields.String(allow_none=True)
    logo = fields.String(allow_none=True)
    tos = fields.String(allow_none=True)
    privacy_policy = fields.String(data_key="privacy_policy", allow_none=True)
    security_contact = fields.String(data_key="security_contact", allow_none=True)
    privacy_contact = fields.String(data_key="privacy_contact", allow_none=True)


# Configuration schema for client settings
class ClientConfigurationResponseSchema(Schema):
    oidc_conformant = fields.Bool()
    sender_constrained = fields.Bool()
    token_endpoint_auth_method = fields.String(allow_none=True)
    uris = fields.Nested(URIResponseSchema())
    cors = fields.Nested(CORSConfigResponseSchema())
    refresh = fields.Nested(RefreshTokenSettingsSchema())
    jwt = fields.Nested(JWTSettingsSchema())


# Client secret schema with visibility settings
class ClientSecretSchema(Schema):
    value = fields.String(required=True)
    visibility = fields.String(required=True, default="private")


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
