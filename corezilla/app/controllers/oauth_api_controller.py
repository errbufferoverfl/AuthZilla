import http.client
from flask import request, jsonify, redirect
from flask.views import MethodView
from flask_smorest import Blueprint

from flask_smorest.error_handler import ErrorSchema
from flask_login import current_user

from corezilla.app.models import Client
from corezilla.app.schemas.oauth_schema import TokenResponseSchema, AuthorizationCodeRequest, AuthorizationCodeResponse

oauth_api = Blueprint("oauth", "oauth", url_prefix="/api/oauth", description="OAuth2 authorization endpoints")

def redirect_uri_factory(redirect_uri, **params):
    """Helper function to append query parameters to a redirect URI."""
    from urllib.parse import urlencode

    if params:
        redirect_uri = f"{redirect_uri}?{urlencode(params)}"
    return redirect(redirect_uri)


def handle_error(redirect_uri, error, description=None):
    """Helper function to handle redirect-based errors."""
    params = {"error": error}
    if description:
        params["error_description"] = description
    return redirect_uri_factory(redirect_uri, **params)

@oauth_api.route("/authorize")
class AuthorizationApi(MethodView):

    @oauth_api.arguments(AuthorizationCodeRequest, location="query" )
    @oauth_api.response(http.HTTPStatus.FOUND, schema=AuthorizationCodeResponse)
    @oauth_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    def get(self, args):
        """Authorization Endpoint (GET)

        The authorization endpoint is used to interact with the resource
        owner and obtain an authorization grant. The authorization server
        MUST first verify the identity of the resource owner.
        """

        # Ensure the user is authenticated before granting authorization
        if not current_user.is_authenticated:
            return handle_error(
                redirect_uri=args.get("redirect_uri"),
                error="unauthorized",
                description="User is not authenticated"
            )

        client_id = args.get("client_id")
        redirect_uri = args.get("redirect_uri")
        scope = args.get("scope")
        state = args.get("state")
        response_type = args.get("response_type")

        # Fetch additional ignored query parameters
        additional_params = {k: v for k, v in request.args.items() if k not in args}

        if state:
            additional_params["state"] = state

        # Validate 'client_id'
        if not client_id:
            return handle_error(redirect_uri, "invalid_request", "The request is missing the 'client_id' parameter.")

        requested_client = Client.query.filter_by(client_id=client_id).first()
        if not requested_client:
            return handle_error(redirect_uri, "access_denied", "Invalid client ID.")

        # Check ownership of the client
        if requested_client.owner_id != current_user.id:
            return handle_error(redirect_uri, "access_denied", "Access denied.")

        # Validate 'redirect_uri'
        if not redirect_uri:
            return handle_error(redirect_uri, "invalid_request", "The request is missing the 'redirect_uri' parameter.")

        # If all checks pass, return authorization successful
        return {"message": "Authorization successful", "additional_params": additional_params}, http.HTTPStatus.FOUND


@oauth_api.route("/token")
class TokenApi(MethodView):
    """
    The token endpoint is used by the client to obtain an access token using a grant.

    The token endpoint URL MUST NOT include a fragment component, and MAY include an
    application/x-www-form-urlencoded formatted query component

    The client MUST use the HTTP POST method when making requests to the token endpoint.

    The authorization server MUST ignore unrecognized request parameters sent to the token endpoint.

    Parameters sent without a value MUST be treated as if they were omitted from the request. Request and response
    parameters defined by this specification MUST NOT be included more than once.
    """

    @oauth_api.response(http.HTTPStatus.OK, TokenResponseSchema)
    @oauth_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    def post(self, args):
        if not current_user.is_authenticated:
            return {
                "code": http.HTTPStatus.UNAUTHORIZED,
                "status": "unauthorized",
                "message": "User is not authenticated",
                "errors": {}
            }, http.HTTPStatus.UNAUTHORIZED

