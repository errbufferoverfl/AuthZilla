import uuid
from http import HTTPStatus

from flask import Blueprint, render_template, session, abort
from flask_login import login_required

from corezilla.app.models import Client
from corezilla.app.models.Connection import AuthenticationConnection

core_web = Blueprint('web', __name__)


@core_web.route('/')
@core_web.route('/dashboard', methods=['GET'])
def home():
    return render_template('index.html')


@core_web.route('/clients', methods=['GET'])
@login_required
def list_client_view():
    return render_template('clients.html')


@core_web.route('/connections', methods=['GET'])
@login_required
def list_connections_view():
    return render_template('connections.html')


@core_web.route('/clients/create', methods=['GET'])
@login_required
def create_client_view():
    # Generate a client ID on the backend
    client_id = str(uuid.uuid4())  # Or any other method of generating a client ID
    session['client_id'] = client_id  # Store the client_id in the session

    # Render the form and pass the client_id
    return render_template('get_client.html', client_id=client_id)


@core_web.route('/clients/<client_id>', methods=['GET'])
@login_required
def get_client_view(client_id):
    client = Client.query.filter_by(client_id=client_id).one()
    print(client)
    return render_template('get_client.html', client=client)


def get_connections_by_type(connection_type):
     """Fetch connections based on type (OIDC or SAML)."""
     return AuthenticationConnection.query.filter_by(type=connection_type.upper()).all()


@core_web.route('/connections/<connection_type>', methods=['GET'])
@login_required
def get_connection_view(connection_type):
    if connection_type.lower() not in ["oidc", "saml"]:
        return "Invalid connection type", 400

    return render_template('list_connections.html', connection_type=connection_type.upper())


def get_template_for_connection_type(connection_type):
    """Return the appropriate template for the given connection type."""
    templates = {
        "oidc": "create_oidc_connection.html",
        "saml": "create_saml_connection.html"
    }
    return templates.get(connection_type.lower())


@core_web.route('/connections/<connection_type>/new', methods=['GET'])
@login_required
def create_connection_view(connection_type):
    template = get_template_for_connection_type(connection_type)
    if not template:
        abort(400, description="Invalid connection type")
    return render_template(template)


@core_web.errorhandler(400)
def unauthorized_error(error):
    return render_template('400.html'), HTTPStatus.BAD_REQUEST


@core_web.errorhandler(401)
def unauthorized_error(error):
    return render_template('401.html'), HTTPStatus.UNAUTHORIZED


@core_web.errorhandler(404)
def unauthorized_error(error):
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@core_web.errorhandler(500)
def unauthorized_error(error):
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR