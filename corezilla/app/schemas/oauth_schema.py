import marshmallow_sqlalchemy as ma
from flask_marshmallow import Schema
from marshmallow import pre_load, post_dump, fields, validates_schema, ValidationError, validate, INCLUDE


class AuthorizationCodeRequest(Schema):
    """
    The authorization endpoint is used by the authorization code grant type and implicit grant type flows.
    The client informs the authorization server of the desired grant type using the response_type.
    """
    client_id = fields.String()
    redirect_uri = fields.Str()
    scope = fields.Str()
    state = fields.Str()
    response_type = fields.Str()

    class Meta:
        unknown = INCLUDE

class AuthorizationCodeResponse(Schema):
    code = fields.Str(validate=validate.Length(min=1))
    state = fields.Str(validate=validate.Length(min=1))


class TokenResponseSchema(ma.SQLAlchemySchema):
    access_token = fields.Str(dump_only=True)
    refresh_token = fields.Str(dump_only=True)
    expires_in = fields.Int(dump_only=True)
    scope = fields.Str(dump_only=True)