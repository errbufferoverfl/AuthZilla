import http


def test_create_user_session_success(client, init_database):
    """
    Test creating a user session (login) with correct credentials.
    """
    # Simulate a login request with valid credentials
    response = client.put("/api/users/session", json={
        "username": "testuser",
        "password": "password123"
    })

    assert response.status_code == http.HTTPStatus.CREATED
    json_data = response.get_json()
    assert json_data['username'] == 'testuser'


def test_create_user_session_fail(client, init_database):
    """
    Test creating a user session (login) with incorrect credentials.
    """
    # Simulate a login request with invalid credentials
    response = client.put("/api/users/session", json={
        "username": "testuser",
        "password": "wrongpassword"
    })

    assert response.status_code == http.HTTPStatus.NO_CONTENT


def test_get_user_session_success(client, init_database):
    """
    Test retrieving current user session when logged in.
    """
    # Log in first
    response = client.put("/api/users/session", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == http.HTTPStatus.CREATED

    # Get the current user session
    response = client.get("/api/users/session/me")
    assert response.status_code == http.HTTPStatus.FOUND
    json_data = response.get_json()
    assert json_data['username'] == 'testuser'


def test_get_user_session_unauthorized(client):
    """
    Test retrieving current user session when not logged in.
    """
    response = client.get("/api/users/session/me")
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_delete_user_session(client, init_database):
    """
    Test logging out (deleting session).
    """
    # Log in first
    response = client.put("/api/users/session", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == http.HTTPStatus.CREATED

    # Now log out
    response = client.delete("/api/users/session/me")
    assert response.status_code == http.HTTPStatus.NO_CONTENT


def test_create_user_already_exists(client, init_database):
    """
    Test trying to create a user that already exists.
    """
    response = client.put("/api/users", json={
        "username": "testuser",
        "password": "newpassword"
    })

    assert response.status_code == http.HTTPStatus.CONFLICT


def test_create_new_user_success(client):
    """
    Test creating a new user successfully.
    """
    response = client.put("/api/users", json={
        "username": "newuser",
        "password": "password123"
    })

    assert response.status_code == http.HTTPStatus.CREATED
    json_data = response.get_json()
    assert json_data['username'] == 'newuser'
