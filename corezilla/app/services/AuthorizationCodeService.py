import secrets
import datetime
import base64
import json

import flask
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class AuthorizationCodeService:
    """Handles generating, encrypting, decrypting, and validating OAuth 2.0 authorization codes"""

    @staticmethod
    def generate_authorization_code(client_id: str, user_id: str):
        iss = flask.current_app.config.get('ISSUER_NAME')
        ttl = flask.current_app.config.get('AUTH_CODE_EXPIRY_MINUTES')
        auth_code_secret = flask.current_app.config.get('AUTH_CODE_SECRET_KEY')

        """Generate an encrypted authorization code with required claims"""
        now = datetime.datetime.utcnow()
        payload = {
            "client_id": client_id,
            "user_id": user_id,
            "iss": iss,
            "iat": int(now.timestamp()),
            "nbf": int(now.timestamp()),
            "exp": int((now + datetime.timedelta(seconds=ttl)).timestamp())
        }

        # Convert payload to JSON bytes
        payload_bytes = json.dumps(payload).encode()

        if isinstance(auth_code_secret, str):
            auth_code_secret = auth_code_secret.encode()

        # Encrypt using AES-GCM
        aesgcm = AESGCM(auth_code_secret)
        nonce = secrets.token_bytes(12)  # Generate a unique nonce for encryption
        encrypted_data = aesgcm.encrypt(nonce, payload_bytes, None)

        # Encode (nonce + encrypted data) into a compact, URL-safe format
        return base64.urlsafe_b64encode(nonce + encrypted_data).decode()

    @staticmethod
    def decrypt_authorization_code(auth_code: str):
        """Decrypts an authorization code and returns the payload"""
        auth_code_secret = flask.current_app.config.get('AUTH_CODE_SECRET_KEY')

        if isinstance(auth_code_secret, str):
            auth_code_secret = auth_code_secret.encode()

        try:
            # Decode the base64-encoded encrypted data
            decoded_data = base64.urlsafe_b64decode(auth_code)
            nonce, encrypted_payload = decoded_data[:12], decoded_data[12:]

            # Decrypt the payload
            aesgcm = AESGCM(auth_code_secret)
            decrypted_bytes = aesgcm.decrypt(nonce, encrypted_payload, None)
            payload = json.loads(decrypted_bytes.decode())

            return payload
        except Exception as e:
            raise ValueError("Invalid authorization code") from e

    @staticmethod
    def validate_authorization_code(auth_code: str, client_id: str):
        """Validates the authorization code and checks claims"""
        try:
            payload = AuthorizationCodeService.decrypt_authorization_code(auth_code)
            iss = flask.current_app.config.get('ISSUER_NAME')

            now = int(datetime.datetime.utcnow().timestamp())

            # Validate claims
            if payload.get("client_id") != client_id:
                raise ValueError("Client ID mismatch")

            if payload.get("iss") != iss:
                raise ValueError("Invalid issuer")

            if now < payload.get("nbf"):
                raise ValueError("Authorization code is not yet valid")

            if now > payload.get("exp"):
                raise ValueError("Authorization code has expired")

            return payload

        except Exception as e:
            raise ValueError(f"Authorization code validation failed: {str(e)}") from e
