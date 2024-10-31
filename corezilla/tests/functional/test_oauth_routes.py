import pytest


def test_authorize(test_client):
    assert test_client.get('/authorize').status_code == 200


@pytest.mark.parametrize(('client_id', 'redirect_uri', 'message'), (
        ("", "https://example.com", "mandatory_parameter_missing"),
        ("", "https://example.com", "mandatory_parameter_missing"),
        # ("A123456", "https://example.com", ""),
        # ("A123456", "https://example.com", ""),
        ("A123456", "", "mandatory_parameter_missing"),
        ("A123456", "", "mandatory_parameter_missing"),
))
def test_request_example(test_client, client_id, redirect_uri, message):
    response = test_client.get(
        "/api/authorize",
        query_string={"client_id": client_id, "redirect_uri": redirect_uri}
    )

    error_msg = response.json
    error_msg = error_msg.get("description")

    assert error_msg == message
