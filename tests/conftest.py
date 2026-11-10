"""Shared fixtures: a sample device, a sample forecast and a mocked-API setup helper."""

import copy
from collections.abc import AsyncIterator, Awaitable, Callable
from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import web
from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.weatherxm.const import CONF_FILTER_OWNED_DEVICES, DEFAULT_HOST, DOMAIN

ENTRY_DATA = {"username": "user@example.com", "password": "secret", "host": DEFAULT_HOST}

SAMPLE_DEVICE = {
    "id": "dev1",
    "name": "Some Name",
    "relation": "owned",
    "label": "AB:CD",
    "timezone": "Europe/Madrid",
    "address": "Barcelona",
    "profile": "Helium",
    "bat_state": "ok",
    "location": {"lat": 41.38, "lon": 2.17},
    "attributes": {
        "friendlyName": "Garden",
        "isActive": True,
        "firmware": {"current": "1.0", "assigned": "1.1"},
        "lastWeatherStationActivity": "2026-11-10T10:00:00+00:00",
        "lastActiveAt": "2026-11-10T10:00:00+00:00",
        "claimedAt": "2024-08-30T11:58:02+02:00",
    },
    "rewards": {"actual_reward": 1.5, "total_rewards": 100.2},
    "bundle": {
        "name": "h1",
        "title": "Helium",
        "connectivity": "helium",
        "ws_model": "WS2000",
        "gw_model": "WG2000",
        "url": "https://example.com/docs",
    },
    "metrics": {"qod_score": 78, "pol_reason": None, "ts": "2026-11-10T01:00:00+00:00"},
    "current_weather": {
        "timestamp": "2026-11-10T10:00:00+00:00",
        "temperature": 18.2,
        "feels_like": 17.9,
        "humidity": 70,
        "dew_point": 12.5,
        "wind_speed": 2.1,
        "wind_gust": 4.3,
        "wind_direction": 180,
        "pressure": 1013.2,
        "uv_index": 3,
        "solar_irradiance": 250.5,
        "precipitation": 0.2,
        "precipitation_accumulated": 1.4,
        "icon": "overcast-night",
    },
}

SAMPLE_FORECAST = [
    {
        "date": "2026-11-10",
        "daily": {
            "timestamp": "2026-11-10T00:00:00+00:00",
            "temperature_max": 20,
            "temperature_min": 10,
            "icon": "overcast-day",
        },
        "hourly": [
            {"timestamp": "2026-11-10T11:00:00+00:00", "temperature": 18, "icon": "rain"},
        ],
    }
]


@pytest.fixture
async def serve(socket_enabled) -> AsyncIterator[Callable[[web.Application], Awaitable[str]]]:
    """Start an aiohttp app on a free local port and return its base URL."""
    runners: list[web.AppRunner] = []

    async def _serve(app: web.Application) -> str:
        runner = web.AppRunner(app)
        await runner.setup()
        runners.append(runner)
        await web.TCPSite(runner, "127.0.0.1", 0).start()
        return f"http://127.0.0.1:{runner.addresses[0][1]}"

    yield _serve

    for runner in runners:
        await runner.cleanup()


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow HA to load the custom_components/weatherxm integration in every test."""
    yield


@pytest.fixture
def device() -> Callable[..., dict]:
    """Factory returning a fresh copy of the sample device, with top-level overrides applied."""

    def make(**overrides) -> dict:
        dev = copy.deepcopy(SAMPLE_DEVICE)
        dev.update(overrides)
        return dev

    return make


@pytest.fixture
async def setup_integration(hass) -> AsyncIterator[Callable[..., Awaitable[MockConfigEntry]]]:
    """Set up a WeatherXM entry with the API class mocked to return the given devices.

    Entries still loaded or waiting for retry are unloaded at teardown so no timers leak.
    """
    entries: list[MockConfigEntry] = []

    async def _setup(
        devices: list[dict] | None = None,
        *,
        forecast=None,
        options: dict | None = None,
    ) -> MockConfigEntry:
        entry = MockConfigEntry(
            domain=DOMAIN,
            data=ENTRY_DATA,
            options=options if options is not None else {CONF_FILTER_OWNED_DEVICES: True},
        )
        entry.add_to_hass(hass)
        entries.append(entry)

        with patch("custom_components.weatherxm.WeatherXMAPI") as api_cls:
            api = api_cls.return_value
            api.authenticate = AsyncMock(return_value=True)
            api.get_devices = AsyncMock(return_value=copy.deepcopy(devices or []))
            api.get_forecast_data = AsyncMock(
                return_value=copy.deepcopy(SAMPLE_FORECAST if forecast is None else forecast)
            )
            api.close = AsyncMock()
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
        return entry

    yield _setup

    for entry in entries:
        if entry.state in (ConfigEntryState.LOADED, ConfigEntryState.SETUP_RETRY):
            await hass.config_entries.async_unload(entry.entry_id)
