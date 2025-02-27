import http.client
from urllib.parse import urlencode

from flask import redirect
from flask import request
from flask.views import MethodView
from flask_login import current_user
from flask_smorest import Blueprint
from flask_smorest.error_handler import ErrorSchema

from corezilla.app.enums.ResponseTypeEnum import ResponseType
from corezilla.app.schemas.oauth_schema import AuthorizationCodeRequest, AuthorizationCodeResponse
from corezilla.app.schemas.oauth_schema import TokenResponseSchema
from corezilla.app.services.AuthorizationCodeService import AuthorizationCodeService
from corezilla.app.services.ClientService import ClientService
from corezilla.app.services.TokenService import TokenService
from corezilla.app.utils.handlers import handle_error

oauth_api = Blueprint("oauth", "oauth", url_prefix="/api/oauth", description="OAuth2 authorization endpoints")

def redirect_uri_factory(redirect_uri, **params):
    """Helper function to append query parameters to a redirect URI."""
    from urllib.parse import urlencode

    if params:
        redirect_uri = f"{redirect_uri}?{urlencode(params)}"
    return redirect(redirect_uri)


@oauth_api.route("/authorize")
class AuthorizationApi(MethodView):

    @oauth_api.arguments(AuthorizationCodeRequest, location="query" )
    @oauth_api.response(http.HTTPStatus.FOUND, schema=AuthorizationCodeResponse)
    @oauth_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    def get(self, args):
        """Authorization Endpoint (GET)

        https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1

        The authorization endpoint is used to interact with the resource
        owner and obtain an authorization grant. The authorization server
        MUST first verify the identity of the resource owner.
        """

        # Ensure the user is authenticated
        if not current_user.is_authenticated:
            return handle_error(
                redirect_uri=args.get("redirect_uri"),
                error="unauthorized",
                description="User is not authenticated"
            )

        client_id = args.get("client_id")
        redirect_uri = args.get("redirect_uri")
        scope = args.get("scope")
        response_type = args.get("response_type")
        resource = args.getlist("resource") if "resource" in request.args else []
        state = args.get("state")

        # Fetch additional ignored query parameters
        additional_params = {k: v for k, v in request.args.items() if k not in args}

        # Validate 'client_id'
        if not client_id:
            return handle_error(
                redirect_uri=None,
                error="invalid_request",
                description="Missing 'client_id' parameter.",
                state=state
            )

        # Validate 'response_type'
        if not response_type:
            return handle_error(
                redirect_uri=None,
                error="invalid_request",
                description="Missing 'response_type' parameter.",
                state=state
            )

        # Ensure 'response_type' is set to code.
        if response_type != ResponseType.CODE.value:
            return handle_error(
                redirect_uri=None,
                error="unsupported_response_type",
                description="Authorization code flow required.",
                state=state
            )

        requested_client = ClientService.get_client(client_id)
        if not requested_client:
            return handle_error(
                redirect_uri=None,
                error="invalid_client",
                description="Invalid client ID.",
                state=state
            )

        # If the client isn't public
        if not requested_client.is_public and requested_client.user_id != current_user.user_id:
                return handle_error(
                    redirect_uri=None,
                    error="access_denied",
                    description="Access Denied.",
                    state=state
                )

        requested_client_configuration = ClientService.get_client_configuration(client_id)
        if not requested_client_configuration:
            return handle_error(
                redirect_uri=None,
                error="not_found",
                description="No client configuration found for the provided client_id.",
                state=state
            )

        # https://www.ietf.org/archive/id/draft-ietf-oauth-v2-1-12.html#section-2.3.2
        # If multiple redirect URIs have been registered to a client, the client MUST include a redirect URI with
        # the authorization request using the redirect_uri request parameter (Section 4.1.1). If only a single
        # redirect URI has been registered to a client, the redirect_uri request parameter is optional.

        requested_client_redirect_uris = requested_client_configuration.configuration_blob.get("uris", {}).get("redirect_uris", [])

        if len(requested_client_redirect_uris) == 1 and redirect_uri:
            if redirect_uri not in requested_client_redirect_uris:
                # https://www.ietf.org/archive/id/draft-ietf-oauth-v2-1-12.html#section-2.3.2
                # If an authorization request fails validation due to a missing, invalid, or mismatching redirect URI,
                # the authorization server SHOULD inform the resource owner of the error and MUST NOT automatically redirect
                # the user agent to the invalid redirect URI.
                return handle_error(
                    redirect_uri=None,
                    error="invalid_request",
                    description="The provided 'redirect_uri' does not match the registered 'redirect_uri'.",
                    state=state
                )

        if len(requested_client_redirect_uris) > 1 and not redirect_uri:
            # If an authorization request fails validation due to a missing, invalid, or mismatching redirect URI,
            # the authorization server SHOULD inform the resource owner of the error and MUST NOT automatically redirect
            # the user agent to the invalid redirect URI.
            return handle_error(
                redirect_uri=None,
                error="invalid_request",
                description="The provided 'redirect_uri' does not match the registered 'redirect_uri'.",
                state=state
            )

        if redirect_uri not in requested_client_redirect_uris:
            # If an authorization request fails validation due to a missing, invalid, or mismatching redirect URI,
            # the authorization server SHOULD inform the resource owner of the error and MUST NOT automatically redirect
            # the user agent to the invalid redirect URI.
            return handle_error(
                redirect_uri=None,
                error="invalid_request",
                description="The provided 'redirect_uri' does not match the registered 'redirect_uri'.",
                state=state
            )

        if redirect_uri and not ClientService.is_absolute_uri(redirect_uri):
            return handle_error(
                redirect_uri=None,
                error="invalid_request",
                description="The 'redirect_uri' must be an absolute URI.",
                state=state
            )

        if scope and not isinstance(scope, str):  # Ensure it's a string
                return handle_error(
                    redirect_uri=None,
                    error="invalid_request",
                    description="The 'scope' parameter must be a string.",
                    state=state
                )

        # Resource Indicators for OAuth 2.0
        # https://datatracker.ietf.org/doc/html/rfc8707#name-resource-parameter
        if resource:
            try:
                ClientService.validate_resource_uris(resource)
            except ValueError as e:
                return {
                    'code': 400,
                    'status': 'invalid_target',
                    'message': 'The requested resource is invalid, missing, unknown, or malformed.',
                    'errors': {}
                }, http.HTTPStatus.BAD_REQUEST

        authorization_code = AuthorizationCodeService.generate_authorization_code(client_id, current_user.user_id)
        redirect_params = {"code": authorization_code}

        if state:
            additional_params["state"] = state

        redirect_url = f"{redirect_uri}?{urlencode(redirect_params)}"
        return redirect(redirect_url)


@oauth_api.route("/token")
class TokenApi(MethodView):
    """
    The token endpoint is used by the client to obtain an access token using a grant.
    """
    @oauth_api.response(http.HTTPStatus.OK, TokenResponseSchema)
    @oauth_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    def post(self):
        if not current_user.is_authenticated:
            return {
                "code": http.HTTPStatus.UNAUTHORIZED,
                "status": "unauthorized",
                "message": "User is not authenticated",
                "errors": {}
            }, http.HTTPStatus.UNAUTHORIZED

        data = request.form
        grant_type = data.get("grant_type")
        client_id = data.get("client_id")
        client_secret = data.get("client_secret")

        # Validate client
        client = ClientService.get_client(client_id)
        if not client or not client.verify_secret(client_secret):
            return {
                "code": http.HTTPStatus.UNAUTHORIZED,
                "status": "unauthorized",
                "message": "Invalid client credentials",
                "errors": {}
            }, http.HTTPStatus.UNAUTHORIZED

        # Process grant type
        if grant_type == "authorization_code":
            code = data.get("code")
            redirect_uri = data.get("redirect_uri")
            token_response = TokenService.handle_authorization_code_grant(client, code, redirect_uri)
        elif grant_type == "refresh_token":
            refresh_token = data.get("refresh_token")
            token_response = TokenService.handle_refresh_token_grant(client, refresh_token)
        elif grant_type == "client_credentials":
            token_response = TokenService.handle_client_credentials_grant(client)
        else:
            return {
                "code": http.HTTPStatus.BAD_REQUEST,
                "status": "invalid_request",
                "message": "Unsupported grant type",
                "errors": {}
            }, http.HTTPStatus.BAD_REQUEST

        if not token_response:
            return {
                "code": http.HTTPStatus.BAD_REQUEST,
                "status": "invalid_request",
                "message": "Invalid request parameters",
                "errors": {}
            }, http.HTTPStatus.BAD_REQUEST

        return token_response, http.HTTPStatus.OK


@oauth_api.route("/revoke")
class RevocationApi(MethodView):
    @oauth_api.response(http.HTTPStatus.NO_CONTENT)
    @oauth_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    def post(self):
        """
        Endpoint for revoking an access or refresh token.
        """
        token = request.form.get("token")
        token_type_hint = request.form.get("token_type_hint", "access_token")

        if not token:
            return {
                "code": http.HTTPStatus.BAD_REQUEST,
                "status": "invalid_request",
                "message": "Missing token parameter",
                "errors": {}
            }, http.HTTPStatus.BAD_REQUEST

        success = TokenService.revoke_token(token, token_type_hint)
        if not success:
            return {
                "code": http.HTTPStatus.BAD_REQUEST,
                "status": "invalid_request",
                "message": "Invalid or already revoked token",
                "errors": {}
            }, http.HTTPStatus.BAD_REQUEST

        return "", http.HTTPStatus.NO_CONTENT


@oauth_api.route("/introspect")
class IntrospectionApi(MethodView):
    @oauth_api.response(http.HTTPStatus.OK, TokenResponseSchema)
    @oauth_api.alt_response(status_code=http.HTTPStatus.BAD_REQUEST, schema=ErrorSchema, success=False)
    def post(self):
        """
        Endpoint for token introspection.
        """
        token = request.form.get("token")
        token_type_hint = request.form.get("token_type_hint", "access_token")

        if not token:
            return {
                "code": http.HTTPStatus.BAD_REQUEST,
                "status": "invalid_request",
                "message": "Missing token parameter",
                "errors": {}
            }, http.HTTPStatus.BAD_REQUEST

        token_info = TokenService.introspect_token(token, token_type_hint)
        if not token_info:
            return {
                "active": False
            }, http.HTTPStatus.OK

        return token_info, http.HTTPStatus.OK