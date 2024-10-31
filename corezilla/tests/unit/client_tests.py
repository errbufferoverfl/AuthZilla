import pytest
from flask import url_for

from corezilla.app.models.User import Client, ClientMetadata


def test_client_creation(new_user):
    """
    GIVEN a Client model
    WHEN a new Client is created
    THEN check the name, authentication method, and grant types are defined correctly
    """
    client_one = Client("Test Client 1", 0, ["authorization_code", ], new_user.user_id)

    assert client_one.id is not None
    assert client_one.client_name == "Test Client 1"
    assert client_one.auth_method == 0
    assert client_one.grant_types == "['authorization_code']"
    assert client_one.owner_id == new_user.user_id


def test_client_creation_no_owner():
    """
    GIVEN a Client model
    WHEN a new Client is created without an owner
    THEN raise a TypeError
    """
    with pytest.raises(TypeError) as err:
        client_one = Client("", 0, ["authorization_code", ], )


def test_client_creation_sneaky_no_owner():
    """
    GIVEN a Client model
    WHEN a new Client is created with a blank string, or None in the owner_id
    THEN raise a TypeError
    """
    with pytest.raises(TypeError) as err:
        client_one = Client("", 0, ["authorization_code", ], None)
    assert "Client must have a valid owner associated with it." in str(err.value)

    with pytest.raises(TypeError):
        client_one = Client("", 0, ["authorization_code", ], "")
    assert "Client must have a valid owner associated with it." in str(err.value)


def test_nameless_client_creation(new_user):
    """
    GIVEN a Client model
    WHEN a new Client is created without a client_name
    THEN check the client_id is returned in place of the client_name
    """
    client_one = Client("", 0, ["authorization_code", ], new_user.user_id)

    assert client_one.id is not None
    assert client_one.client_name == client_one.id


def test_get_clients_no_clients(test_client, mock_user):
    """Test the GET /api/clients route when no clients are registered."""
    response = test_client.get(url_for('clients.ClientAPI'))

    assert response.status_code == 200
    assert response.json == {"clients": []}, "Expected an empty client list"


def test_get_clients_with_clients(test_client, mock_user, mocker):
    """Test the GET /api/clients route with registered clients."""
    # Mocking some client data
    client = mocker.Mock(spec=Client)
    client.id = "mock-client-1"
    client.client_name = "Test Client"
    client_metadata = mocker.Mock(spec=ClientMetadata)
    client_metadata.client_uri = "https://test.com/callback"
    client_metadata.description = "Test Client Description"

    # Set the user's clients
    mock_user.clients = [client]
    mocker.patch.object(client, 'client_metadata', [client_metadata])

    response = test_client.get(url_for('clients.ClientAPI'))

    assert response.status_code == 200
    assert len(response.json['clients']) == 1
    assert response.json['clients'][0]['name'] == "Test Client"
    assert response.json['clients'][0]['client_id'] == "mock-client-1"
    assert response.json['clients'][0]['redirect_uri'] == "https://test.com/callback"


def test_create_client_success(test_client, mock_user, mocker):
    """Test the POST /api/clients route for successful client creation."""
    # Mock database session
    mock_db_session = mocker.patch('corezilla.app.db.session.add')
    mocker.patch('corezilla.app.db.session.commit')

    # Data to be sent in the request
    data = {
        "name": "My OAuth Client",
        "token_endpoint_auth_method": 1,
        "grant_types": ["authorization_code", "refresh_token"],
        "redirect_uri": "https://myapp.com/callback",
        "logo_uri": "https://myapp.com/logo.png",
        "contacts": ["admin@myapp.com"],
        "policy_uri": "https://myapp.com/policy",
        "tos_uri": "https://myapp.com/tos"
    }

    # Send POST request to create a client
    response = test_client.post(url_for('clients.ClientAPI'), json=data)

    # Check response and mock calls
    assert response.status_code == 201
    assert response.json['message'] == "Client created successfully"
    assert response.json['client']['name'] == "My OAuth Client"
    assert mock_db_session.called, "Expected database session to add the client"
    assert mock_user.fs_uniquifier == "mock-user-123", "Expected user ID to be set"


def test_create_client_validation_error(test_client, mock_user):
    """Test the POST /api/clients route when validation fails (missing fields)."""
    # Missing required fields
    data = {
        "name": "My OAuth Client",
        "grant_types": ["authorization_code"],  # Missing token_endpoint_auth_method
        "redirect_uri": "https://myapp.com/callback",
    }

    response = test_client.post(url_for('clients.ClientAPI'), json=data)

    # Check that validation fails and returns a 422 status code
    assert response.status_code == 422
    assert "token_endpoint_auth_method" in response.json["messages"]["json"], "Missing field should be reported"


def test_create_client_invalid_grant_type(test_client, mock_user):
    """Test the POST /api/clients route when an invalid grant type is provided."""
    data = {
        "name": "Invalid Client",
        "token_endpoint_auth_method": 1,
        "grant_types": ["invalid_grant_type"],
        "redirect_uri": "https://myapp.com/callback",
    }

    response = test_client.post(url_for('clients.ClientAPI'), json=data)

    # Check that the invalid grant type returns a 422 error
    assert response.status_code == 422
    assert "Invalid grant type" in response.json["messages"]["json"]["grant_types"][0]
