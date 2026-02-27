"""Tests for DisruptionsAPI — URL construction, params, headers, and model parsing."""

import pytest
from pytest_httpx import HTTPXMock

from py_ns import NSClient
from py_ns.models.disruptions import Calamity, Disruption, DisruptionType

from .conftest import (
    FIXTURE_DISRUPTIONS,
    FIXTURE_DISRUPTIONS_MIXED,
    MINIMAL_CALAMITY,
    MINIMAL_DISRUPTION,
)

DISRUPTIONS_BASE = "https://gateway.apiportal.ns.nl/disruptions"


# ---------------------------------------------------------------------------
# list()
# ---------------------------------------------------------------------------


def test_list_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DISRUPTIONS)
    client.disruptions.list()
    assert httpx_mock.get_request().url.path == "/disruptions/v3"


def test_list_sends_is_active_param(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DISRUPTIONS)
    client.disruptions.list(is_active=True)
    assert "isActive=true" in str(httpx_mock.get_request().url)


def test_list_sends_type_param(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DISRUPTIONS)
    client.disruptions.list(disruption_type=DisruptionType.disruption)
    assert "type=DISRUPTION" in str(httpx_mock.get_request().url)


def test_list_sends_accept_language_header(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DISRUPTIONS)
    client.disruptions.list(language="nl")
    assert httpx_mock.get_request().headers["Accept-Language"] == "nl"


def test_list_without_language_omits_header(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DISRUPTIONS)
    client.disruptions.list()
    assert "accept-language" not in httpx_mock.get_request().headers


def test_list_returns_disruption_model(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[MINIMAL_DISRUPTION])
    result = client.disruptions.list()
    assert len(result) == 1
    assert isinstance(result[0], Disruption)
    assert result[0].id == "dis-123"
    assert result[0].is_active is True
    assert result[0].title == "Test disruption"


def test_list_returns_calamity_model_for_calamity_type(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=[MINIMAL_CALAMITY])
    result = client.disruptions.list()
    assert len(result) == 1
    assert isinstance(result[0], Calamity)
    assert result[0].id == "cal-123"
    assert result[0].priority.value == "PRIO_1"


def test_list_dispatches_mixed_types(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DISRUPTIONS_MIXED)
    result = client.disruptions.list()
    assert len(result) == 2
    assert isinstance(result[0], Disruption)
    assert isinstance(result[1], Calamity)


def test_list_returns_empty_list(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[])
    result = client.disruptions.list()
    assert result == []


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


def test_get_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=MINIMAL_DISRUPTION)
    client.disruptions.get(DisruptionType.disruption, "dis-123")
    assert httpx_mock.get_request().url.path == "/disruptions/v3/DISRUPTION/dis-123"


def test_get_sends_language_header(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=MINIMAL_DISRUPTION)
    client.disruptions.get(DisruptionType.disruption, "dis-123", language="en")
    assert httpx_mock.get_request().headers["Accept-Language"] == "en"


def test_get_returns_disruption_model(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=MINIMAL_DISRUPTION)
    result = client.disruptions.get(DisruptionType.disruption, "dis-123")
    assert isinstance(result, Disruption)
    assert result.id == "dis-123"


def test_get_returns_calamity_model(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=MINIMAL_CALAMITY)
    result = client.disruptions.get(DisruptionType.calamity, "cal-123")
    assert isinstance(result, Calamity)
    assert result.id == "cal-123"


# ---------------------------------------------------------------------------
# list_for_station()
# ---------------------------------------------------------------------------


def test_list_for_station_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DISRUPTIONS)
    client.disruptions.list_for_station("ASD")
    assert httpx_mock.get_request().url.path == "/disruptions/v3/station/ASD"


def test_list_for_station_sends_language_header(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DISRUPTIONS)
    client.disruptions.list_for_station("UT", language="nl")
    assert httpx_mock.get_request().headers["Accept-Language"] == "nl"


def test_list_for_station_returns_list(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[MINIMAL_DISRUPTION])
    result = client.disruptions.list_for_station("ASD")
    assert len(result) == 1
    assert isinstance(result[0], Disruption)


# ---------------------------------------------------------------------------
# list_personal()
# ---------------------------------------------------------------------------


def test_list_personal_sends_push_id_header(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[])
    client.disruptions.list_personal("push-id-xyz")
    assert httpx_mock.get_request().headers["x-ns-push-id"] == "push-id-xyz"


def test_list_personal_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[])
    client.disruptions.list_personal("push-id-xyz")
    assert httpx_mock.get_request().url.path == "/disruptions/v1/personal-disruptions"


# ---------------------------------------------------------------------------
# sync_saved_trips()
# ---------------------------------------------------------------------------


def test_sync_saved_trips_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    from py_ns.models.disruptions import RepeatOn, SyncSavedTripsRequest

    httpx_mock.add_response(status_code=204)
    repeat_on = RepeatOn(
        monday=True, tuesday=False, wednesday=False, thursday=False,
        friday=False, saturday=False, sunday=False,
    )
    saved_trip = SyncSavedTripsRequest(
        id=1.0,
        ctxRecon="arnu|test",
        currentCtxRecon="arnu|test",
        repeatOn=repeat_on,
    )
    client.disruptions.sync_saved_trips("sync-api-key", saved_trip)
    request = httpx_mock.get_request()
    assert request.url.path == "/disruptions/v1/personal-disruptions/sync/saved-trips"
    assert request.headers["x-api-key"] == "sync-api-key"
    assert request.method == "POST"
