import pytest

from corezilla.app import create_app, db
from corezilla.app.models.User import User


@pytest.fixture
def app():
    app = create_app(config_object='corezilla.config.TestConfig')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

    with app.app_context():
        db.create_all()  # Create tables in the test database
        yield app
        db.drop_all()  # Drop all tables after the test


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def init_database(app):
    # Add a sample user to the test database
    with app.app_context():
        user = User(username='testuser', email='user@example.invalid', password='hashed_password')
        db.session.add(user)
        db.session.commit()
        yield db
        db.session.remove()


@pytest.fixture(scope='module')
def new_user(test_client):
    user = User('username@example.com', 'Password1!')
    return user


@pytest.fixture
def mock_user(mocker):
    """Fixture to mock the current_user with clients."""
    user = mocker.Mock()
    user.fs_uniquifier = "mock-user-123"
    user.clients = []  # Start with an empty client list
    mocker.patch('flask_login.utils._get_user', return_value=user)
    return user