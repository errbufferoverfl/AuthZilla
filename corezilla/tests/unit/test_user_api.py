import http


def test_create_user_session_success(oauth_client, init_database):
    """
    Test creating a user session (login) with correct credentials.
    """
    # Simulate a login request with valid credentials
    response = oauth_client.put("/api/users/session", json={
        "username": "testuser",
        "password": "password123"
    })

    assert response.status_code == http.HTTPStatus.CREATED
    json_data = response.get_json()
    assert json_data['username'] == 'testuser'


def test_create_user_session_fail(oauth_client, init_database):
    """
    Test creating a user session (login) with incorrect credentials.
    """
    # Simulate a login request with invalid credentials
    response = oauth_client.put("/api/users/session", json={
        "username": "testuser",
        "password": "wrongpassword"
    })

    assert response.status_code == http.HTTPStatus.NO_CONTENT


def test_get_user_session_success(oauth_client, init_database):
    """
    Test retrieving current user session when logged in.
    """
    # Log in first
    response = oauth_client.put("/api/users/session", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == http.HTTPStatus.CREATED

    # Get the current user session
    response = oauth_client.get("/api/users/session/me")
    assert response.status_code == http.HTTPStatus.FOUND
    json_data = response.get_json()
    assert json_data['username'] == 'testuser'


def test_get_user_session_unauthorized(oauth_client):
    """
    Test retrieving current user session when not logged in.
    """
    response = oauth_client.get("/api/users/session/me")
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_delete_user_session(oauth_client, init_database):
    """
    Test logging out (deleting session).
    """
    # Log in first
    response = oauth_client.put("/api/users/session", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == http.HTTPStatus.CREATED

    # Now log out
    response = oauth_client.delete("/api/users/session/me")
    assert response.status_code == http.HTTPStatus.NO_CONTENT


def test_create_user_already_exists(oauth_client, init_database):
    """
    Test trying to create a user that already exists.
    """
    response = oauth_client.put("/api/users", json={
        "username": "testuser",
        "password": "newpassword"
    })

    assert response.status_code == http.HTTPStatus.CONFLICT


def test_create_new_user_success(oauth_client):
    """
    Test creating a new user successfully.
    """
    response = oauth_client.put("/api/users", json={
        "username": "newuser",
        "password": "password123"
    })

    assert response.status_code == http.HTTPStatus.CREATED
    json_data = response.get_json()
    assert json_data['username'] == 'newuser'
