import http
import logging

from flask import request
from flask.views import MethodView
from flask_login import login_required, current_user
from flask_smorest import Blueprint
from flask_smorest.error_handler import ErrorSchema
from sqlalchemy.exc import SQLAlchemyError

from corezilla.app import db
from corezilla.app.models.Client import Client, ClientMetadata, ClientConfiguration
from corezilla.app.schemas.create_client_request_schema import CreateClientRequest, ReadClientRequest
from corezilla.app.schemas.create_client_response_schema import CreateClientResponseSchema, GetClientResponseSchema, ClientMetadataResponseSchema, ClientConfigurationResponseSchema
from corezilla.app.schemas.update_client_request_schema import UpdateClientRequest

client_api = Blueprint("clients", "clients", url_prefix="/api/clients", description="Client endpoints")


@client_api.route("/")
class ClientsAPI(MethodView):
    @client_api.arguments(ReadClientRequest, location="query", description="Retrieve a list of all OAuth clients associated with the authenticated user.")
    @client_api.response(status_code=http.HTTPStatus.OK, schema=GetClientResponseSchema(), examples={
        "Returning Multiple Clients": {
            "value": {
                "clients": [{
                "client_id": "cl-ab12cd34ef56gh78",
                "name": "My Example App",
                "client_secret": "AZL-SOxY9zQqPzhXP-z-f-fxfnCvlvqlJil99NaQjLLEcRcQMY6lcj0IDV-4aWEa_HDgsQy09ZHCqH6xVfSWbQ0SN_W3dVc7_2zqNbf_a3CpFvj6WsN8fPPVIbk6iKv5WqkNT1UqcVz1QpmVWZbr4bl1OR3kqDVSZeijV6X6NICkdtg",
                "is_public": True,
                "client_type": "regular_web",
                "client_uri": "https://example.com",
                "metadata": {
                    "description": "An example application that demonstrates OAuth flow.",
                    "logo": "https://example.com/logo.png",
                    "tos": "https://example.com/tos",
                    "privacy_policy": "https://example.com/privacy",
                    "security_contact": "security@example.com",
                    "privacy_contact": "privacy@example.com"
                },
                "configuration": {
                    "oidc_conformant": True,
                    "sender_constrained": True,
                    "token_endpoint_auth_method": "client_secret_basic",
                    "uris": {
                        "app_login_uri": "https://example.com/login",
                        "redirect_uris": [
                            "https://example.com/callback",
                            "https://example.com/redirect"
                        ],
                        "logout_uris": ["https://example.com/logout"],
                        "web_origins": ["https://example.com"]
                    },
                    "cors": {
                        "is_enabled": "true",
                        "allowed_origins": ["https://example.com", "https://anotherexample.com"],
                        "fallback_url": "https://example.com/cors-fallback"
                    },
                    "refresh": {
                        "refresh_token_rotation_enabled": True,
                        "rotation_overlap_period": 300,
                        "idle_refresh_token_lifetime_enabled": True,
                        "idle_refresh_token_lifetime": 1296000,
                        "maximum_refresh_token_lifetime_enabled": True,
                        "maximum_refresh_token_lifetime": 2592000
                    },
                    "jwt": {
                        "algorithm": "RS256"
                    }
                },
                "_links": {
                    "self": "https://api.example.com/clients/cl-ab12cd34ef56gh78"
                }
            }, {
                "client_id": "cl-ijklmn12op34qrst",
                "name": "Sample Mobile App",
                "client_secret": "AZL-XYZJ09f8e-WdfxlyvMf43vh4XJq9RtAq67RNT0xa9HfQ13pL6Q08bX7MeWxBjsQIWK-XFb6jcnKfZe_GNVl08yRqK_HFz-UZnD6TiHvye9MlX26P82iYwNls",
                "is_public": False,
                "client_type": "native",
                "client_uri": "https://mobile.example.com",
                "metadata": {
                    "description": "Mobile client for seamless OAuth integration.",
                    "logo": "https://mobile.example.com/logo.png",
                    "tos": "https://mobile.example.com/tos",
                    "privacy_policy": "https://mobile.example.com/privacy",
                    "security_contact": "security@mobile.example.com",
                    "privacy_contact": "privacy@mobile.example.com"
                },
                "configuration": {
                    "oidc_conformant": False,
                    "sender_constrained": False,
                    "token_endpoint_auth_method": "client_secret_post",
                    "uris": {
                        "app_login_uri": "https://mobile.example.com/login",
                        "redirect_uris": ["myapp://callback"],
                        "logout_uris": ["myapp://logout"],
                        "web_origins": ["https://mobile.example.com"]
                    },
                    "cors": {
                        "is_enabled": False,
                        "allowed_origins": [],
                        "fallback_url": ""
                    },
                    "refresh": {
                        "refresh_token_rotation_enabled": False,
                        "rotation_overlap_period": 0,
                        "idle_refresh_token_lifetime_enabled": True,
                        "idle_refresh_token_lifetime": 86400,
                        "maximum_refresh_token_lifetime_enabled": False,
                        "maximum_refresh_token_lifetime": 604800
                    },
                    "jwt": {
                        "algorithm": "HS256"
                    }
                },
                "_links": {
                    "self": "https://api.example.com/clients/cl-ijklmn12op34qrst"
                },
            }],
                "page": 1,
                "per_page": 50,
                "total": 0
        },
        },
        "Returning No Clients": {
            "value": {"clients": [],
                      "page": 1,
                      "per_page": 50,
                      "total": 0},
        }})
    @client_api.alt_response(status_code=http.HTTPStatus.UNAUTHORIZED, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY, schema=ErrorSchema, success=False)
    @login_required
    def get(self, args):
        """Get Clients"""
        # Retrieve pagination parameters, with defaults
        page: int = args.get("page", 1)
        per_page: int = args.get("per_page", 50)

        # Query the database for the user's clients, with pagination
        paginated_clients = Client.query.filter_by(user_id=current_user.user_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Fetch the latest metadata and configuration for each client
        clients_data = []
        for client in paginated_clients.items:
            # Fetch the latest metadata
            metadata = (
                ClientMetadata.query.filter_by(client_id=client.id)
                .first()
            )
            metadata = ClientMetadataResponseSchema().load(metadata.metadata_blob, many=False)

            # Fetch the latest configuration
            configuration = (
                ClientConfiguration.query.filter_by(client_id=client.id)
                .order_by(ClientConfiguration.version.desc())
                .first()
            )
            configuration = ClientConfigurationResponseSchema().load(configuration.configuration_blob, many=False)

            # Append client data with metadata and configuration to the list
            clients_data.append({
                "client_id": client.client_id,
                "name": client.client_name,
                "client_secret": client.client_secret,
                "is_public": client.is_public,
                "client_type": client.app_type,
                "client_uri": client.client_uri,

                "metadata": metadata,
                "configuration": configuration,
            })

        # Serialize client data and prepare pagination details
        serialized_clients = CreateClientResponseSchema().dump(clients_data, many=True)

        response = {
            "clients": serialized_clients,
            "page": page,
            "per_page": per_page,
            "total": paginated_clients.total,
        }

        return response, http.HTTPStatus.OK

    @client_api.arguments(CreateClientRequest, location="json", content_type="application/json")
    @client_api.response(status_code=http.HTTPStatus.CREATED, schema=CreateClientResponseSchema, example={
            "client": {
                "client_id": "cl-ab12cd34ef56gh78",
                "name": "My Example App",
                "client_secret": "AZL-SOxY9zQqPzhXP-z-f-fxfnCvlvqlJil99NaQjLLEcRcQMY6lcj0IDV-4aWEa_HDgsQy09ZHCqH6xVfSWbQ0SN_W3dVc7_2zqNbf_a3CpFvj6WsN8fPPVIbk6iKv5WqkNT1UqcVz1QpmVWZbr4bl1OR3kqDVSZeijV6X6NICkdtg",
                "is_public": True,
                "client_type": "regular_web",
                "client_uri": "https://example.com",
                "metadata": {
                    "description": "An example application that demonstrates OAuth flow.",
                    "logo": "https://example.com/logo.png",
                    "tos": "https://example.com/tos",
                    "privacy_policy": "https://example.com/privacy",
                    "security_contact": "security@example.com",
                    "privacy_contact": "privacy@example.com"
                },
                "configuration": {
                    "oidc_conformant": True,
                    "sender_constrained": False,
                    "token_endpoint_auth_method": "client_secret_basic",
                    "uris": {
                        "app_login_uri": "https://example.com/login",
                        "redirect_uris": [
                            "https://example.com/callback"
                        ],
                        "logout_uris": ["https://example.com/logout"],
                        "web_origins": ["https://example.com"]
                    },
                    "cors": {
                        "is_enabled": False,
                        "allowed_origins": ["https://example.com"],
                        "fallback_url": "https://example.com/fallback"
                    },
                    "refresh": {
                        "refresh_token_rotation_enabled": False,
                        "rotation_overlap_period": 0,
                        "idle_refresh_token_lifetime_enabled": False,
                        "idle_refresh_token_lifetime": 1296000,
                        "maximum_refresh_token_lifetime_enabled": False,
                        "maximum_refresh_token_lifetime": 2592000
                    },
                    "jwt": {
                        "algorithm": "RS256"
                    }
                },
                "_links": {
                    "self": "https://api.example.com/clients/cl-ab12cd34ef56gh78"
                }
            }
        })
    @client_api.alt_response(status_code=http.HTTPStatus.UNAUTHORIZED, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY, schema=ErrorSchema, success=False)
    @login_required
    def post(self, args):
        """Create a client"""
        client = Client(
            owner=current_user,
            name=args.get("name"),
        )

        db.session.add(client)
        db.session.commit()

        default_metadata = {
            "description": "",
            "logo": "/images/sample_logo.png",
            "tos": "",
            "privacy_policy": "",
            "security_contact": "",
            "privacy_contact": ""
        }

        client_metadata = ClientMetadata(
            client_id=client.id,
            metadata_blob=default_metadata
        )

        default_configuration = {
            "oidc_conformant": True,
            "sender_constrained": False,
            "token_endpoint_auth_method": "authorization_code",
            "uris": {
                "app_login_uri": "",
                "redirect_uris": [],
                "logout_uris": [],
                "web_origins": []
            },
            "cors": {
                "is_enabled": False,
                "allowed_origins": [],
                "fallback_url": ""
            },
            "refresh": {
                "refresh_token_rotation_enabled": False,
                "rotation_overlap_period": 0,
                "idle_refresh_token_lifetime_enabled": False,
                "idle_refresh_token_lifetime": 1296000,
                "maximum_refresh_token_lifetime_enabled": False,
                "maximum_refresh_token_lifetime": 2592000
            },
            "jwt": {
                "algorithm": "RS256"
            }
        }

        client_configuration = ClientConfiguration(
            client_id=client.id,
            configuration_blob=default_configuration
        )

        # Save the new client and related data to the database
        db.session.add(client_metadata)
        db.session.add(client_configuration)
        db.session.commit()

        serialised_client_configuration_response = ClientConfigurationResponseSchema().load(client_configuration.configuration_blob)
        serialised_client_metadata_response = ClientMetadataResponseSchema().load(client_metadata.metadata_blob)

        client_data = {
            "client_id": client.client_id,
            "name": client.client_name,
            "client_secret": client.client_secret,
            "is_public": client.is_public,
            "client_type": client.app_type,
            "client_uri": client.client_uri,

            "metadata": serialised_client_metadata_response,
            "configuration": serialised_client_configuration_response
        }

        response = CreateClientResponseSchema().dump(client_data)

        return response, http.HTTPStatus.CREATED


@client_api.route("/<client_id>")
class ClientAPI(MethodView):
    @client_api.response(status_code=http.HTTPStatus.OK, schema=CreateClientResponseSchema)
    @client_api.alt_response(status_code=http.HTTPStatus.UNAUTHORIZED, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY, schema=ErrorSchema, success=False)
    @login_required
    def get(self, client_id):
        """Get client by id"""
        if not client_id:
            return {
                'code': 400,
                'status': 'Bad Request',
                'message': 'Missing required parameter: client_id',
                'errors': {}
            }, http.HTTPStatus.BAD_REQUEST

        client = Client.query.filter_by(client_id=client_id, user_id=current_user.user_id).first()

        if not client:
            return {
                'code': 404,
                'status': 'Not Found',
                'message': f'Client {client_id} not found',
                'errors': {}
            }, http.HTTPStatus.NOT_FOUND

        client_data = {
            "client_id": client.client_id,
            "name": client.client_name,
            "client_secret": client.client_secret,
            "is_public": client.is_public,
            "client_type": client.app_type,
            "client_uri": client.client_uri,

            "metadata": client.client_metadata.metadata_blob,
            "configuration": client.client_configurations[0].configuration_blob
        }

        response = CreateClientResponseSchema().dump(client_data)

        return response

    @client_api.arguments(UpdateClientRequest, location="json", content_type="application/json")
    @client_api.response(status_code=http.HTTPStatus.OK, schema=CreateClientResponseSchema)
    @client_api.alt_response(status_code=http.HTTPStatus.UNAUTHORIZED, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY, schema=ErrorSchema, success=False)
    @login_required
    def put(self, args, client_id):
        """Update a client"""
        if not client_id:
            return {
                'code': 400,
                'status': 'Bad Request',
                'message': 'Missing required parameter: client_id',
                'errors': {}
            }, http.HTTPStatus.BAD_REQUEST

        client = Client.query.filter_by(client_id=client_id, user_id=current_user.user_id).first()

        if not client:
            return {
                'code': 404,
                'status': 'Not Found',
                'message': f'Client {client_id} not found',
                'errors': {}
            }, http.HTTPStatus.NOT_FOUND

        client_metadata = ClientMetadata.query.filter_by(client_id=client_id).first()
        client_configuration = ClientConfiguration.query.filter_by(client_id=client_id).first()

        # Replace all fields with new data
        client.client_name = args.get("name", client.client_name)
        client.client_uri = args.get("uri", client.client_uri)

        # TODO: Add in support for changing visibility

        client.app_type = args.get("type", client.app_type)

        client_metadata.metadata_blob = args["metadata_blob"]
        client_configuration.configuration_blob = args["configuration_blob"]

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error("Database commit failed. Rolling back the session.", exc_info=True)
            raise Exception("An error occurred while committing to the database. Please try again later.") from e

        response = CreateClientResponseSchema().dump(client)

        return response

    @client_api.arguments(UpdateClientRequest, location="json", content_type="application/json")
    @client_api.response(status_code=http.HTTPStatus.OK, schema=CreateClientResponseSchema)
    @client_api.alt_response(status_code=http.HTTPStatus.UNAUTHORIZED, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY, schema=ErrorSchema, success=False)
    @login_required
    def patch(self, args, client_id):
        """Update client configuration"""
        logging.info(f"PATCH request received. Client ID: {client_id}, Request IP: {request.remote_addr}")

        if not client_id:
            logging.warning(f"Missing required parameter: client_id. Request IP: {request.remote_addr}")
            return {
                'code': 400,
                'status': 'Bad Request',
                'message': 'Missing required parameter: client_id',
                'errors': {}
            }, http.HTTPStatus.BAD_REQUEST

        # Fetch client and verify ownership
        client = Client.query.filter_by(client_id=client_id, user_id=current_user.user_id).first()
        if not client:
            logging.warning(f"Client ID {client_id} not found for user ID {current_user.user_id}. Request IP: {request.remote_addr}")
            return {
                'code': 404,
                'status': 'Not Found',
                'message': f'Client {client_id} not found',
                'errors': {}
            }, http.HTTPStatus.NOT_FOUND

        # Log successful retrieval of the client
        logging.info(f"Client ID {client_id} found for user ID {current_user.user_id}. Proceeding with update.")

        try:
            client_metadata = ClientMetadata.query.filter_by(client_id=client_id).first_or_404()
            client_configuration = ClientConfiguration.query.filter_by(client_id=client_id).first_or_404()

            # Update only provided fields
            if "name" in args:
                old_name = client.client_name
                new_name = args.get("name")
                client.client_name = new_name
                logging.info(f"Updated client name for client ID {client_id} from '{old_name}' to '{new_name}'")

            if "metadata_blob" in args:
                old_metadata = client_metadata.metadata_blob
                new_metadata = args.get("metadata_blob")
                client_metadata.metadata_blob.update(new_metadata)
                logging.info(f"Updated metadata_blob for client ID {client_id}. Old value: {old_metadata}, New value: {new_metadata}")

            if "configuration_blob" in args:
                old_configuration = client_configuration.configuration_blob
                new_configuration = args.get("configuration_blob")
                client_configuration.configuration_blob.update(new_configuration)
                logging.info(f"Updated configuration_blob for client ID {client_id}. Old value: {old_configuration}, New value: {new_configuration}")

            # Commit changes to the database
            db.session.commit()
            logging.info(f"Successfully updated client configuration for client ID {client_id}.")

            client_response_data = GetClientResponseSchema().dump({"client": client})
            logging.info(f"Response data prepared for client ID {client_id}. Returning response.")

            return client_response_data, http.HTTPStatus.OK

        except Exception as e:
            logging.error(f"Error occurred while updating client ID {client_id}. Error: {str(e)}", exc_info=True)
            return {
                'code': 500,
                'status': 'Internal Server Error',
                'message': 'An error occurred while updating the client configuration',
                'errors': {'details': str(e)}
            }, http.HTTPStatus.INTERNAL_SERVER_ERROR

    @client_api.response(status_code=http.HTTPStatus.NO_CONTENT)
    @client_api.alt_response(status_code=http.HTTPStatus.UNAUTHORIZED, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    @client_api.alt_response(status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY, schema=ErrorSchema, success=False)
    @login_required
    def delete(self, client_id):
        """Delete a client"""
        if not client_id:
            return {
                'code': 400,
                'status': 'Bad Request',
                'message': 'Missing required parameter: client_id',
                'errors': {}
            }, http.HTTPStatus.BAD_REQUEST

        client = Client.query.filter_by(client_id=client_id, user_id=current_user.user_id).first()

        if not client:
            return {
                'code': 404,
                'status': 'Not Found',
                'message': f'Client {client_id} not found',
                'errors': {}
            }, http.HTTPStatus.NOT_FOUND

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
