from urllib.parse import urlparse

from corezilla.app.exceptions.user import InvalidURI


def validate_redirect_uri(uri: str):
    """
    The redirection endpoint URI MUST be an absolute URI as defined by
    [RFC3986] Section 4.3.

    absolute-URI  = scheme ":" hier-part [ "?" query ]

    The endpoint URI MAY include an "application/x-www-form-urlencoded"
    formatted (per Appendix B) query component ([RFC3986] Section 3.4),
    which MUST be retained when adding additional query parameters.

    The endpoint URI MUST NOT include a fragment component.
    """

    url = urlparse(uri, allow_fragments=False)

    if not url.scheme:
        raise InvalidURI("Invalid URI as defined by RFC 3986#Section 4.3. Missing scheme.")
    elif url.scheme.lower() == "http":
        raise InvalidURI("Redirection endpoints provided to this server MUST use TLS.")
    else:
        return url
