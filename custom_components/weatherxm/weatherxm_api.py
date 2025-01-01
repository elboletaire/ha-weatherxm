"""WeatherXM API Client."""
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

class WeatherXMError(Exception):
    """Exception to indicate a WeatherXM API error."""

class WeatherXMAPI:
    """WeatherXM API Client."""

    def __init__(self, host: str) -> None:
        """Initialize the API client."""
        self.host = host
        self._session = aiohttp.ClientSession()
        self._auth_token = None
        self._refresh_token = None

    async def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with WeatherXM API."""
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {'username': username, 'password': password}

        try:
            async with self._session.post(
                f'{self.host}/api/v1/auth/login',
                json=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self._auth_token = result['token']
                    self._refresh_token = result['refreshToken']
                    return True
                else:
                    error = await response.text()
                    _LOGGER.error("Authentication failed: %s", error)
                    return False
        except aiohttp.ClientError as err:
            _LOGGER.error("Error during authentication: %s", err)
            return False

    async def refresh_token(self) -> bool:
        """Refresh the authentication token."""
        if not self._refresh_token:
            _LOGGER.error("No refresh token available")
            return False

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {'refreshToken': self._refresh_token}

        try:
            async with self._session.post(
                f'{self.host}/api/v1/auth/refresh',
                json=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self._auth_token = result['token']
                    self._refresh_token = result['refreshToken']
                    return True
                else:
                    error = await response.text()
                    _LOGGER.error("Token refresh failed: %s", error)
                    # Clear tokens on refresh failure
                    self._auth_token = None
                    self._refresh_token = None
                    return False
        except aiohttp.ClientError as err:
            _LOGGER.error("Error during token refresh: %s", err)
            return False

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make an API request with automatic token refresh."""
        if not self._auth_token:
            raise WeatherXMError("Not authenticated")

        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self._auth_token}'
        headers['accept'] = 'application/json'

        url = f'{self.host}/api/v1/{endpoint}'
        _LOGGER.debug("Making API request to %s", endpoint)

        try:
            async with self._session.request(
                method,
                url,
                headers=headers,
                **kwargs
            ) as response:
                if response.status == 401:
                    _LOGGER.debug("Token expired, attempting refresh")
                    # Token expired, try to refresh
                    if await self.refresh_token():
                        # Retry request with new token
                        _LOGGER.debug("Token refreshed, retrying request")
                        headers['Authorization'] = f'Bearer {self._auth_token}'
                        async with self._session.request(
                            method,
                            url,
                            headers=headers,
                            **kwargs
                        ) as retry_response:
                            return await retry_response.json()
                    else:
                        raise WeatherXMError("Token refresh failed")
                elif response.status == 200:
                    _LOGGER.debug("API request successful")
                    return await response.json()
                else:
                    error = await response.text()
                    _LOGGER.error("API request failed with status %s: %s", response.status, error)
                    raise WeatherXMError(f"API request failed: {error}")
        except aiohttp.ClientError as err:
            raise WeatherXMError(f"Request error: {err}")

    async def get_devices(self) -> list:
        """Get user's devices."""
        try:
            return await self._request('GET', 'me/devices')
        except WeatherXMError as err:
            _LOGGER.error("Failed to get devices: %s", err)
            return []

    async def get_forecast_data(self, device_id: str) -> dict:
        """Get forecast data for a device."""
        today = datetime.now().strftime('%Y-%m-%d')
        future = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

        try:
            return await self._request(
                'GET',
                f'me/devices/{device_id}/forecast',
                params={'fromDate': today, 'toDate': future}
            )
        except WeatherXMError as err:
            _LOGGER.error("Failed to get forecast data: %s", err)
            return {}

    async def close(self) -> None:
        """Close the API client."""
        if self._session:
            await self._session.close()
