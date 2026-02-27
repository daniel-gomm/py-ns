"""Tests for the HTTP transport layer: auth, error mapping, response parsing."""

import pytest
from pytest_httpx import HTTPXMock

from py_ns._base.transport import HttpTransport
from py_ns.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

API_KEY = "test-key-abc"
TEST_URL = "https://example.com/api/test"


@pytest.fixture
def transport():
    t = HttpTransport(api_key=API_KEY, timeout=5.0)
    yield t
    t.close()


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def test_auth_header_is_sent(transport: HttpTransport, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={"ok": True})
    transport.get(TEST_URL)
    request = httpx_mock.get_request()
    assert request.headers["Ocp-Apim-Subscription-Key"] == API_KEY


def test_auth_header_present_on_post(transport: HttpTransport, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={"ok": True})
    transport.post(TEST_URL, json={"data": 1})
    request = httpx_mock.get_request()
    assert request.headers["Ocp-Apim-Subscription-Key"] == API_KEY


# ---------------------------------------------------------------------------
# Successful responses
# ---------------------------------------------------------------------------


def test_get_returns_parsed_json(transport: HttpTransport, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={"key": "value"})
    result = transport.get(TEST_URL)
    assert result == {"key": "value"}


def test_get_with_params_sends_query_string(transport: HttpTransport, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={})
    transport.get(TEST_URL, params={"station": "ASD", "maxJourneys": 10})
    request = httpx_mock.get_request()
    assert "station=ASD" in str(request.url)
    assert "maxJourneys=10" in str(request.url)


def test_get_with_extra_headers_merges_them(transport: HttpTransport, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={})
    transport.get(TEST_URL, headers={"Accept-Language": "nl"})
    request = httpx_mock.get_request()
    assert request.headers["Accept-Language"] == "nl"
    assert request.headers["Ocp-Apim-Subscription-Key"] == API_KEY


def test_post_sends_json_body(transport: HttpTransport, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={"created": True})
    transport.post(TEST_URL, json={"id": 42})
    request = httpx_mock.get_request()
    assert b'"id": 42' in request.content or b'"id":42' in request.content


# ---------------------------------------------------------------------------
# Error mapping
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status_code", [401, 403])
def test_auth_errors_raise_authentication_error(
    status_code: int, transport: HttpTransport, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(status_code=status_code, json={"message": "Unauthorized"})
    with pytest.raises(AuthenticationError) as exc_info:
        transport.get(TEST_URL)
    assert exc_info.value.status_code == status_code


def test_404_raises_not_found_error(transport: HttpTransport, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=404, json={"message": "Not found"})
    with pytest.raises(NotFoundError) as exc_info:
        transport.get(TEST_URL)
    assert exc_info.value.status_code == 404


def test_429_raises_rate_limit_error(transport: HttpTransport, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=429, json={"message": "Too many requests"})
    with pytest.raises(RateLimitError) as exc_info:
        transport.get(TEST_URL)
    assert exc_info.value.status_code == 429


@pytest.mark.parametrize("status_code", [500, 502, 503])
def test_5xx_raises_server_error(
    status_code: int, transport: HttpTransport, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(status_code=status_code, text="Internal Server Error")
    with pytest.raises(ServerError) as exc_info:
        transport.get(TEST_URL)
    assert exc_info.value.status_code == status_code


def test_400_raises_api_error(transport: HttpTransport, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400, json={"message": "Bad request"})
    with pytest.raises(APIError) as exc_info:
        transport.get(TEST_URL)
    assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# Error message extraction
# ---------------------------------------------------------------------------


def test_error_message_extracted_from_json_body(transport: HttpTransport, httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400, json={"message": "Station not found"})
    with pytest.raises(APIError, match="Station not found"):
        transport.get(TEST_URL)


def test_error_message_falls_back_to_response_text(
    transport: HttpTransport, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(status_code=500, text="Gateway timeout")
    with pytest.raises(ServerError, match="Gateway timeout"):
        transport.get(TEST_URL)


def test_error_message_falls_back_when_json_has_no_message(
    transport: HttpTransport, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(status_code=400, json={"error": "bad"})
    # Should not raise KeyError — falls back to the raw JSON text
    with pytest.raises(APIError):
        transport.get(TEST_URL)


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


def test_context_manager_closes_transport(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={})
    with HttpTransport(api_key=API_KEY) as t:
        t.get(TEST_URL)
    # After exiting, the client should be closed; subsequent calls raise
    with pytest.raises(Exception):
        t.get(TEST_URL)
