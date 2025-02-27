import uuid
from datetime import timedelta

import flask.config
import jwt
from flask_security.utils import aware_utcnow


class TokenService:
    @staticmethod
    def generate_jwt(payload, expires_in, resources:str):
        """Generate a JWT access or refresh token with required parameters."""
        iss = flask.current_app.config.get('ISSUER_NAME')
        aud = resources
        access_token_secret = flask.current_app.config.get('ACCESS_TOKEN_SECRET')

        if not iss or not iss.strip():
            raise ValueError("Issuer (iss) cannot be None or empty.")
        if not aud or not aud.strip():
            raise ValueError("Audience (aud) cannot be None or empty.")


        payload.update({
            "iss": iss,
            "aud": aud,
            "iat": aware_utcnow().replace(tzinfo=None),
            "exp": aware_utcnow().replace(tzinfo=None) + timedelta(seconds=expires_in),
            "jti": str(uuid.uuid4())
        })
        return jwt.encode(payload, access_token_secret, algorithm=flask.current_app.config.get('JWT_ALGORITHM', "HS256"))

    @staticmethod
    def generate_refresh_token(payload, expires_in):
        """Generate a JWT refresh token with required parameters."""
        iss = flask.current_app.config.get('ISSUER_NAME')
        aud = flask.current_app.config.get('AUDIENCE')
        access_token_secret = flask.current_app.config.get('ACCESS_TOKEN_SECRET')

        if not iss or not iss.strip():
            raise ValueError("Issuer (iss) cannot be None or empty.")
        if not aud or not aud.strip():
            raise ValueError("Audience (aud) cannot be None or empty.")

        payload.update({
            "iss": iss,
            "aud": aud,
            "iat": aware_utcnow().replace(tzinfo=None),
            "exp": aware_utcnow().replace(tzinfo=None) + timedelta(seconds=expires_in),
            "jti": str(uuid.uuid4()),
            "token_type": "refresh_token"
        })
        return jwt.encode(payload, access_token_secret, algorithm=flask.current_app.config.get('JWT_ALGORITHM', "HS256"))


    @staticmethod
    def handle_authorization_code_grant(client, code, redirect_uri):
        """Validate authorization code and generate access and refresh JWT tokens."""
        auth_code = client.validate_authorization_code(code, redirect_uri)
        if not auth_code:
            return None

        access_token_exp = flask.current_app.config.get('ACCESS_TOKEN_EXPIRE_MINUTES', 60) * 60
        refresh_token_exp = flask.current_app.config.get('REFRESH_TOKEN_EXPIRE_MINUTES', 43200) * 60

        access_token_payload = {
            "sub": auth_code.user_id,
            "client_id": client.client_id,
            "scope": auth_code.scope,
            "token_type": "access_token"
        }
        refresh_token_payload = {
            "sub": auth_code.user_id,
            "client_id": client.client_id,
            "scope": auth_code.scope,
            "token_type": "refresh_token"
        }

        access_token = TokenService.generate_jwt(access_token_payload, access_token_exp)
        refresh_token = TokenService.generate_refresh_token(refresh_token_payload, refresh_token_exp)

        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": access_token_exp,
            "refresh_token": refresh_token
        }

    @staticmethod
    def handle_refresh_token_grant(client, refresh_token):
        """Validate refresh JWT token and generate a new access JWT token."""
        access_token_secret = flask.current_app.config.get('ACCESS_TOKEN_SECRET')

        try:
            decoded_token = jwt.decode(refresh_token, access_token_secret, algorithms=[flask.current_app.config.get('JWT_ALGORITHM', "HS256")], audience=flask.current_app.config.get('AUDIENCE', AUDIENCE))
        except jwt.ExpiredSignatureError:
            return None

        if decoded_token["token_type"] != "refresh_token":
            return None

        access_token_exp = flask.current_app.config.get('ACCESS_TOKEN_EXPIRE_MINUTES', 60) * 60

        new_access_token_payload = {
            "sub": decoded_token["sub"],
            "client_id": decoded_token["client_id"],
            "scope": decoded_token["scope"],
            "token_type": "access_token"
        }
        new_access_token = TokenService.generate_jwt(new_access_token_payload, access_token_exp)

        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": access_token_exp,
            "refresh_token": refresh_token
        }
