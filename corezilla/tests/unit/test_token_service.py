from datetime import timedelta

import jwt
import pytest
from flask_security.utils import aware_utcnow

from corezilla.app.services.TokenService import TokenService


@pytest.mark.usefixtures("oauth_client", "user", "db_session")
class TestTokenService:
    def test_generate_jwt_success(self, auth_config):
        """Ensure a JWT token is generated successfully."""
        payload = {"sub": "user123", "role": "admin"}
        expires_in = auth_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60

        token = TokenService.generate_jwt(payload, expires_in)

        assert isinstance(token, str)
        assert len(token) > 30  # JWTs are long


    def test_generate_refresh_token_success(self, auth_config):
        """Ensure a refresh token is generated successfully."""
        payload = {"sub": "user123", "client_id": "client456"}
        expires_in = auth_config["REFRESH_TOKEN_EXPIRE_MINUTES"] * 60

        token = TokenService.generate_refresh_token(payload, expires_in)
        assert isinstance(token, str)
        assert len(token) > 30


    def test_jwt_contains_correct_claims(self, auth_config):
        """Ensure JWT contains required claims."""
        payload = {"sub": "user123", "role": "admin"}
        expires_in = auth_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60

        token = TokenService.generate_jwt(payload, expires_in)
        decoded_token = jwt.decode(token, auth_config["SECRET_KEY"], algorithms=["HS256"])

        assert decoded_token["iss"] == auth_config["ISSUER_NAME"]
        assert decoded_token["aud"] == auth_config["AUDIENCE"]
        assert "iat" in decoded_token
        assert "exp" in decoded_token
        assert "jti" in decoded_token


    def test_jwt_expiration(self, auth_config):
        """Ensure JWT expires correctly."""
        payload = {"sub": "user123"}
        expires_in = 1  # 1 second expiration

        token = TokenService.generate_jwt(payload, expires_in)
        import time
        time.sleep(2)  # Wait for token to expire

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, auth_config["SECRET_KEY"], algorithms=["HS256"])


    def test_missing_issuer(self, auth_config):
        """Ensure an error is raised when the issuer is missing."""
        del auth_config["ISSUER_NAME"]

        payload = {"sub": "user123"}
        expires_in = auth_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60

        with pytest.raises(ValueError, match="Issuer \(iss\) cannot be None or empty."):
            TokenService.generate_jwt(payload, expires_in)


    def test_missing_audience(self, auth_config):
        """Ensure an error is raised when the audience is missing."""
        del auth_config["AUDIENCE"]

        payload = {"sub": "user123"}
        expires_in = auth_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60

        with pytest.raises(ValueError, match="Audience \(aud\) cannot be None or empty."):
            TokenService.generate_jwt(payload, expires_in)


    def test_handle_authorization_code_grant_success(self, oauth_client, auth_config, mocker):
        """Ensure access and refresh tokens are generated on successful authorization grant."""
        mock_auth_code = mocker.Mock()
        mock_auth_code.user_id = "user123"
        mock_auth_code.scope = "openid profile email"

        mocker.patch.object(oauth_client, "validate_authorization_code", return_value=mock_auth_code)

        result = TokenService.handle_authorization_code_grant(oauth_client, "valid-code", "https://example.com")

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "Bearer"
        assert result["expires_in"] == auth_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60


    def test_handle_authorization_code_grant_invalid_code(self, oauth_client, auth_config, mocker):
        """Ensure an invalid authorization code results in failure."""
        mocker.patch.object(oauth_client, "validate_authorization_code", return_value=None)

        result = TokenService.handle_authorization_code_grant(oauth_client, "invalid-code", "https://example.com")
        assert result is None


    def test_handle_refresh_token_grant_success(self, oauth_client, auth_config, mocker):
        """Ensure a new access token is generated from a valid refresh token."""
        refresh_token_payload = {
            "sub": "user123",
            "client_id": oauth_client.client_id,
            "scope": "openid profile email",
            "token_type": "refresh_token",
            "aud": auth_config["AUDIENCE"]
        }

        refresh_token = jwt.encode(refresh_token_payload, auth_config["SECRET_KEY"], algorithm="HS256")

        result = TokenService.handle_refresh_token_grant(oauth_client, refresh_token)

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "Bearer"
        assert result["expires_in"] == auth_config["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60


    def test_handle_refresh_token_grant_expired(self, oauth_client, auth_config):
        """Ensure an expired refresh token cannot generate a new access token."""
        refresh_token_payload = {
            "sub": "user123",
            "client_id": oauth_client.client_id,
            "scope": "openid profile email",
            "token_type": "refresh_token",
            "aud": auth_config["AUDIENCE"],
            "exp": aware_utcnow().replace(tzinfo=None) - timedelta(seconds=1)  # Expired
        }

        expired_refresh_token = jwt.encode(refresh_token_payload, auth_config["SECRET_KEY"], algorithm="HS256")

        result = TokenService.handle_refresh_token_grant(oauth_client, expired_refresh_token)
        assert result is None


    def test_handle_refresh_token_grant_invalid_type(self, oauth_client, auth_config):
        """Ensure only refresh tokens are accepted."""
        invalid_token_payload = {
            "sub": "user123",
            "client_id": oauth_client.client_id,
            "scope": "openid profile email",
            "token_type": "access_token",  # Wrong type
            "aud": auth_config["AUDIENCE"]
        }

        invalid_token = jwt.encode(invalid_token_payload, auth_config["SECRET_KEY"], algorithm="HS256")

        result = TokenService.handle_refresh_token_grant(oauth_client, invalid_token)
        assert result is None


    def test_handle_refresh_token_grant_invalid_signature(self, oauth_client, auth_config):
        """Ensure an invalid JWT signature is rejected."""
        refresh_token_payload = {
            "sub": "user123",
            "client_id": oauth_client.client_id,
            "scope": "openid profile email",
            "token_type": "refresh_token",
            "aud": auth_config["AUDIENCE"]
        }

        invalid_refresh_token = jwt.encode(refresh_token_payload, "wrong-secret-key", algorithm="HS256")

        result = TokenService.handle_refresh_token_grant(oauth_client, invalid_refresh_token)
        assert result is None
