import base64
import datetime
import json
import secrets

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from corezilla.app.services.AuthorizationCodeService import AuthorizationCodeService


@pytest.mark.usefixtures("oauth_client", "user", "db_session")
class TestAuthorizationCodeService:
    def test_generate_authorization_code(self, app, oauth_client, auth_config):
        """Ensure an authorization code is generated and correctly encrypted."""
        auth_code = AuthorizationCodeService.generate_authorization_code(oauth_client.client_id, oauth_client.owner.user_id)

        assert isinstance(auth_code, str)
        assert len(auth_code) > 30  # Ensure it's long enough


    def test_decrypt_authorization_code(self, oauth_client, auth_config):
        """Ensure a generated authorization code can be decrypted correctly."""
        auth_code = AuthorizationCodeService.generate_authorization_code(oauth_client.client_id, oauth_client.owner.user_id)
        payload = AuthorizationCodeService.decrypt_authorization_code(auth_code)

        assert payload["client_id"] == oauth_client.client_id
        assert payload["user_id"] == oauth_client.owner.user_id
        assert payload["iss"] == auth_config["ISSUER_NAME"]


    def test_validate_authorization_code_success(self, oauth_client, auth_config):
        """Ensure validation succeeds for a valid code."""
        auth_code = AuthorizationCodeService.generate_authorization_code(oauth_client.client_id, oauth_client.owner.user_id)
        payload = AuthorizationCodeService.validate_authorization_code(auth_code, oauth_client.client_id)

        assert payload["client_id"] == oauth_client.client_id
        assert payload["iss"] == auth_config["ISSUER_NAME"]


    def test_validate_authorization_code_expired(self, oauth_client, auth_config):
        """Ensure validation fails for an expired code."""
        auth_code = AuthorizationCodeService.generate_authorization_code(oauth_client.client_id, oauth_client.owner.user_id)

        # Simulate expiration
        payload = AuthorizationCodeService.decrypt_authorization_code(auth_code)
        payload["exp"] = int(datetime.datetime.utcnow().timestamp()) - 1  # Past expiry

        # Re-encrypt with modified expiration
        secret = auth_config["AUTH_CODE_SECRET_KEY"]
        payload_bytes = json.dumps(payload).encode()
        aesgcm = AESGCM(secret)
        nonce = secrets.token_bytes(12)
        encrypted_data = aesgcm.encrypt(nonce, payload_bytes, None)
        tampered_code = base64.urlsafe_b64encode(nonce + encrypted_data).decode()

        with pytest.raises(ValueError, match="Authorization code has expired"):
            AuthorizationCodeService.validate_authorization_code(tampered_code, oauth_client.client_id)


    def test_validate_authorization_code_invalid_client(self, oauth_client, auth_config):
        """Ensure validation fails if client_id does not match."""
        auth_code = AuthorizationCodeService.generate_authorization_code(oauth_client.client_id, oauth_client.owner.user_id)

        with pytest.raises(ValueError, match="Client ID mismatch"):
            AuthorizationCodeService.validate_authorization_code(auth_code, "wrong-client")


    def test_validate_authorization_code_tampered(self, oauth_client, auth_config):
        """Ensure validation fails if the authorization code is tampered with."""
        auth_code = AuthorizationCodeService.generate_authorization_code(oauth_client.client_id, oauth_client.owner.user_id)

        # Modify auth_code by changing one character
        tampered_code = auth_code[:-1] + ('A' if auth_code[-1] != 'A' else 'B')

        with pytest.raises(ValueError, match="Invalid authorization code"):
            AuthorizationCodeService.validate_authorization_code(tampered_code, oauth_client.client_id)


    def test_decrypt_invalid_code(self, auth_config):
        """Ensure decryption fails for an invalid authorization code."""
        invalid_code = "invalid_code"

        with pytest.raises(ValueError, match="Invalid authorization code"):
            AuthorizationCodeService.decrypt_authorization_code(invalid_code)


    def test_validate_invalid_issuer(self, oauth_client, auth_config):
        """Ensure validation fails if the issuer is incorrect."""
        auth_code = AuthorizationCodeService.generate_authorization_code(oauth_client.client_id, oauth_client.owner.user_id)

        # Tamper payload by modifying the issuer
        payload = AuthorizationCodeService.decrypt_authorization_code(auth_code)
        payload["iss"] = "https://wrong-issuer.com"

        # Re-encrypt
        secret = auth_config["AUTH_CODE_SECRET_KEY"]
        payload_bytes = json.dumps(payload).encode()
        aesgcm = AESGCM(secret)
        nonce = secrets.token_bytes(12)
        encrypted_data = aesgcm.encrypt(nonce, payload_bytes, None)
        tampered_code = base64.urlsafe_b64encode(nonce + encrypted_data).decode()

        with pytest.raises(ValueError, match="Invalid issuer"):
            AuthorizationCodeService.validate_authorization_code(tampered_code, oauth_client.client_id)


    def test_code_not_yet_valid(self, oauth_client, auth_config):
        """Ensure validation fails if the authorization code is not yet valid (nbf in the future)."""
        auth_code = AuthorizationCodeService.generate_authorization_code(oauth_client.client_id, oauth_client.owner.user_id)

        # Modify payload to simulate future validity
        payload = AuthorizationCodeService.decrypt_authorization_code(auth_code)
        payload["nbf"] = int(datetime.datetime.utcnow().timestamp()) + 1000  # Future timestamp

        # Re-encrypt
        secret = auth_config["AUTH_CODE_SECRET_KEY"]
        payload_bytes = json.dumps(payload).encode()
        aesgcm = AESGCM(secret)
        nonce = secrets.token_bytes(12)
        encrypted_data = aesgcm.encrypt(nonce, payload_bytes, None)
        tampered_code = base64.urlsafe_b64encode(nonce + encrypted_data).decode()

        with pytest.raises(ValueError, match="Authorization code is not yet valid"):
            AuthorizationCodeService.validate_authorization_code(tampered_code, oauth_client.client_id)
