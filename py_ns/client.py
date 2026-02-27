from py_ns._base.transport import HttpTransport
from py_ns.api.disruptions import DisruptionsAPI
from py_ns.api.stations import StationsAPI
from py_ns.api.travel import TravelAPI


class NSClient:
    """Synchronous client for the NS (Dutch Railways) API.

    Usage::

        client = NSClient(api_key="your-key")
        departures = client.travel.get_departures("ASD")
        disruptions = client.disruptions.list(is_active=True)
        stations = client.stations.list_v3("amsterdam")

    The client can also be used as a context manager to ensure the underlying
    HTTP connection is properly closed::

        with NSClient(api_key="your-key") as client:
            departures = client.travel.get_departures("ASD")
    """

    def __init__(self, api_key: str, *, timeout: float = 30.0) -> None:
        """Create a new NSClient.

        Args:
            api_key: Your NS API subscription key.
            timeout: HTTP request timeout in seconds (default: 30).
        """
        self._transport = HttpTransport(api_key, timeout=timeout)
        self.disruptions = DisruptionsAPI(self._transport)
        self.stations = StationsAPI(self._transport)
        self.travel = TravelAPI(self._transport)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._transport.close()

    def __enter__(self) -> "NSClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
