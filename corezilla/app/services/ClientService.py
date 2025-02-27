from urllib.parse import urlparse

from corezilla.app.models.Client import Client, ClientConfiguration


class ClientService:
    @staticmethod
    def get_client(client_id):
        """
        Retrieve a client by its client_id.
        """
        return Client.query.filter_by(client_id=client_id).first()

    @staticmethod
    def verify_client(client_id, client_secret):
        """
        Verify client credentials.
        """
        client = ClientService.get_client(client_id)
        if client and client.verify_secret(client_secret):
            return client
        return None

    @staticmethod
    def validate_authorization_code(client, code, redirect_uri):
        """
        Validate an authorization code for a given client and redirect URI.
        """
        auth_code = client.get_authorization_code(code)
        if auth_code and auth_code.is_valid(redirect_uri):
            return auth_code
        return None

    @staticmethod
    def validate_refresh_token(client, refresh_token):
        """
        Validate a refresh token for a given client.
        """
        return client.get_refresh_token(refresh_token)

    @staticmethod
    def generate_access_token(client):
        """
        Generate an access token for a client.
        """
        return client.create_access_token()

    @staticmethod
    def generate_refresh_token(client):
        """
        Generate a refresh token for a client.
        """
        return client.create_refresh_token()

    @staticmethod
    def get_client_configuration(client_id):
        ClientConfiguration.query.filter_by(client_id=client_id).order_by(ClientConfiguration.version.desc()).first()

    @staticmethod
    def validate_resource_uris(resource):
        """
        Validate resource URIs according to RFC 8707:
        - Must be an absolute URI
        - Must not include a fragment component
        """
        if isinstance(resource, str):
            resource = [resource]  # Convert single string to list

        if not isinstance(resource, list):
            raise ValueError("resource parameter must be a string or a list of strings.")

        valid_resources = []

        for res in resource:
            parsed = urlparse(res)

            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid resource URI: {res}. Must be an absolute URI.")

            if parsed.fragment:
                raise ValueError(f"Invalid resource URI: {res}. Must not include a fragment component.")

            valid_resources.append(res)

        return valid_resources

    @staticmethod
    def is_absolute_uri(uri):
        parsed = urlparse(uri)
        return bool(parsed.scheme and parsed.netloc)

    @staticmethod
    def generate_authorization_code(client_id, user_id):
        """Generate and store an authorization code."""
        code = secrets.token_urlsafe(32)  # Generate a secure random authorization code
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)  # 10 min expiry

        # Store the authorization code in the database or cache
        AuthorizationCodeService.store(
            code=code,
            client_id=client_id,
            user_id=user_id,
            expires_at=expires_at
        )

        return code

