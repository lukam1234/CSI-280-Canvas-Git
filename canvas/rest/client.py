"""Canvas LMS REST API Client.
==============================

An async client to interact with the Canvas LMS API.
"""

from __future__ import annotations

from typing import Any, cast

from attrs import define, field
from httpx import AsyncClient, Response

from ..errors import APIError
from ..oauth import CanvasAuth

__all__ = ("CanvasAPIClient",)


@define
class CanvasAPIClient:
    """Async client for Canvas LMS API.

    :param auth: Authentication manager to use.
    :type auth: :class:`CanvasAuth`

    :param prefix: API URL prefix.
    :type prefix: str

    :ivar auth: Authentication manager to use.
    :vartype auth: :class:`CanvasAuth`

    :ivar prefix: API URL prefix.
    :vartype prefix: str
    """

    auth: CanvasAuth = field()
    prefix: str = field(default="/api/v1")

    _client: AsyncClient = field(init=False)
    _base_url: str = field(init=False)

    def __attrs_post_init__(self) -> None:
        self._base_url = self.auth._base_url  # pyright: ignore
        self._client = AsyncClient()

    async def __aenter__(self) -> CanvasAPIClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    def _get_url(self, endpoint: str) -> str:
        """Get the full API URL.

        :param endpoint: API endpoint path.
        :type endpoint: str

        :return: Complete API URL.
        :rtype: str
        """
        return f"{self._base_url}{self.prefix}/{endpoint.lstrip('/')}"

    async def _process_response(self, response: Response) -> dict[str, Any]:
        """Process API response and handle errors.

        :param response: HTTP response to process.
        :type response: :class:`httpx.Response`

        :return: Parsed response data.
        :rtype: dict[str, Any]

        :raises APIError: If the API returns an error response.
        """
        data = response.json() if response.content else None

        if not response.is_success:
            message = "API request failed."
            if isinstance(data, dict):
                data = cast(dict[str, Any], data)
                message = data.get("message", message)

            raise APIError(
                message=message,
                status=response.status_code,
                response=cast(dict[str, Any], data),
            )

        return data or {}

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an authenticated API request.

        :param method: HTTP method to use.
        :type method: str

        :param endpoint: API endpoint to request.
        :type endpoint: str

        :param kwargs: Additional request parameters.
        :type kwargs: Any

        :return: Processed response data.
        :rtype: dict[str, Any]

        :raises APIError: If the API request fails.
        """
        token = await self.auth.fetch_token()

        headers = kwargs.pop("headers", {})
        headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            }
        )

        # TODO: Implement ratelimiting.

        response = await self._client.request(
            method=method,
            url=self._get_url(endpoint),
            headers=headers,
            **kwargs,
        )

        return await self._process_response(response)

    async def get(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a GET request to the API.

        :param endpoint: API endpoint to request.
        :type endpoint: str

        :param kwargs: Additional request parameters.
        :type kwargs: Any

        :return: Response data.
        :rtype: dict[str, Any]
        """
        return await self._request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make a POST request to the API.

        :param endpoint: API endpoint to request.
        :type endpoint: str

        :param kwargs: Additional request parameters.
        :type kwargs: Any

        :return: Response data.
        :rtype: dict[str, Any]
        """
        return await self._request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make a PUT request to the API.

        :param endpoint: API endpoint to request.
        :type endpoint: str

        :param kwargs: Additional request parameters.
        :type kwargs: Any

        :return: Response data.
        :rtype: dict[str, Any]
        """
        return await self._request("PUT", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        """Make a DELETE request to the API.

        :param endpoint: API endpoint to request.
        :type endpoint: str

        :param kwargs: Additional request parameters.
        :type kwargs: Any

        :return: Response data.
        :rtype: dict[str, Any]
        """
        return await self._request("DELETE", endpoint, **kwargs)

    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        await self._client.aclose()
