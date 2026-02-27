from __future__ import annotations

from py_ns._base.transport import HttpTransport
from py_ns.models.disruptions import (
    Calamity,
    Disruption,
    DisruptionType,
    PersonalDisruption,
    SyncSavedTripsRequest,
)

_BASE_URL = "https://gateway.apiportal.ns.nl/disruptions"


def _parse_item(item: dict) -> Disruption | Calamity:
    """Dispatch a raw API response item to the correct concrete model."""
    if item.get("type") == "CALAMITY":
        return Calamity.model_validate(item)
    return Disruption.model_validate(item)


class DisruptionsAPI:
    """Wrapper for the NS Disruptions API."""

    def __init__(self, transport: HttpTransport) -> None:
        self._http = transport

    def list(
        self,
        *,
        is_active: bool | None = None,
        disruption_type: DisruptionType | None = None,
        language: str | None = None,
    ) -> list[Disruption | Calamity]:
        """Return all disruptions, optionally filtered by active state or type.

        Args:
            is_active: When True, return only currently active disruptions.
            disruption_type: Filter by DISRUPTION, MAINTENANCE, or CALAMITY.
            language: BCP-47 language tag for localised text (e.g. 'nl', 'en').
        """
        params: dict = {}
        if is_active is not None:
            params["isActive"] = is_active
        if disruption_type is not None:
            params["type"] = disruption_type.value

        headers: dict[str, str] | None = None
        if language is not None:
            headers = {"Accept-Language": language}

        data = self._http.get(f"{_BASE_URL}/v3", params=params, headers=headers)
        return [_parse_item(item) for item in data]

    def get(
        self,
        disruption_type: DisruptionType,
        disruption_id: str,
        *,
        language: str | None = None,
    ) -> Disruption | Calamity:
        """Return a single disruption by type and ID.

        Args:
            disruption_type: The type of the disruption.
            disruption_id: The unique identifier of the disruption.
            language: BCP-47 language tag for localised text.
        """
        headers: dict[str, str] | None = None
        if language is not None:
            headers = {"Accept-Language": language}

        data = self._http.get(
            f"{_BASE_URL}/v3/{disruption_type.value}/{disruption_id}",
            headers=headers,
        )
        return _parse_item(data)

    def list_for_station(
        self,
        station_code: str,
        *,
        language: str | None = None,
    ) -> list[Disruption | Calamity]:
        """Return all disruptions affecting a specific station.

        Args:
            station_code: The NS station code (e.g. 'ASD' for Amsterdam Centraal).
            language: BCP-47 language tag for localised text.
        """
        headers: dict[str, str] | None = None
        if language is not None:
            headers = {"Accept-Language": language}

        data = self._http.get(
            f"{_BASE_URL}/v3/station/{station_code}", headers=headers
        )
        return [_parse_item(item) for item in data]

    def list_personal(
        self,
        push_id: str,
    ) -> list[PersonalDisruption]:
        """Return personalised disruption information for an NS app user.

        Args:
            push_id: The push ID of the NS app user (x-ns-push-id).
        """
        data = self._http.get(
            f"{_BASE_URL}/v1/personal-disruptions",
            headers={"x-ns-push-id": push_id},
        )
        return [PersonalDisruption.model_validate(item) for item in data]

    def sync_saved_trips(
        self,
        api_key: str,
        saved_trip: SyncSavedTripsRequest,
    ) -> None:
        """Sync a saved trip from the NS reiswijzer with the disruptions API.

        Args:
            api_key: The x-api-key required to sync saved trips.
            saved_trip: The saved trip to sync.
        """
        self._http.post(
            f"{_BASE_URL}/v1/personal-disruptions/sync/saved-trips",
            json=saved_trip.model_dump(by_alias=True),
            headers={"x-api-key": api_key},
        )
