from typing import Any

import httpx

from py_ns.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)


class HttpTransport:
    """
    Thin wrapper around httpx.Client that handles authentication,
    response parsing, and error mapping.

    This class is internal. API namespace classes depend on it;
    end users interact only with NSClient.
    """

    def __init__(self, api_key: str, timeout: float = 30.0) -> None:
        self._client = httpx.Client(
            headers={"Ocp-Apim-Subscription-Key": api_key},
            timeout=timeout,
        )

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        response = self._client.get(url, params=params, headers=headers)
        return self._handle_response(response)

    def post(
        self,
        url: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        response = self._client.post(url, json=json, headers=headers)
        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> Any:
        if response.is_success:
            if not response.content:
                return None
            return response.json()

        message = self._extract_error_message(response)
        match response.status_code:
            case 401 | 403:
                raise AuthenticationError(message, response.status_code)
            case 404:
                raise NotFoundError(message, response.status_code)
            case 429:
                raise RateLimitError(message, response.status_code)
            case status if status >= 500:
                raise ServerError(message, response.status_code)
            case _:
                raise APIError(message, response.status_code)

    def _extract_error_message(self, response: httpx.Response) -> str:
        try:
            data = response.json()
            if isinstance(data, dict):
                return data.get("message", response.text)
        except Exception:
            pass
        return response.text

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpTransport":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
