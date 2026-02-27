from __future__ import annotations

import warnings
from datetime import datetime

from py_ns._base.transport import HttpTransport
from py_ns.models.travel import (
    Arrival,
    CalamitiesResponse,
    Departure,
    Journey,
    Price,
    PricesResponseV3,
    RepresentationResponseArrivalsPayload,
    RepresentationResponseDeparturesPayload,
    RepresentationResponseJourney,
    RepresentationResponsePrice,
    RepresentationResponsePricesResponseV3,
    Station,
    StationResponse,
    TravelAdvice,
    TravelClass,
    TravelDiscount,
    TravelProduct,
    Trip,
)

_BASE_URL = "https://gateway.apiportal.ns.nl/reisinformatie-api"

# Deprecation message templates
_DISRUPTIONS_DEPRECATION = (
    "{method} is deprecated by NS. Use {replacement} instead, which uses the "
    "dedicated Disruptions API (https://gateway.apiportal.ns.nl/disruptions)."
)
_STATIONS_DEPRECATION = (
    "{method} is deprecated by NS. Use the dedicated Stations API at "
    "https://gateway.apiportal.ns.nl/nsapp-stations instead."
)


class TravelAPI:
    """Wrapper for the NS Reisinformatie (Travel Information) API."""

    def __init__(self, transport: HttpTransport) -> None:
        self._http = transport

    # -------------------------------------------------------------------------
    # Departures and arrivals
    # -------------------------------------------------------------------------

    def get_departures(
        self,
        station: str,
        *,
        uic_code: str | None = None,
        date_time: datetime | None = None,
        max_journeys: int = 40,
        language: str | None = None,
    ) -> list[Departure]:
        """Return upcoming departures for a station.

        Args:
            station: NS station code (e.g. 'ASD'). Omit if uic_code is given.
            uic_code: UIC station code. Alternative to station.
            date_time: Return departures from this moment onward (default: now).
                Only supported for foreign stations; domestic defaults to server time.
            max_journeys: Maximum number of departures to return (default: 40).
            language: BCP-47 language tag for localised text (e.g. 'nl', 'en').
        """
        params: dict = {"maxJourneys": max_journeys}
        if station:
            params["station"] = station
        if uic_code is not None:
            params["uicCode"] = uic_code
        if date_time is not None:
            params["dateTime"] = date_time.isoformat()
        if language is not None:
            params["lang"] = language

        data = self._http.get(f"{_BASE_URL}/api/v2/departures", params=params)
        response = RepresentationResponseDeparturesPayload.model_validate(data)
        return response.payload.departures

    def get_arrivals(
        self,
        station: str,
        *,
        uic_code: str | None = None,
        date_time: datetime | None = None,
        max_journeys: int = 40,
        language: str | None = None,
    ) -> list[Arrival]:
        """Return upcoming arrivals for a station.

        Args:
            station: NS station code (e.g. 'ASD'). Omit if uic_code is given.
            uic_code: UIC station code. Alternative to station.
            date_time: Return arrivals from this moment onward (default: now).
                Only supported for foreign stations; domestic defaults to server time.
            max_journeys: Maximum number of arrivals to return (default: 40).
            language: BCP-47 language tag for localised text (e.g. 'nl', 'en').
        """
        params: dict = {"maxJourneys": max_journeys}
        if station:
            params["station"] = station
        if uic_code is not None:
            params["uicCode"] = uic_code
        if date_time is not None:
            params["dateTime"] = date_time.isoformat()
        if language is not None:
            params["lang"] = language

        data = self._http.get(f"{_BASE_URL}/api/v2/arrivals", params=params)
        response = RepresentationResponseArrivalsPayload.model_validate(data)
        return response.payload.arrivals

    # -------------------------------------------------------------------------
    # Journey details
    # -------------------------------------------------------------------------

    def get_journey(
        self,
        *,
        train: int | None = None,
        journey_id: str | None = None,
        date_time: datetime | None = None,
        departure_uic_code: str | None = None,
        transfer_uic_code: str | None = None,
        arrival_uic_code: str | None = None,
        omit_crowd_forecast: bool = False,
    ) -> Journey:
        """Return details for a specific journey.

        Either train or journey_id must be provided.

        Args:
            train: Train number (e.g. 6952).
            journey_id: Journey identifier from the journeyDetailRef field
                in /api/v3/trips output (e.g. '1|231691|0|784|15122020').
            date_time: Date for this journey (default: now).
            departure_uic_code: UIC code of the station to mark as DEPARTURE.
            transfer_uic_code: UIC code of the station to mark as TRANSFER.
            arrival_uic_code: UIC code of the station to mark as ARRIVAL.
            omit_crowd_forecast: When True, omit crowd forecast data.
        """
        params: dict = {"omitCrowdForecast": omit_crowd_forecast}
        if train is not None:
            params["train"] = train
        if journey_id is not None:
            params["id"] = journey_id
        if date_time is not None:
            params["dateTime"] = date_time.isoformat()
        if departure_uic_code is not None:
            params["departureUicCode"] = departure_uic_code
        if transfer_uic_code is not None:
            params["transferUicCode"] = transfer_uic_code
        if arrival_uic_code is not None:
            params["arrivalUicCode"] = arrival_uic_code

        data = self._http.get(f"{_BASE_URL}/api/v2/journey", params=params)
        response = RepresentationResponseJourney.model_validate(data)
        return response.payload

    # -------------------------------------------------------------------------
    # Trip planning
    # -------------------------------------------------------------------------

    def plan_trip(
        self,
        from_station: str | None = None,
        to_station: str | None = None,
        *,
        # Origin alternatives
        origin_uic_code: str | None = None,
        origin_lat: float | None = None,
        origin_lng: float | None = None,
        origin_name: str | None = None,
        # Destination alternatives
        destination_uic_code: str | None = None,
        destination_lat: float | None = None,
        destination_lng: float | None = None,
        destination_name: str | None = None,
        # Via
        via_station: str | None = None,
        via_uic_code: str | None = None,
        via_lat: float | None = None,
        via_lng: float | None = None,
        via_wait_time: int | None = None,
        # When
        date_time: datetime | None = None,
        search_for_arrival: bool = False,
        # General options
        language: str | None = None,
        context: str | None = None,
        add_change_time: int | None = None,
        passing: bool | None = None,
        local_trains_only: bool | None = None,
        exclude_high_speed_trains: bool | None = None,
        exclude_trains_with_reservation_required: bool | None = None,
        travel_request_type: str | None = None,
        filter_transport_mode: str | None = None,
        disabled_transport_modalities: list[str] | None = None,
        # First / last mile modalities
        origin_walk: bool | None = None,
        origin_bike: bool | None = None,
        origin_car: bool | None = None,
        destination_walk: bool | None = None,
        destination_bike: bool | None = None,
        destination_car: bool | None = None,
        first_mile_modality: str | None = None,
        last_mile_modality: str | None = None,
        entire_trip_modality: str | None = None,
        # Accessibility
        travel_assistance: bool | None = None,
        search_for_accessible_trip: bool | None = None,
        accessibility_equipment1: str | None = None,
        accessibility_equipment2: str | None = None,
        # Pricing
        product: str | None = None,
        discount: str | None = None,
        travel_class: int | None = None,
        # Authentication (required for travel assistance options)
        authorization: str | None = None,
        nsr: int | None = None,
        # Deprecated parameters — warn on use
        departure: bool | None = None,
        shorter_change: bool | None = None,
        minimal_change_time: int | None = None,
        origin_accessible: bool | None = None,
        travel_assistance_transfer_time: int | None = None,
    ) -> TravelAdvice:
        """Return travel advice for a journey between two locations.

        The result contains a list of Trip options accessible via ``.trips``,
        each with legs, stops, and fare information.

        Origin and destination can be specified as NS station codes, UIC codes,
        or coordinates. At least one origin and one destination must be given.

        Args:
            from_station: Origin NS station code (e.g. 'ASD').
            to_station: Destination NS station code (e.g. 'UT').
            origin_uic_code: UIC code of the origin station.
            origin_lat: Latitude of a custom origin location.
            origin_lng: Longitude of a custom origin location.
            origin_name: Display name for a custom origin location.
            destination_uic_code: UIC code of the destination station.
            destination_lat: Latitude of a custom destination location.
            destination_lng: Longitude of a custom destination location.
            destination_name: Display name for a custom destination location.
            via_station: NS station code of an intermediate via station.
            via_uic_code: UIC code of the via station.
            via_lat: Latitude of a custom via location.
            via_lng: Longitude of a custom via location.
            via_wait_time: Required waiting time at the via stop (minutes).
            date_time: Departure (or arrival) datetime (default: now).
            search_for_arrival: When True, treat date_time as desired arrival.
            language: BCP-47 language tag for localised text.
            context: Pagination context from a previous response for next/prev page.
            add_change_time: Extra minutes required at all transfers.
            passing: Include intermediate stops the train passes without stopping.
            local_trains_only: Restrict results to local trains only.
            exclude_high_speed_trains: Exclude high-speed trains (Thalys etc.).
            exclude_trains_with_reservation_required: Exclude trains needing a reservation.
            travel_request_type: 'DEFAULT', 'DIRECTIONS', or 'DIRECTIONS_ONLY'.
            filter_transport_mode: Filter for REGIONAL_TRAINS. Prefer local_trains_only.
            disabled_transport_modalities: List of modalities to exclude.
            origin_walk / origin_bike / origin_car: Enable first-mile modalities.
            destination_walk / destination_bike / destination_car: Enable last-mile modalities.
            first_mile_modality: Shared modality filter for the first mile.
            last_mile_modality: Shared modality filter for the last mile.
            entire_trip_modality: Shared modality filter for the entire trip.
            travel_assistance: Request trip options from the travel assistance engine.
            search_for_accessible_trip: Return only wheelchair-accessible trips.
            accessibility_equipment1: Accessibility equipment code.
            accessibility_equipment2: Second accessibility equipment code.
            product: Product name for price calculations.
            discount: Discount to apply for price calculations.
            travel_class: Travel class for price calculations (1 or 2).
            authorization: Bearer token for travel assistance (PAS) options.
            nsr: NSR customer number (no longer used, kept for compatibility).

        Deprecated args (emit DeprecationWarning when used):
            departure: Use search_for_arrival=True instead.
            shorter_change: Removed; no replacement.
            minimal_change_time: Use add_change_time instead.
            origin_accessible: Use travel_assistance instead.
            travel_assistance_transfer_time: Use add_change_time instead.
        """
        if departure is not None:
            warnings.warn(
                "The 'departure' parameter is deprecated. Use 'search_for_arrival' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        if shorter_change is not None:
            warnings.warn(
                "The 'shorter_change' parameter is deprecated and has no effect. "
                "NS removed this functionality.",
                DeprecationWarning,
                stacklevel=2,
            )
        if minimal_change_time is not None:
            warnings.warn(
                "The 'minimal_change_time' parameter is deprecated. "
                "Use 'add_change_time' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        if origin_accessible is not None:
            warnings.warn(
                "The 'origin_accessible' parameter is deprecated. "
                "Use 'travel_assistance' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        if travel_assistance_transfer_time is not None:
            warnings.warn(
                "The 'travel_assistance_transfer_time' parameter is deprecated. "
                "Use 'add_change_time' instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        params: dict = {}
        _set(params, "fromStation", from_station)
        _set(params, "toStation", to_station)
        _set(params, "originUicCode", origin_uic_code)
        _set(params, "originLat", origin_lat)
        _set(params, "originLng", origin_lng)
        _set(params, "originName", origin_name)
        _set(params, "destinationUicCode", destination_uic_code)
        _set(params, "destinationLat", destination_lat)
        _set(params, "destinationLng", destination_lng)
        _set(params, "destinationName", destination_name)
        _set(params, "viaStation", via_station)
        _set(params, "viaUicCode", via_uic_code)
        _set(params, "viaLat", via_lat)
        _set(params, "viaLng", via_lng)
        _set(params, "viaWaitTime", via_wait_time)
        _set(params, "dateTime", date_time.isoformat() if date_time else None)
        _set(params, "searchForArrival", search_for_arrival or None)
        _set(params, "lang", language)
        _set(params, "context", context)
        _set(params, "addChangeTime", add_change_time)
        _set(params, "passing", passing)
        _set(params, "localTrainsOnly", local_trains_only)
        _set(params, "excludeHighSpeedTrains", exclude_high_speed_trains)
        _set(params, "excludeTrainsWithReservationRequired", exclude_trains_with_reservation_required)
        _set(params, "travelRequestType", travel_request_type)
        _set(params, "filterTransportMode", filter_transport_mode)
        _set(params, "disabledTransportModalities", disabled_transport_modalities)
        _set(params, "originWalk", origin_walk)
        _set(params, "originBike", origin_bike)
        _set(params, "originCar", origin_car)
        _set(params, "destinationWalk", destination_walk)
        _set(params, "destinationBike", destination_bike)
        _set(params, "destinationCar", destination_car)
        _set(params, "firstMileModality", first_mile_modality)
        _set(params, "lastMileModality", last_mile_modality)
        _set(params, "entireTripModality", entire_trip_modality)
        _set(params, "travelAssistance", travel_assistance)
        _set(params, "searchForAccessibleTrip", search_for_accessible_trip)
        _set(params, "accessibilityEquipment1", accessibility_equipment1)
        _set(params, "accessibilityEquipment2", accessibility_equipment2)
        _set(params, "product", product)
        _set(params, "discount", discount)
        _set(params, "travelClass", travel_class)
        _set(params, "nsr", nsr)
        # Deprecated — pass through if provided
        _set(params, "departure", departure)
        _set(params, "shorterChange", shorter_change)
        _set(params, "minimalChangeTime", minimal_change_time)
        _set(params, "originAccessible", origin_accessible)
        _set(params, "travelAssistanceTransferTime", travel_assistance_transfer_time)

        headers: dict[str, str] | None = None
        if authorization is not None:
            headers = {"Authorization": authorization}

        data = self._http.get(f"{_BASE_URL}/api/v3/trips", params=params, headers=headers)
        return TravelAdvice.model_validate(data)

    def get_trip(
        self,
        ctx_recon: str,
        *,
        date: datetime | None = None,
        travel_request_type: str = "DEFAULT",
        product: str | None = None,
        discount: str | None = None,
        travel_class: int | None = None,
        authorization: str | None = None,
        language: str | None = None,
        nsr: int | None = None,
        # Deprecated
        source_ctx_recon: bool | None = None,
    ) -> Trip:
        """Reconstruct a single trip from a context reconstruction string.

        The ctxRecon string can be found in the output of plan_trip().

        Args:
            ctx_recon: Reconstruction context (ctxRecon) from plan_trip output.
            date: Date to use when reconstructing, may differ from original.
            travel_request_type: 'DEFAULT', 'DIRECTIONS', or 'DIRECTIONS_ONLY'.
            product: Product name for price calculations.
            discount: Discount for price calculations.
            travel_class: Travel class for price calculations (1 or 2).
            authorization: Bearer token for travel assistance options.
            language: BCP-47 language tag for localised text.
            nsr: NSR customer number (no longer used).

        Deprecated args:
            source_ctx_recon: Deprecated. Use the sourceCtxRecon field in the
                Trip response instead.
        """
        if source_ctx_recon is not None:
            warnings.warn(
                "The 'source_ctx_recon' parameter is deprecated. "
                "Use the sourceCtxRecon field in the Trip response instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        params: dict = {"ctxRecon": ctx_recon, "travelRequestType": travel_request_type}
        _set(params, "date", date.isoformat() if date else None)
        _set(params, "product", product)
        _set(params, "discount", discount)
        _set(params, "travelClass", travel_class)
        _set(params, "nsr", nsr)
        _set(params, "sourceCtxRecon", source_ctx_recon)

        headers: dict[str, str] | None = None
        if authorization is not None:
            headers = {"Authorization": authorization}
        if language is not None:
            headers = {**(headers or {}), "lang": language}

        data = self._http.get(f"{_BASE_URL}/api/v3/trips/trip", params=params, headers=headers)
        return Trip.model_validate(data)

    def get_booked_trip(
        self,
        ctx_recon: str,
        booking_number: int,
        original_trip_request_id: int,
        authorization: str,
        *,
        accessibility_equipment1: str | None = None,
        accessibility_equipment2: str | None = None,
        language: str | None = None,
    ) -> Trip:
        """Return a booked trip from the travel assistance system.

        Args:
            ctx_recon: Reconstruction context (ctxRecon) from plan_trip output.
            booking_number: The booking number from the NS Customer API.
            original_trip_request_id: The ID returned by the travel assistance
                backend when the travel advice was requested.
            authorization: Bearer token (required for booked trips).
            accessibility_equipment1: Accessibility equipment code.
            accessibility_equipment2: Second accessibility equipment code.
            language: BCP-47 language tag for localised text.
        """
        params: dict = {
            "ctxRecon": ctx_recon,
            "bookingNumber": booking_number,
            "originalTripRequestId": original_trip_request_id,
        }
        _set(params, "accessibilityEquipment1", accessibility_equipment1)
        _set(params, "accessibilityEquipment2", accessibility_equipment2)

        headers: dict[str, str] = {"Authorization": authorization}
        if language is not None:
            headers["lang"] = language

        data = self._http.get(
            f"{_BASE_URL}/api/v3/trips/booked-trip", params=params, headers=headers
        )
        return Trip.model_validate(data)

    # -------------------------------------------------------------------------
    # Pricing
    # -------------------------------------------------------------------------

    def get_price(
        self,
        *,
        from_station: str | None = None,
        to_station: str | None = None,
        travel_class: TravelClass | None = None,
        travel_type: str | None = None,
        is_joint_journey: bool = False,
        adults: int = 1,
        children: int = 0,
        route_id: str | None = None,
        planned_departure_time: datetime | None = None,
        planned_arrival_time: datetime | None = None,
    ) -> PricesResponseV3:
        """Return domestic price information (v3).

        Station codes and UIC codes are both accepted for from_station/to_station.

        Args:
            from_station: Origin station code or UIC code.
            to_station: Destination station code or UIC code.
            travel_class: FIRST_CLASS or SECOND_CLASS.
            travel_type: 'single' or 'return'.
            is_joint_journey: Include joint journey discount when True.
            adults: Number of adults (default: 1).
            children: Number of children (default: 0).
            route_id: Specific route ID from plan_trip output.
            planned_departure_time: Planned departure time (to resolve route).
            planned_arrival_time: Planned arrival time (to resolve route).
        """
        params: dict = {
            "isJointJourney": is_joint_journey,
            "adults": adults,
            "children": children,
        }
        _set(params, "fromStation", from_station)
        _set(params, "toStation", to_station)
        _set(params, "travelClass", travel_class.value if travel_class else None)
        _set(params, "travelType", travel_type)
        _set(params, "routeId", route_id)
        _set(params, "plannedDepartureTime", planned_departure_time.isoformat() if planned_departure_time else None)
        _set(params, "plannedArrivalTime", planned_arrival_time.isoformat() if planned_arrival_time else None)

        data = self._http.get(f"{_BASE_URL}/api/v3/price", params=params)
        response = RepresentationResponsePricesResponseV3.model_validate(data)
        return response.payload

    def get_price_v2(
        self,
        *,
        from_station: str | None = None,
        to_station: str | None = None,
        travel_class: str | None = None,
        travel_type: str | None = None,
        is_joint_journey: bool = False,
        adults: int = 1,
        children: int = 0,
        route_id: str | None = None,
        planned_from_time: datetime | None = None,
        planned_arrival_time: datetime | None = None,
    ) -> Price:
        """Return domestic price information (v2, legacy).

        Prefer get_price() (v3) where possible. The v2 endpoint uses integer
        strings ('1', '2') for travel_class instead of 'FIRST_CLASS'/'SECOND_CLASS'.

        Args:
            from_station: Origin NS station code.
            to_station: Destination NS station code.
            travel_class: '1' for first class, '2' for second class.
            travel_type: 'single' or 'return'.
            is_joint_journey: Include joint journey discount when True.
            adults: Number of adults (default: 1).
            children: Number of children (default: 0).
            route_id: Specific route ID from plan_trip output.
            planned_from_time: Planned departure time (to resolve route).
            planned_arrival_time: Planned arrival time (to resolve route).
        """
        params: dict = {
            "isJointJourney": is_joint_journey,
            "adults": adults,
            "children": children,
        }
        _set(params, "fromStation", from_station)
        _set(params, "toStation", to_station)
        _set(params, "travelClass", travel_class)
        _set(params, "travelType", travel_type)
        _set(params, "routeId", route_id)
        _set(params, "plannedFromTime", planned_from_time.isoformat() if planned_from_time else None)
        _set(params, "plannedArrivalTime", planned_arrival_time.isoformat() if planned_arrival_time else None)

        data = self._http.get(f"{_BASE_URL}/api/v2/price", params=params)
        response = RepresentationResponsePrice.model_validate(data)
        return response.payload

    # -------------------------------------------------------------------------
    # Stations
    # -------------------------------------------------------------------------

    def get_stations(
        self,
        query: str | None = None,
        *,
        country_codes: list[str] | None = None,
        limit: int = 10,
    ) -> list[Station]:
        """Return NS stations, optionally filtered by name or country.

        .. deprecated::
            This endpoint is deprecated by NS. Use the dedicated Stations API
            at https://gateway.apiportal.ns.nl/nsapp-stations instead.

        Args:
            query: Partial station name to filter results (min 2 characters).
            country_codes: Country codes to filter by (e.g. ['nl', 'b', 'd']).
            limit: Maximum results when using query (default: 10).
        """
        warnings.warn(
            _STATIONS_DEPRECATION.format(method="get_stations()"),
            DeprecationWarning,
            stacklevel=2,
        )
        params: dict = {"limit": limit}
        if query is not None:
            params["q"] = query
        if country_codes is not None:
            params["countryCodes"] = ",".join(country_codes)

        data = self._http.get(f"{_BASE_URL}/api/v2/stations", params=params)
        response = StationResponse.model_validate(data)
        return response.payload

    def get_nearest_stations(
        self,
        lat: float,
        lng: float,
        *,
        limit: int = 2,
    ) -> list[Station]:
        """Return stations closest to the given coordinates.

        .. deprecated::
            This endpoint is deprecated by NS. Use the dedicated Stations API
            at https://gateway.apiportal.ns.nl/nsapp-stations/nearest instead.

        Args:
            lat: Latitude.
            lng: Longitude.
            limit: Number of stations to return (default: 2).
        """
        warnings.warn(
            _STATIONS_DEPRECATION.format(method="get_nearest_stations()"),
            DeprecationWarning,
            stacklevel=2,
        )
        params: dict = {"lat": lat, "lng": lng, "limit": limit}
        data = self._http.get(f"{_BASE_URL}/api/v2/stations/nearest", params=params)
        response = StationResponse.model_validate(data)
        return response.payload

    # -------------------------------------------------------------------------
    # Deprecated disruption endpoints (superseded by DisruptionsAPI)
    # -------------------------------------------------------------------------

    def get_calamities(
        self,
        *,
        language: str | None = None,
    ) -> CalamitiesResponse:
        """Return active calamities.

        .. deprecated::
            This endpoint is deprecated by NS. Use
            ``client.disruptions.list(disruption_type=DisruptionType.calamity)``
            instead, which uses the dedicated Disruptions API.

        Args:
            language: Language for localising the calamities.
        """
        warnings.warn(
            _DISRUPTIONS_DEPRECATION.format(
                method="get_calamities()",
                replacement="client.disruptions.list(disruption_type=DisruptionType.calamity)",
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        params: dict = {}
        _set(params, "lang", language)
        data = self._http.get(f"{_BASE_URL}/api/v1/calamities", params=params)
        return CalamitiesResponse.model_validate(data)

    def list_disruptions(
        self,
        *,
        disruption_type: list[str] | None = None,
        is_active: bool = False,
        language: str | None = None,
    ) -> list:
        """Return disruptions, maintenance, and calamities.

        .. deprecated::
            This endpoint is deprecated by NS. Use
            ``client.disruptions.list()`` instead, which uses the dedicated
            Disruptions API at https://gateway.apiportal.ns.nl/disruptions/v3.

        Args:
            disruption_type: Filter by type(s): 'CALAMITY', 'DISRUPTION', 'MAINTENANCE'.
            is_active: Return only currently active items when True.
            language: BCP-47 language tag (e.g. 'nl-NL').
        """
        warnings.warn(
            _DISRUPTIONS_DEPRECATION.format(
                method="list_disruptions()",
                replacement="client.disruptions.list()",
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        params: dict = {"isActive": is_active}
        if disruption_type is not None:
            params["type"] = disruption_type

        headers: dict[str, str] | None = None
        if language is not None:
            headers = {"Accept-Language": language}

        return self._http.get(
            f"{_BASE_URL}/api/v3/disruptions", params=params, headers=headers
        )

    def list_station_disruptions(
        self,
        station_code: str,
    ) -> list:
        """Return disruptions affecting a specific station.

        .. deprecated::
            This endpoint is deprecated by NS. Use
            ``client.disruptions.list_for_station()`` instead, which uses the
            dedicated Disruptions API.

        Args:
            station_code: The NS station code (e.g. 'ASD').
        """
        warnings.warn(
            _DISRUPTIONS_DEPRECATION.format(
                method="list_station_disruptions()",
                replacement="client.disruptions.list_for_station()",
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return self._http.get(
            f"{_BASE_URL}/api/v3/disruptions/station/{station_code}"
        )

    def get_disruption(
        self,
        disruption_type: str,
        disruption_id: str,
    ) -> dict:
        """Return a single disruption by type and ID.

        .. deprecated::
            This endpoint is deprecated by NS. Use
            ``client.disruptions.get()`` instead, which uses the dedicated
            Disruptions API.

        Args:
            disruption_type: 'CALAMITY', 'DISRUPTION', or 'MAINTENANCE'.
            disruption_id: Unique identifier of the disruption.
        """
        warnings.warn(
            _DISRUPTIONS_DEPRECATION.format(
                method="get_disruption()",
                replacement="client.disruptions.get()",
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return self._http.get(
            f"{_BASE_URL}/api/v3/disruptions/{disruption_type}/{disruption_id}"
        )


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

def _set(params: dict, key: str, value: object) -> None:
    """Add key/value to params only when value is not None."""
    if value is not None:
        params[key] = value
