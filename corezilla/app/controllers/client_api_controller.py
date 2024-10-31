import http

from flask import jsonify
from flask.views import MethodView
from flask_login import login_required, current_user
from flask_smorest import Blueprint
from flask_smorest.error_handler import ErrorSchema

from corezilla.app import db
from corezilla.app.models.Client import Client, ClientMetadata, ClientConfiguration
from corezilla.app.schemas.create_client_request_schema import CreateClientRequest
from corezilla.app.schemas.create_client_response_schema import ClientResponse, ClientResponseWrapperSchema
from corezilla.app.schemas.update_client_request_schema import UpdateClientRequest

client_api = Blueprint("clients", "clients", url_prefix="/api/clients", description="Client endpoints")


@client_api.route("/")
class ClientAPI(MethodView):
    @client_api.response(status_code=http.HTTPStatus.OK, schema=ClientResponse(many=True))
    @client_api.alt_response(status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY, schema=ErrorSchema, success=False)
    @login_required
    def get(self):
        """Retrieve all clients registered by the current user."""
        users_clients = Client.query.filter_by(user_id=current_user.user_id).all()

        # Format each client to match ClientResponse schema
        clients = [
            {
                "client_id": client.client_id,
                "name": client.client_name,
                "client_secret": client.client_secret,  # Assuming client_secret should be included in response
                "is_public": client.is_public,
                "client_type": client.app_type,
                "client_uri": client.client_uri,
                "metadata": {
                    "description": client.client_metadata.metadata_blob.get("description", ""),
                    "logo": client.client_metadata.metadata_blob.get("logo", ""),
                    "tos": client.client_metadata.metadata_blob.get("tos", ""),
                    "privacy_policy": client.client_metadata.metadata_blob.get("privacy policy", ""),
                    "security_contact": client.client_metadata.metadata_blob.get("security contact", ""),
                    "privacy_contact": client.client_metadata.metadata_blob.get("privacy contact", "")
                },
                "configuration": {
                    "oidc_conformant": client.client_configurations[0].configuration_blob.get("oidc_conformant", False),
                    "sender_constrained": client.client_configurations[0].configuration_blob.get("sender_constrained", False),
                    "token_endpoint_auth_method": client.client_configurations[0].configuration_blob.get("token_endpoint_auth_method", ""),
                    "uris": client.client_configurations[0].configuration_blob.get("uris", {}),
                    "cors": client.client_configurations[0].configuration_blob.get("cors", {}),
                    "refresh": client.client_configurations[0].configuration_blob.get("refresh", {}),
                    "jwt": client.client_configurations[0].configuration_blob.get("jwt", {})
                }
            }
            for client in users_clients
        ]

        return jsonify({"clients": clients})

    @client_api.arguments(CreateClientRequest, location="json", content_type="application/json")
    @client_api.response(status_code=http.HTTPStatus.CREATED, schema=ClientResponseWrapperSchema)
    @client_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    @login_required
    def post(self, args):
        """Create a new client."""
        # Initialize new client and metadata
        client = Client(owner=current_user, name=args.get("name"))
        db.session.add(client)
        db.session.commit()

        client_metadata = ClientMetadata(
            client_id=client.id,
            metadata_blob=args["metadata_blob"]
        )
        client_configuration = ClientConfiguration(
            client_id=client.id,
            configuration_blob=args["configuration_blob"]
        )

        # Save the new client and related data to the database
        db.session.add(client_metadata)
        db.session.add(client_configuration)
        db.session.commit()

        client_data = {
            "client_id": client.client_id,
            "name": client.client_name,
            "client_secret": client.client_secret,
            "is_public": client.is_public,
            "client_type": client.app_type,
            "client_uri": client.client_uri,
            "metadata_blob": client_metadata.metadata_blob,
            "configuration_blob": client_configuration.configuration_blob
        }

        client_response_data = ClientResponseWrapperSchema().dump({"client": client_data})

        return client_response_data

    @client_api.arguments(UpdateClientRequest, location="json", content_type="application/json")
    @client_api.response(status_code=http.HTTPStatus.OK, schema=ClientResponse)
    @client_api.alt_response(status_code=http.HTTPStatus.NOT_FOUND, schema=ErrorSchema, success=False)
    @login_required
    def put(self, args, client_id):
        """Replace an existing client given the client_id."""
        client = Client.query.filter_by(id=client_id).first_or_404()
        client_metadata = ClientMetadata.query.filter_by(client_id=client_id).first_or_404()
        client_configuration = ClientConfiguration.query.filter_by(client_id=client_id).first_or_404()

        # Replace all fields with new data
        client.client_name = args.get("name", client.client_name)
        client_metadata.metadata_blob = args["metadata_blob"]
        client_configuration.configuration_blob = args["configuration_blob"]

        db.session.commit()
        return client

    @client_api.arguments(UpdateClientRequest, location="json", content_type="application/json")
    @client_api.response(status_code=http.HTTPStatus.OK, schema=ClientResponse)
    @client_api.alt_response(status_code=http.HTTPStatus.NOT_FOUND, schema=ErrorSchema, success=False)
    @login_required
    def patch(self, args, client_id):
        """Partially update an existing client given the client_id."""
        client = Client.query.filter_by(id=client_id).first_or_404()
        client_metadata = ClientMetadata.query.filter_by(client_id=client_id).first_or_404()
        client_configuration = ClientConfiguration.query.filter_by(client_id=client_id).first_or_404()

        # Update only provided fields
        if "name" in args:
            client.client_name = args["name"]
        if "metadata_blob" in args:
            client_metadata.metadata_blob.update(args["metadata_blob"])
        if "configuration_blob" in args:
            client_configuration.configuration_blob.update(args["configuration_blob"])

        db.session.commit()
        return client

    @client_api.response(status_code=http.HTTPStatus.NO_CONTENT)
    @client_api.alt_response(status_code=http.HTTPStatus.NOT_FOUND, schema=ErrorSchema, success=False)
    @login_required
    def delete(self, client_id):
        """Delete an existing client given the client_id."""
        client = Client.query.filter_by(id=client_id).first_or_404()
        client_metadata = ClientMetadata.query.filter_by(client_id=client_id).first()
        client_configuration = ClientConfiguration.query.filter_by(client_id=client_id).first()

        # Remove client and related data
        if client_metadata:
            db.session.delete(client_metadata)
        if client_configuration:
            db.session.delete(client_configuration)
        db.session.delete(client)
        db.session.commit()

        return '', http.HTTPStatus.NO_CONTENT