import uuid
from http import HTTPStatus

from flask import Blueprint, render_template, session
from flask_login import login_required

core_web = Blueprint('web', __name__)


@core_web.route('/')
def home():
    return render_template('index.html')


@core_web.route('/clients', methods=['GET'])
@core_web.route('/dashboard', methods=['GET'])
@login_required
def list_client_view():
    return render_template('client.html')


@core_web.route('/clients/create', methods=['GET'])
@login_required
def create_client_view():
    # Generate a client ID on the backend
    client_id = str(uuid.uuid4())  # Or any other method of generating a client ID
    session['client_id'] = client_id  # Store the client_id in the session

    # Render the form and pass the client_id
    return render_template('create_client.html', client_id=client_id)


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