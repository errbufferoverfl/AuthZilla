from marshmallow import Schema, fields, validate
from marshmallow import pre_load, post_dump

from corezilla.app.models.User import User


class UserSessionSchema(Schema):
    username = fields.Str()
    password = fields.Str(load_only=True)


class LoginUserRequest(Schema):
    username_or_email = fields.Str(
        required=True,
        validate=validate.Length(min=1)
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8)
    )


class RegisterUserRequest(Schema):
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3)
    )
    email = fields.Email(
        required=True
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8)
    )
    password_confirm = fields.Str(
        required=True,
        validate=validate.Length(min=8)
    )

    class Meta:
        ordered = True


class UserResponseSchema(Schema):
    message = fields.Str()


class UserSchema(Schema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True  # Include foreign keys if applicable
        exclude = ("password",)  # Exclude sensitive fields like password
        ordered = True

    username = fields.Str(example="leetify")
    password = fields.Str(load_only=True)

    last_login_at = fields.Str(dump_only=True)
    current_login_at = fields.Str(dump_only=True)
    last_login_ip = fields.Str(dump_only=True)
    current_login_ip = fields.Str(dump_only=True)

    @pre_load
    def make_user(self, data, **kwargs):  # noqa
        return data

    @post_dump
    def dump_user(self, data, **kwargs):  # noqa
        return {"user": data}

