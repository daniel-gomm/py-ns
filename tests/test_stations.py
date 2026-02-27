"""Tests for StationsAPI — URL construction, params, and model parsing."""

import pytest
from pytest_httpx import HTTPXMock

from py_ns import NSClient
from py_ns.models.stations import StationV2, StationV3

from .conftest import (
    FIXTURE_STATION_V3,
    FIXTURE_STATIONS_V2,
    FIXTURE_STATIONS_V3,
    MINIMAL_STATION_V2,
    MINIMAL_STATION_V3,
)

STATIONS_BASE = "https://gateway.apiportal.ns.nl/nsapp-stations"


# ---------------------------------------------------------------------------
# list_v2()
# ---------------------------------------------------------------------------


def test_list_v2_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V2)
    client.stations.list_v2()
    assert httpx_mock.get_request().url.path == "/nsapp-stations/v2"


def test_list_v2_sends_query_param(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V2)
    client.stations.list_v2("amsterdam")
    assert "q=amsterdam" in str(httpx_mock.get_request().url)


def test_list_v2_sends_country_codes(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V2)
    client.stations.list_v2(country_codes="NL,BE")
    assert "countryCodes=NL%2CBE" in str(httpx_mock.get_request().url)


def test_list_v2_sends_limit(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V2)
    client.stations.list_v2(limit=5)
    assert "limit=5" in str(httpx_mock.get_request().url)


def test_list_v2_sends_include_non_plannable(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V2)
    client.stations.list_v2(include_non_plannable=True)
    assert "includeNonPlannableStations=true" in str(httpx_mock.get_request().url)


def test_list_v2_omits_optional_params_when_not_provided(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V2)
    client.stations.list_v2()
    url = str(httpx_mock.get_request().url)
    assert "q=" not in url
    assert "limit=" not in url
    assert "countryCodes=" not in url


def test_list_v2_returns_station_v2_list(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={"payload": [MINIMAL_STATION_V2]})
    result = client.stations.list_v2()
    assert len(result) == 1
    assert isinstance(result[0], StationV2)
    assert result[0].uic_code == "8400058"
    assert result[0].station_type.value == "MEGA_STATION"
    assert result[0].heeft_faciliteiten is True
    assert result[0].code == "ASD"


def test_list_v2_returns_empty_list(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={"payload": []})
    result = client.stations.list_v2()
    assert result == []


# ---------------------------------------------------------------------------
# list_nearest_v2()
# ---------------------------------------------------------------------------


def test_list_nearest_v2_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V2)
    client.stations.list_nearest_v2(52.379, 4.900)
    assert httpx_mock.get_request().url.path == "/nsapp-stations/v2/nearest"


def test_list_nearest_v2_sends_lat_lng(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V2)
    client.stations.list_nearest_v2(52.379, 4.900)
    url = str(httpx_mock.get_request().url)
    assert "lat=52.379" in url
    assert "lng=4.9" in url


def test_list_nearest_v2_sends_limit(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V2)
    client.stations.list_nearest_v2(52.379, 4.900, limit=3)
    assert "limit=3" in str(httpx_mock.get_request().url)


def test_list_nearest_v2_returns_station_v2_list(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V2)
    result = client.stations.list_nearest_v2(52.379, 4.900)
    assert len(result) == 1
    assert isinstance(result[0], StationV2)


# ---------------------------------------------------------------------------
# list_v3()
# ---------------------------------------------------------------------------


def test_list_v3_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V3)
    client.stations.list_v3()
    assert httpx_mock.get_request().url.path == "/nsapp-stations/v3"


def test_list_v3_sends_query_param(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V3)
    client.stations.list_v3("utrecht")
    assert "q=utrecht" in str(httpx_mock.get_request().url)


def test_list_v3_sends_country_codes(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V3)
    client.stations.list_v3(country_codes="NL")
    assert "countryCodes=NL" in str(httpx_mock.get_request().url)


def test_list_v3_sends_limit(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V3)
    client.stations.list_v3(limit=10)
    assert "limit=10" in str(httpx_mock.get_request().url)


def test_list_v3_returns_station_v3_list(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={"payload": [MINIMAL_STATION_V3]})
    result = client.stations.list_v3()
    assert len(result) == 1
    assert isinstance(result[0], StationV3)
    assert result[0].id.uic_code == "8400058"
    assert result[0].id.code == "ASD"
    assert result[0].names.long == "Amsterdam Centraal"
    assert result[0].names.synonyms == ["AMS"]
    assert result[0].station_type.value == "MEGA_STATION"
    assert result[0].has_known_facilities is True
    assert result[0].country == "NL"
    assert result[0].location.lat == 52.3791


def test_list_v3_returns_empty_list(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={"payload": []})
    result = client.stations.list_v3()
    assert result == []


# ---------------------------------------------------------------------------
# list_nearest_v3()
# ---------------------------------------------------------------------------


def test_list_nearest_v3_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V3)
    client.stations.list_nearest_v3(52.379, 4.900)
    assert httpx_mock.get_request().url.path == "/nsapp-stations/v3/nearest"


def test_list_nearest_v3_sends_lat_lng(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V3)
    client.stations.list_nearest_v3(52.089, 5.110)
    url = str(httpx_mock.get_request().url)
    assert "lat=52.089" in url
    assert "lng=5.11" in url


def test_list_nearest_v3_sends_limit(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V3)
    client.stations.list_nearest_v3(52.379, 4.900, limit=2)
    assert "limit=2" in str(httpx_mock.get_request().url)


def test_list_nearest_v3_sends_include_non_plannable(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V3)
    client.stations.list_nearest_v3(52.379, 4.900, include_non_plannable=False)
    assert "includeNonPlannableStations=false" in str(httpx_mock.get_request().url)


def test_list_nearest_v3_returns_station_v3_list(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=FIXTURE_STATIONS_V3)
    result = client.stations.list_nearest_v3(52.379, 4.900)
    assert len(result) == 1
    assert isinstance(result[0], StationV3)


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


def test_get_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATION_V3)
    client.stations.get("8400058")
    assert httpx_mock.get_request().url.path == "/nsapp-stations/v1/station"


def test_get_sends_uic_code(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATION_V3)
    client.stations.get("8400058")
    assert "uicCode=8400058" in str(httpx_mock.get_request().url)


def test_get_sends_uic_cd_code_when_provided(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATION_V3)
    client.stations.get("8400058", uic_cd_code="8400058000")
    url = str(httpx_mock.get_request().url)
    assert "uicCode=8400058" in url
    assert "uicCdCode=8400058000" in url


def test_get_omits_uic_cd_code_when_not_provided(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=FIXTURE_STATION_V3)
    client.stations.get("8400058")
    assert "uicCdCode" not in str(httpx_mock.get_request().url)


def test_get_returns_station_v3(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATION_V3)
    result = client.stations.get("8400058")
    assert isinstance(result, StationV3)
    assert result.id.uic_code == "8400058"
    assert result.names.long == "Amsterdam Centraal"
    assert result.has_travel_assistance is True
    assert result.is_border_stop is False
    assert result.tracks == ["1", "2"]
