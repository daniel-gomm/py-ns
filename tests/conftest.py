"""
Shared fixtures and minimal response payloads for the py-ns test suite.

Each FIXTURE_* constant is a minimal but structurally valid JSON payload that
matches what the real NS API returns. They are used to verify both that the
correct HTTP request is made AND that the response parses into the expected
Pydantic models without errors.

When the NS API spec changes, update the corresponding fixture here so that
the test suite reflects the new contract.
"""

import pytest

from py_ns import NSClient

# ---------------------------------------------------------------------------
# Minimal model building blocks
# ---------------------------------------------------------------------------

MINIMAL_PRODUCT = {
    "number": "1234",
    "categoryCode": "IC",
    "shortCategoryName": "IC",
    "longCategoryName": "Intercity",
    "operatorCode": "NS",
    "operatorName": "NS",
    "type": "TRAIN",
}

MINIMAL_DEPARTURE = {
    "name": "IC 1234",
    "product": MINIMAL_PRODUCT,
    "trainCategory": "IC",
    "cancelled": False,
    "routeStations": [],
    "messages": [],
    "departureStatus": "ON_STATION",
}

MINIMAL_ARRIVAL = {
    "name": "IC 1234",
    "product": MINIMAL_PRODUCT,
    "trainCategory": "IC",
    "cancelled": False,
    "messages": [],
    "arrivalStatus": "ON_STATION",
}

MINIMAL_DISRUPTION = {
    "id": "dis-123",
    "type": "DISRUPTION",
    "isActive": True,
    "title": "Test disruption",
    "local": False,
    "titleSections": [],
    "publicationSections": [],
    "timespans": [],
    "alternativeTransportTimespans": [],
}

MINIMAL_CALAMITY = {
    "id": "cal-123",
    "type": "CALAMITY",
    "isActive": True,
    "title": "Test calamity",
    "topic": "test-topic",
    "priority": "PRIO_1",
    "bodyItems": [],
    "buttons": {"position": [], "items": []},
}

MINIMAL_STOP = {
    "notes": [],
    "cancelled": False,
    "borderStop": False,
    "passing": False,
}

MINIMAL_LEG = {
    "partCancelled": False,
    "cancelled": False,
    "isAfterCancelledLeg": False,
    "isOnOrAfterCancelledLeg": False,
    "changePossible": True,
    "alternativeTransport": False,
    "origin": {"name": "Amsterdam Centraal"},
    "destination": {"name": "Utrecht Centraal"},
    "stops": [MINIMAL_STOP],
    "reachable": True,
    "preSteps": [],
    "postSteps": [],
}

MINIMAL_TRIP = {
    "uid": "trip-uid-123",
    "ctxRecon": "arnu|test|ctx|recon",
    "transfers": 0,
    "status": "NORMAL",
    "legs": [MINIMAL_LEG],
    "optimal": True,
    "type": "NS",
    "realtime": True,
}

MINIMAL_JOURNEY_STOP = {
    "id": "stop-1",
    "stop": {"name": "Amsterdam Centraal"},
    "previousStopId": [],
    "nextStopId": ["stop-2"],
    "arrivals": [],
    "departures": [],
}

MINIMAL_STATION = {
    "code": "ASD",
    "namen": {"lang": "Amsterdam Centraal", "middel": "Amsterdam C.", "kort": "Asd"},
    "land": "NL",
    "lat": 52.3791,
    "lng": 4.9003,
}

MINIMAL_STATION_V2 = {
    "UICCode": "8400058",
    "stationType": "MEGA_STATION",
    "sporen": [{"spoorNummer": "1"}],
    "synoniemen": ["AMS"],
    "heeftFaciliteiten": True,
    "heeftVertrektijden": True,
    "heeftReisassistentie": True,
    "namen": {"lang": "Amsterdam Centraal", "middel": "Amsterdam C.", "kort": "Asd"},
    "code": "ASD",
    "land": "NL",
    "lat": 52.3791,
    "lng": 4.9003,
}

MINIMAL_STATION_V3 = {
    "id": {"uicCode": "8400058", "code": "ASD"},
    "stationType": "MEGA_STATION",
    "names": {
        "long": "Amsterdam Centraal",
        "medium": "Amsterdam C.",
        "short": "Asd",
        "synonyms": ["AMS"],
    },
    "location": {"lat": 52.3791, "lng": 4.9003},
    "tracks": ["1", "2"],
    "hasKnownFacilities": True,
    "availableForAccessibleTravel": True,
    "hasTravelAssistance": True,
    "areTracksIndependentlyAccessible": False,
    "isBorderStop": False,
    "country": "NL",
}

# ---------------------------------------------------------------------------
# Full API response payloads
# ---------------------------------------------------------------------------

FIXTURE_DEPARTURES = {
    "payload": {
        "source": "DDR",
        "departures": [MINIMAL_DEPARTURE],
    }
}

FIXTURE_ARRIVALS = {
    "payload": {
        "source": "DDR",
        "arrivals": [MINIMAL_ARRIVAL],
    }
}

FIXTURE_DISRUPTIONS = [MINIMAL_DISRUPTION]

FIXTURE_DISRUPTIONS_MIXED = [MINIMAL_DISRUPTION, MINIMAL_CALAMITY]

FIXTURE_TRAVEL_ADVICE = {
    "source": "HARP",
    "trips": [MINIMAL_TRIP],
}

FIXTURE_TRIP = MINIMAL_TRIP

FIXTURE_JOURNEY = {
    "notes": [],
    "productNumbers": ["1234"],
    "stops": [MINIMAL_JOURNEY_STOP],
    "allowCrowdReporting": False,
    "source": "DDR",
}

FIXTURE_JOURNEY_RESPONSE = {"payload": FIXTURE_JOURNEY}

FIXTURE_STATIONS = {
    "payload": [MINIMAL_STATION],
}

FIXTURE_STATIONS_V2 = {"payload": [MINIMAL_STATION_V2]}

FIXTURE_STATIONS_V3 = {"payload": [MINIMAL_STATION_V3]}

FIXTURE_STATION_V3 = {"payload": MINIMAL_STATION_V3}

FIXTURE_CALAMITIES = {
    "calamiteit": None,
    "meldingen": [],
}

FIXTURE_PRICE_V3 = {
    "payload": {
        "prices": [],
    }
}

FIXTURE_PRICE_V2 = {
    "payload": {
        "totalPriceInCents": 1090,
        "travelDiscount": "NO_DISCOUNT",
        "travelClass": "SECOND_CLASS",
        "travelProducts": [],
    }
}

# ---------------------------------------------------------------------------
# Client fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    with NSClient(api_key="test-api-key") as c:
        yield c
