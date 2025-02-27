import pytest
import http
from flask import url_for
from corezilla.app.services.TokenService import TokenService
from corezilla.app.services.ClientService import ClientService
from corezilla.app.services.AuthorizationCodeService import AuthorizationCodeService


@pytest.mark.usefixtures("oauth_client", "user", "db_session")
class TestAuthorizationApi:

    def test_authorization_endpoint_authenticated(self, app, user, client, oauth_client, db_session):
        """Test the authorization endpoint with an authenticated user."""
        with app.test_client() as test_client:
            # Simulate login by setting session variables directly
            with test_client.session_transaction() as session:
                session['_user_id'] = str(user.user_id)  # Use correct field for user identification
                session['_fresh'] = True  # Ensure the session is marked as fresh

            client_id = oauth_client.client_id

            # Include session cookie for subsequent requests
            response = test_client.get(
                url_for("oauth.AuthorizationApi"),
                query_string={
                    "client_id": client_id,
                    "response_type": "code",
                    "redirect_uri": "https://example.com/callback"
                },
                follow_redirects=False
            )

            print(response.data)
            assert response.status_code == http.HTTPStatus.FOUND
            assert "code=" in response.location

    def test_authorization_endpoint_invalid_client(self, client):
        """Test authorization endpoint with an invalid client_id."""
        response = client.get(
            url_for("oauth.authorize"),
            query_string={
                "client_id": "invalid_client",
                "response_type": "code",
                "redirect_uri": "https://example.com/callback"
            }
        )
        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert "invalid_client" in response.json["status"]

    def test_token_endpoint_valid_code(self, client, oauth_client, user, db_session):
        """Test token endpoint with a valid authorization code."""
        authorization_code = AuthorizationCodeService.generate_authorization_code(oauth_client.client_id, user.id)
        response = client.post(
            url_for("oauth.token"),
            data={
                "grant_type": "authorization_code",
                "client_id": oauth_client.client_id,
                "client_secret": "test_secret",
                "code": authorization_code,
                "redirect_uri": "https://example.com/callback"
            }
        )
        assert response.status_code == http.HTTPStatus.OK
        assert "access_token" in response.json

    def test_token_endpoint_invalid_grant_type(self, client):
        """Test token endpoint with an unsupported grant type."""
        response = client.post(
            url_for("oauth.token"),
            data={
                "grant_type": "invalid_grant",
                "client_id": "test_client",
                "client_secret": "test_secret"
            }
        )
        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert "invalid_request" in response.json["status"]

    def test_introspect_active_token(self, client, oauth_client, user, db_session):
        """Test token introspection endpoint with an active token."""
        access_token = TokenService.generate_jwt({"sub": user.id, "client_id": oauth_client.client_id}, 3600)
        response = client.post(
            url_for("oauth.IntrospectionApi"),
            data={"token": access_token}
        )
        assert response.status_code == http.HTTPStatus.OK
        assert response.json["active"] is True

    def test_revoke_token(self, client, oauth_client, user, db_session):
        """Test token revocation endpoint."""
        access_token = TokenService.generate_jwt({"sub": user.id, "client_id": oauth_client.client_id}, 3600)
        response = client.post(
            url_for("oauth.RevocationApi"),
            data={"token": access_token}
        )
        assert response.status_code == http.HTTPStatus.NO_CONTENT
