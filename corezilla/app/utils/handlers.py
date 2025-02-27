import http
from urllib.parse import urlencode

from flask import jsonify, redirect


def handle_error(redirect_uri, error, description=None, state=None):
    """
    Handles OAuth 2.0 errors according to RFC 6749.

    If a valid `redirect_uri` is provided, redirects the user with the error
    parameters. Otherwise, returns a JSON error response.

    Args:
        redirect_uri (str): The redirect URI to send the error response to.
        error (str): The OAuth error code (e.g., "invalid_request", "unauthorized").
        description (str, optional): A human-readable error description.
        state (str, optional): The original state parameter to maintain CSRF protection.

    Returns:
        A Flask `redirect` response if `redirect_uri` is valid, else a JSON error response.
    """
    error_response = {
        "error": error,
        "error_description": description or "An error occurred during authorization."
    }

    if state:
        error_response["state"] = state  # Preserve state for CSRF protection

    # If `redirect_uri` is provided, validate and redirect
    if redirect_uri:
        from urllib.parse import urlparse

        parsed_uri = urlparse(redirect_uri)
        if not parsed_uri.scheme or not parsed_uri.netloc:
            # Invalid `redirect_uri`, fallback to JSON response
            return jsonify(error_response), http.HTTPStatus.BAD_REQUEST

        # Append error parameters to redirect URI
        redirect_url = f"{redirect_uri}?{urlencode(error_response)}"
        return redirect(redirect_url)

    # If no `redirect_uri`, return JSON error response
    return jsonify(error_response), http.HTTPStatus.BAD_REQUEST