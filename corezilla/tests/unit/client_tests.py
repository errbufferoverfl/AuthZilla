import json
import pytest
from http import HTTPStatus
from corezilla.app.models.Client import Client, ClientMetadata, ClientConfiguration


@pytest.mark.usefixtures("client", "user", "db_session")
class TestClientsAPI:

    def test_get_clients(self, client, app, user):
        with app.test_client() as test_client:
            # Simulate login by setting session variables directly
            with test_client.session_transaction() as session:
                session['_user_id'] = str(user.user_id)  # Use correct field for user identification
                session['_fresh'] = True  # Ensure the session is marked as fresh

            # GET request to retrieve clients
            response = test_client.get('/api/clients/')
            data = response.get_json()

            # Assertions
            assert response.status_code == HTTPStatus.OK
            assert "clients" in data
            assert len(data["clients"]) >= 1
            assert data["clients"][0]["name"] == "Test Client"

            # Assertions about the REST pagination
            assert data.get("page") == 1
            assert data.get("per_page") == 50
            assert len(data["clients"]) == data.get("total")

            ## Assertions about the REST link
            assert data["clients"][0]["_links"]["self"] == f"/api/clients/{data['client_id']}"


    def test_post_create_client(self, app, user):
        with app.test_client() as test_client:
            # Simulate login by setting session variables directly
            with test_client.session_transaction() as session:
                session['_user_id'] = str(user.user_id)  # Use correct field for user identification
                session['_fresh'] = True  # Ensure the session is marked as fresh

            # POST request to create a new client
            new_client_data = {
                "name": "New Test Client",
                "metadata_blob": {
                    "description": "New client for testing",
                    "logo": "https://example.com/logo.png"
                },
                "configuration_blob": {
                    "oidc_conformant": True,
                    "sender_constrained": True,
                    "token_endpoint_auth_method": "client_secret_basic",
                    "uris": {
                        "app_login_uri": "https://example.com/login",
                        "redirect_uris": ["https://example.com/callback"],
                        "logout_uris": ["https://example.com/logout"]
                    },
                    "cors": {
                        "is_enabled": True,
                        "allowed_origins": ["https://example.com"]
                    },
                    "refresh": {
                        "refresh_token_rotation_enabled": True
                    },
                    "jwt": {
                        "algorithm": "RS256"
                    }
                }
            }

            response = test_client.post(
                '/api/clients/',
                data=json.dumps(new_client_data),
                content_type="application/json"
            )

            # Assertions
            assert response.status_code == HTTPStatus.CREATED
            data = response.get_json()
            assert "client" in data
            assert data["client"]["name"] == "New Test Client"

    def test_get_single_client(self, client, app, user):
        with app.test_client() as test_client:
            # Simulate login by setting session variables directly
            with test_client.session_transaction() as session:
                session['_user_id'] = str(user.user_id)  # Use correct field for user identification
                session['_fresh'] = True  # Ensure the session is marked as fresh

            # GET request for a single client
            response = test_client.get(f'/api/clients/{client.client_id}')
            data = response.get_json()

            # Assertions
            assert response.status_code == HTTPStatus.OK
            assert "client" in data
            assert data["client"]["client_id"] == client.client_id

    def test_put_update_client(self, client, app, user):
        with app.test_client() as test_client:
            # Simulate login
            with test_client.session_transaction() as session:
                session['user_id'] = user.user_id

            # PUT request to update the client
            updated_data = {
                "name": "Updated Test Client",
                "metadata_blob": {
                    "description": "Updated description"
                },
                "configuration_blob": {
                    "oidc_conformant": False
                }
            }

            response = test_client.put(
                f'/api/clients/{client.client_id}',
                data=json.dumps(updated_data),
                content_type="application/json"
            )

            # Assertions
            assert response.status_code == HTTPStatus.OK
            data = response.get_json()
            assert "client" in data
            assert data["client"]["name"] == "Updated Test Client"
            assert data["client"]["metadata"]["description"] == "Updated description"

    def test_patch_partial_update_client(self, client, app, user):
        with app.test_client() as test_client:
            # Simulate login by setting session variables directly
            with test_client.session_transaction() as session:
                session['_user_id'] = str(user.user_id)  # Use correct field for user identification
                session['_fresh'] = True  # Ensure the session is marked as fresh

            # PATCH request for partial update
            partial_update_data = {
                "name": "Partially Updated Client",
                "metadata_blob": {"description": "Partially updated description"}
            }

            response = test_client.patch(
                f'/api/clients/{client.client_id}',
                data=json.dumps(partial_update_data),
                content_type="application/json"
            )

            # Assertions
            assert response.status_code == HTTPStatus.OK
            data = response.get_json()
            assert "client" in data
            assert data["client"]["name"] == "Partially Updated Client"
            assert data["client"]["metadata"]["description"] == "Partially updated description"

    def test_delete_client(self, client, app, user):
        with app.test_client() as test_client:
            # Simulate login by setting session variables directly
            with test_client.session_transaction() as session:
                session['_user_id'] = str(user.user_id)  # Use correct field for user identification
                session['_fresh'] = True  # Ensure the session is marked as fresh

            # DELETE request for client deletion
            response = test_client.delete(f'/api/clients/{client.client_id}')

            # Assertions
            assert response.status_code == HTTPStatus.NO_CONTENT

            # Confirm deletion
            response = test_client.get(f'/api/clients/{client.client_id}')
            assert response.status_code == HTTPStatus.NOT_FOUND
