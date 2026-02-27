from __future__ import annotations

from py_ns._base.transport import HttpTransport
from py_ns.models.stations import (
    StationV2,
    StationV3,
    StationsV2Response,
    StationsV3Response,
    StationV3Response,
)

_BASE_URL = "https://gateway.apiportal.ns.nl/nsapp-stations"


class StationsAPI:
    """Wrapper for the NS-APP Stations API."""

    def __init__(self, transport: HttpTransport) -> None:
        self._http = transport

    # -------------------------------------------------------------------------
    # v2 endpoints (Dutch field names)
    # -------------------------------------------------------------------------

    def list_v2(
        self,
        query: str | None = None,
        *,
        country_codes: str | None = None,
        include_non_plannable: bool | None = None,
        limit: int | None = None,
    ) -> list[StationV2]:
        """Search stations (v2, Dutch field names).

        Args:
            query: Free-text search string filtered on station name or synonym.
            country_codes: Comma-separated ISO 3166-1 alpha-2 country codes to
                filter on (e.g. 'NL,BE').
            include_non_plannable: When True, include stations that cannot be
                used as an origin or destination in trip planning.
            limit: Maximum number of stations to return.
        """
        params: dict = {}
        if query is not None:
            params["q"] = query
        if country_codes is not None:
            params["countryCodes"] = country_codes
        if include_non_plannable is not None:
            params["includeNonPlannableStations"] = include_non_plannable
        if limit is not None:
            params["limit"] = limit

        data = self._http.get(f"{_BASE_URL}/v2", params=params)
        return StationsV2Response.model_validate(data).payload

    def list_nearest_v2(
        self,
        lat: float,
        lng: float,
        *,
        limit: int | None = None,
        include_non_plannable: bool | None = None,
    ) -> list[StationV2]:
        """Return the stations closest to the given coordinates (v2).

        Args:
            lat: Latitude of the reference point.
            lng: Longitude of the reference point.
            limit: Maximum number of stations to return.
            include_non_plannable: When True, include non-plannable stations.
        """
        params: dict = {"lat": lat, "lng": lng}
        if limit is not None:
            params["limit"] = limit
        if include_non_plannable is not None:
            params["includeNonPlannableStations"] = include_non_plannable

        data = self._http.get(f"{_BASE_URL}/v2/nearest", params=params)
        return StationsV2Response.model_validate(data).payload

    # -------------------------------------------------------------------------
    # v3 endpoints (English field names)
    # -------------------------------------------------------------------------

    def list_v3(
        self,
        query: str | None = None,
        *,
        country_codes: str | None = None,
        include_non_plannable: bool | None = None,
        limit: int | None = None,
    ) -> list[StationV3]:
        """Search stations (v3, English field names).

        Args:
            query: Free-text search string filtered on station name or synonym.
            country_codes: Comma-separated ISO 3166-1 alpha-2 country codes to
                filter on (e.g. 'NL,BE').
            include_non_plannable: When True, include stations that cannot be
                used as an origin or destination in trip planning.
            limit: Maximum number of stations to return.
        """
        params: dict = {}
        if query is not None:
            params["q"] = query
        if country_codes is not None:
            params["countryCodes"] = country_codes
        if include_non_plannable is not None:
            params["includeNonPlannableStations"] = include_non_plannable
        if limit is not None:
            params["limit"] = limit

        data = self._http.get(f"{_BASE_URL}/v3", params=params)
        return StationsV3Response.model_validate(data).payload

    def list_nearest_v3(
        self,
        lat: float,
        lng: float,
        *,
        limit: int | None = None,
        include_non_plannable: bool | None = None,
    ) -> list[StationV3]:
        """Return the stations closest to the given coordinates (v3).

        Args:
            lat: Latitude of the reference point.
            lng: Longitude of the reference point.
            limit: Maximum number of stations to return.
            include_non_plannable: When True, include non-plannable stations.
        """
        params: dict = {"lat": lat, "lng": lng}
        if limit is not None:
            params["limit"] = limit
        if include_non_plannable is not None:
            params["includeNonPlannableStations"] = include_non_plannable

        data = self._http.get(f"{_BASE_URL}/v3/nearest", params=params)
        return StationsV3Response.model_validate(data).payload

    # -------------------------------------------------------------------------
    # v1 single-station lookup
    # -------------------------------------------------------------------------

    def get(
        self,
        uic_code: str,
        *,
        uic_cd_code: str | None = None,
    ) -> StationV3:
        """Return a single station by UIC code (returns v3 model).

        Args:
            uic_code: Short UIC code for the station (e.g. '8400058').
            uic_cd_code: Long UIC code, if required to disambiguate.
        """
        params: dict = {"uicCode": uic_code}
        if uic_cd_code is not None:
            params["uicCdCode"] = uic_cd_code

        data = self._http.get(f"{_BASE_URL}/v1/station", params=params)
        return StationV3Response.model_validate(data).payload
