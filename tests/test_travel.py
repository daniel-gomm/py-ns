"""Tests for TravelAPI — URL construction, params, headers, model parsing, and deprecation warnings."""

import warnings

import pytest
from pytest_httpx import HTTPXMock

from py_ns import NSClient
from py_ns.models.travel import Arrival, Departure, Journey, TravelAdvice, Trip

from .conftest import (
    FIXTURE_ARRIVALS,
    FIXTURE_CALAMITIES,
    FIXTURE_DEPARTURES,
    FIXTURE_JOURNEY_RESPONSE,
    FIXTURE_PRICE_V2,
    FIXTURE_PRICE_V3,
    FIXTURE_STATIONS,
    FIXTURE_TRAVEL_ADVICE,
    FIXTURE_TRIP,
    MINIMAL_ARRIVAL,
    MINIMAL_DEPARTURE,
)

TRAVEL_BASE = "https://gateway.apiportal.ns.nl/reisinformatie-api"


# ---------------------------------------------------------------------------
# get_departures()
# ---------------------------------------------------------------------------


def test_get_departures_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DEPARTURES)
    client.travel.get_departures("ASD")
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v2/departures"


def test_get_departures_sends_station_param(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DEPARTURES)
    client.travel.get_departures("ASD")
    assert "station=ASD" in str(httpx_mock.get_request().url)


def test_get_departures_sends_uic_code(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DEPARTURES)
    client.travel.get_departures("", uic_code="8400058")
    assert "uicCode=8400058" in str(httpx_mock.get_request().url)


def test_get_departures_sends_max_journeys(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DEPARTURES)
    client.travel.get_departures("ASD", max_journeys=10)
    assert "maxJourneys=10" in str(httpx_mock.get_request().url)


def test_get_departures_sends_language(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DEPARTURES)
    client.travel.get_departures("ASD", language="en")
    assert "lang=en" in str(httpx_mock.get_request().url)


def test_get_departures_returns_departure_list(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_DEPARTURES)
    result = client.travel.get_departures("ASD")
    assert len(result) == 1
    assert isinstance(result[0], Departure)
    assert result[0].name == "IC 1234"
    assert result[0].train_category == "IC"
    assert result[0].cancelled is False
    assert result[0].departure_status.value == "ON_STATION"


def test_get_departures_product_optional_fields_are_none(
    client: NSClient, httpx_mock: HTTPXMock
):
    """Verify that patched optional fields on Product default to None when absent."""
    httpx_mock.add_response(json=FIXTURE_DEPARTURES)
    result = client.travel.get_departures("ASD")
    product = result[0].product
    assert product.notes is None
    assert product.name_nes_properties is None
    assert product.product_type is None


def test_get_departures_returns_empty_list(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={"payload": {"source": "DDR", "departures": []}})
    result = client.travel.get_departures("ASD")
    assert result == []


# ---------------------------------------------------------------------------
# get_arrivals()
# ---------------------------------------------------------------------------


def test_get_arrivals_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_ARRIVALS)
    client.travel.get_arrivals("UT")
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v2/arrivals"


def test_get_arrivals_sends_station_param(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_ARRIVALS)
    client.travel.get_arrivals("UT")
    assert "station=UT" in str(httpx_mock.get_request().url)


def test_get_arrivals_returns_arrival_list(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_ARRIVALS)
    result = client.travel.get_arrivals("UT")
    assert len(result) == 1
    assert isinstance(result[0], Arrival)
    assert result[0].name == "IC 1234"
    assert result[0].arrival_status.value == "ON_STATION"


# ---------------------------------------------------------------------------
# get_journey()
# ---------------------------------------------------------------------------


def test_get_journey_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_JOURNEY_RESPONSE)
    client.travel.get_journey(train=1234)
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v2/journey"


def test_get_journey_sends_train_param(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_JOURNEY_RESPONSE)
    client.travel.get_journey(train=6952)
    assert "train=6952" in str(httpx_mock.get_request().url)


def test_get_journey_sends_journey_id(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_JOURNEY_RESPONSE)
    client.travel.get_journey(journey_id="1|231691|0|784|15122020")
    assert "1%7C231691" in str(httpx_mock.get_request().url)


def test_get_journey_sends_omit_crowd_forecast(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_JOURNEY_RESPONSE)
    client.travel.get_journey(train=1234, omit_crowd_forecast=True)
    assert "omitCrowdForecast=true" in str(httpx_mock.get_request().url)


def test_get_journey_returns_journey_model(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_JOURNEY_RESPONSE)
    result = client.travel.get_journey(train=1234)
    assert isinstance(result, Journey)
    assert len(result.stops) == 1
    assert result.source == "DDR"


# ---------------------------------------------------------------------------
# plan_trip()
# ---------------------------------------------------------------------------


def test_plan_trip_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_TRAVEL_ADVICE)
    client.travel.plan_trip("ASD", "UT")
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v3/trips"


def test_plan_trip_sends_from_and_to_station(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_TRAVEL_ADVICE)
    client.travel.plan_trip("ASD", "UT")
    url = str(httpx_mock.get_request().url)
    assert "fromStation=ASD" in url
    assert "toStation=UT" in url


def test_plan_trip_sends_via_station(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_TRAVEL_ADVICE)
    client.travel.plan_trip("ASD", "EHV", via_station="UT")
    assert "viaStation=UT" in str(httpx_mock.get_request().url)


def test_plan_trip_sends_search_for_arrival(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_TRAVEL_ADVICE)
    client.travel.plan_trip("ASD", "UT", search_for_arrival=True)
    assert "searchForArrival=true" in str(httpx_mock.get_request().url)


def test_plan_trip_does_not_send_false_search_for_arrival(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=FIXTURE_TRAVEL_ADVICE)
    client.travel.plan_trip("ASD", "UT")
    assert "searchForArrival" not in str(httpx_mock.get_request().url)


def test_plan_trip_sends_add_change_time(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_TRAVEL_ADVICE)
    client.travel.plan_trip("ASD", "UT", add_change_time=5)
    assert "addChangeTime=5" in str(httpx_mock.get_request().url)


def test_plan_trip_returns_travel_advice(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_TRAVEL_ADVICE)
    result = client.travel.plan_trip("ASD", "UT")
    assert isinstance(result, TravelAdvice)
    assert len(result.trips) == 1
    trip = result.trips[0]
    assert trip.ctx_recon == "arnu|test|ctx|recon"
    assert trip.legs[0].origin.name == "Amsterdam Centraal"
    assert trip.legs[0].destination.name == "Utrecht Centraal"


def test_plan_trip_sends_authorization_header(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_TRAVEL_ADVICE)
    client.travel.plan_trip("ASD", "UT", authorization="Bearer token123")
    assert httpx_mock.get_request().headers["Authorization"] == "Bearer token123"


@pytest.mark.parametrize("param,value,kwarg", [
    ("departure", True, {"departure": True}),
    ("shorter_change", True, {"shorter_change": True}),
    ("minimal_change_time", 3, {"minimal_change_time": 3}),
    ("origin_accessible", True, {"origin_accessible": True}),
    ("travel_assistance_transfer_time", 5, {"travel_assistance_transfer_time": 5}),
])
def test_plan_trip_deprecated_param_emits_warning(
    param: str, value, kwarg: dict, client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=FIXTURE_TRAVEL_ADVICE)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        client.travel.plan_trip("ASD", "UT", **kwarg)
    assert len(caught) == 1
    assert caught[0].category is DeprecationWarning


# ---------------------------------------------------------------------------
# get_trip()
# ---------------------------------------------------------------------------


def test_get_trip_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_TRIP)
    client.travel.get_trip("arnu|test|ctx")
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v3/trips/trip"


def test_get_trip_sends_ctx_recon(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_TRIP)
    client.travel.get_trip("arnu|test|ctx")
    assert "ctxRecon=arnu" in str(httpx_mock.get_request().url)


def test_get_trip_returns_trip_model(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_TRIP)
    result = client.travel.get_trip("arnu|test|ctx|recon")
    assert isinstance(result, Trip)
    assert result.uid == "trip-uid-123"


def test_get_trip_deprecated_source_ctx_recon_warns(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=FIXTURE_TRIP)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        client.travel.get_trip("arnu|test", source_ctx_recon=True)
    assert len(caught) == 1
    assert caught[0].category is DeprecationWarning


# ---------------------------------------------------------------------------
# get_price() v3
# ---------------------------------------------------------------------------


def test_get_price_calls_v3_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_PRICE_V3)
    client.travel.get_price(from_station="ASD", to_station="UT")
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v3/price"


def test_get_price_sends_station_params(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_PRICE_V3)
    client.travel.get_price(from_station="ASD", to_station="UT")
    url = str(httpx_mock.get_request().url)
    assert "fromStation=ASD" in url
    assert "toStation=UT" in url


def test_get_price_sends_travel_class(client: NSClient, httpx_mock: HTTPXMock):
    from py_ns.models.travel import TravelClass
    httpx_mock.add_response(json=FIXTURE_PRICE_V3)
    client.travel.get_price(travel_class=TravelClass.first_class)
    assert "travelClass=FIRST_CLASS" in str(httpx_mock.get_request().url)


# ---------------------------------------------------------------------------
# get_price_v2()
# ---------------------------------------------------------------------------


def test_get_price_v2_calls_v2_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_PRICE_V2)
    client.travel.get_price_v2(from_station="ASD", to_station="UT")
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v2/price"


def test_get_price_v2_sends_travel_class_as_string(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=FIXTURE_PRICE_V2)
    client.travel.get_price_v2(travel_class="1")
    assert "travelClass=1" in str(httpx_mock.get_request().url)


# ---------------------------------------------------------------------------
# Deprecated station endpoints
# ---------------------------------------------------------------------------


def test_get_stations_emits_deprecation_warning(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        client.travel.get_stations("amsterdam")
    assert len(caught) == 1
    assert caught[0].category is DeprecationWarning
    assert "nsapp-stations" in str(caught[0].message).lower()


def test_get_stations_sends_query_param(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS)
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        client.travel.get_stations("amsterdam")
    assert "q=amsterdam" in str(httpx_mock.get_request().url)


def test_get_nearest_stations_emits_deprecation_warning(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=FIXTURE_STATIONS)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        client.travel.get_nearest_stations(52.379, 4.900)
    assert len(caught) == 1
    assert caught[0].category is DeprecationWarning
    assert "nsapp-stations" in str(caught[0].message).lower()


def test_get_nearest_stations_sends_lat_lng(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_STATIONS)
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        client.travel.get_nearest_stations(52.379, 4.900, limit=3)
    url = str(httpx_mock.get_request().url)
    assert "lat=52.379" in url
    assert "lng=4.9" in url
    assert "limit=3" in url


# ---------------------------------------------------------------------------
# Deprecated disruption endpoints
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method,kwargs,expected_substring", [
    ("get_calamities", {}, "client.disruptions.list"),
    ("list_disruptions", {}, "client.disruptions.list"),
    ("list_station_disruptions", {"station_code": "ASD"}, "client.disruptions.list_for_station"),
    ("get_disruption", {"disruption_type": "DISRUPTION", "disruption_id": "123"}, "client.disruptions.get"),
])
def test_deprecated_disruption_method_warns(
    method: str,
    kwargs: dict,
    expected_substring: str,
    client: NSClient,
    httpx_mock: HTTPXMock,
):
    if method == "get_calamities":
        httpx_mock.add_response(json=FIXTURE_CALAMITIES)
    else:
        httpx_mock.add_response(json=[] if "list" in method else {})

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        getattr(client.travel, method)(**kwargs)

    assert len(caught) == 1
    assert caught[0].category is DeprecationWarning
    assert expected_substring in str(caught[0].message)


def test_get_calamities_calls_v1_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=FIXTURE_CALAMITIES)
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        client.travel.get_calamities()
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v1/calamities"


def test_list_disruptions_calls_v3_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[])
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        client.travel.list_disruptions()
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v3/disruptions"


def test_list_station_disruptions_calls_correct_url(
    client: NSClient, httpx_mock: HTTPXMock
):
    httpx_mock.add_response(json=[])
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        client.travel.list_station_disruptions("ASD")
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v3/disruptions/station/ASD"


def test_get_disruption_calls_correct_url(client: NSClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={})
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        client.travel.get_disruption("DISRUPTION", "dis-123")
    assert httpx_mock.get_request().url.path == "/reisinformatie-api/api/v3/disruptions/DISRUPTION/dis-123"
