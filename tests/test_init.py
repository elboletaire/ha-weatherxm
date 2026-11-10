"""Entry setup, unload, retry, failure handling and the filter_owned option."""

import asyncio
import copy
import functools
from unittest.mock import patch

import aiohttp
import pytest
from aiohttp import web
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.weatherxm.const import CONF_FILTER_OWNED_DEVICES, DOMAIN
from custom_components.weatherxm.weatherxm_api import WeatherXMAPI


def spy_on_close():
    """Wrap WeatherXMAPI.close so tests can assert the session was released."""
    return patch.object(WeatherXMAPI, "close", autospec=True, side_effect=WeatherXMAPI.close)


def timeout_client_session():
    """Make every request of the integration's session time out after 0.3s."""
    return patch(
        "aiohttp.ClientSession",
        functools.partial(aiohttp.ClientSession, timeout=aiohttp.ClientTimeout(total=0.3)),
    )


def real_api_entry(hass, host: str) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"username": "user@example.com", "password": "secret", "host": host},
        options={CONF_FILTER_OWNED_DEVICES: True},
    )
    entry.add_to_hass(hass)
    return entry


def station_app(device: dict) -> web.Application:
    """Fake WeatherXM server. Tests change app["control"] to inject failures."""
    app = web.Application()
    app["control"] = {"login": 200, "devices": 200, "forecast": 200, "forecast_delay": 0}

    async def login(request):
        status = request.app["control"]["login"]
        if status != 200:
            return web.Response(status=status, text="InvalidCredentials")
        return web.json_response({"token": "t", "refreshToken": "r"})

    async def devices(request):
        status = request.app["control"]["devices"]
        if status != 200:
            return web.Response(status=status, text="boom")
        return web.json_response([copy.deepcopy(device)])

    async def forecast(request):
        await asyncio.sleep(request.app["control"]["forecast_delay"])
        if request.app["control"]["forecast"] != 200:
            return web.Response(status=request.app["control"]["forecast"], text="boom")
        return web.json_response([])

    app.router.add_post("/api/v1/auth/login", login)
    app.router.add_get("/api/v1/me/devices", devices)
    app.router.add_get("/api/v1/me/devices/{id}/forecast", forecast)
    return app


async def test_entry_loads_and_unloads(hass, device, setup_integration):
    entry = await setup_integration([device()])

    assert entry.state is ConfigEntryState.LOADED
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert entry.entry_id not in hass.data[DOMAIN]
    api.close.assert_awaited_once()


async def test_devices_api_error_schedules_setup_retry(hass, serve, device, socket_enabled):
    app = station_app(device())
    app["control"]["devices"] = 500
    entry = real_api_entry(hass, await serve(app))

    with spy_on_close() as close:
        try:
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
            assert entry.state is ConfigEntryState.SETUP_RETRY
        finally:
            await hass.config_entries.async_unload(entry.entry_id)
    close.assert_awaited_once()


async def test_login_connection_error_schedules_setup_retry(hass, socket_enabled, unused_tcp_port):
    entry = real_api_entry(hass, f"http://127.0.0.1:{unused_tcp_port}")

    with spy_on_close() as close:
        try:
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
            assert entry.state is ConfigEntryState.SETUP_RETRY
        finally:
            await hass.config_entries.async_unload(entry.entry_id)
    close.assert_awaited_once()


@pytest.mark.parametrize("status", [429, 500, 503])
async def test_login_server_error_schedules_setup_retry(hass, serve, device, status):
    app = station_app(device())
    app["control"]["login"] = status
    entry = real_api_entry(hass, await serve(app))

    with spy_on_close() as close:
        try:
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
            assert entry.state is ConfigEntryState.SETUP_RETRY
        finally:
            await hass.config_entries.async_unload(entry.entry_id)
    close.assert_awaited_once()


@pytest.mark.parametrize("status", [400, 401, 403])
async def test_rejected_login_fails_setup_without_retry(hass, serve, device, caplog, status):
    app = station_app(device())
    app["control"]["login"] = status
    entry = real_api_entry(hass, await serve(app))

    with spy_on_close() as close:
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    close.assert_awaited_once()

    assert entry.state is ConfigEntryState.SETUP_ERROR
    assert any("rejected the login" in r.getMessage() for r in caplog.records)


async def test_forecast_http_error_keeps_sensors_populated(hass, serve, device):
    app = station_app(device())
    app["control"]["forecast"] = 500
    entry = real_api_entry(hass, await serve(app))

    try:
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert entry.state is ConfigEntryState.LOADED
        assert hass.states.get("sensor.garden_temperature").state == "18.2"
    finally:
        await hass.config_entries.async_unload(entry.entry_id)


async def test_forecast_timeout_keeps_sensors_populated(hass, serve, device):
    app = station_app(device())
    app["control"]["forecast_delay"] = 1
    entry = real_api_entry(hass, await serve(app))

    try:
        with timeout_client_session():
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()

        assert entry.state is ConfigEntryState.LOADED
        assert hass.states.get("sensor.garden_temperature").state == "18.2"
    finally:
        await hass.config_entries.async_unload(entry.entry_id)


async def test_devices_outage_makes_entities_unavailable_then_recovers(hass, serve, device):
    app = station_app(device())
    entry = real_api_entry(hass, await serve(app))

    try:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        assert hass.states.get("sensor.garden_temperature").state == "18.2"

        app["control"]["devices"] = 500
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert hass.states.get("sensor.garden_temperature").state == STATE_UNAVAILABLE
        assert hass.states.get("binary_sensor.garden_online").state == STATE_UNAVAILABLE

        app["control"]["devices"] = 200
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        assert hass.states.get("sensor.garden_temperature").state == "18.2"
        assert hass.states.get("binary_sensor.garden_online").state == "on"
    finally:
        await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize(
    ("options", "expected_sensors"),
    [
        pytest.param({CONF_FILTER_OWNED_DEVICES: True}, {"garden"}, id="owned-only"),
        pytest.param({CONF_FILTER_OWNED_DEVICES: False}, {"garden", "park"}, id="all-devices"),
        pytest.param({}, {"garden"}, id="option-defaults-to-owned-only"),
    ],
)
async def test_filter_owned_option(hass, device, setup_integration, options, expected_sensors):
    owned = device(id="owned")
    followed = device(id="followed", relation="followed")
    followed["attributes"]["friendlyName"] = "Park"

    await setup_integration([owned, followed], options=options)

    present = {
        alias
        for alias in ("garden", "park")
        if hass.states.get(f"binary_sensor.{alias}_online") is not None
    }
    assert present == expected_sensors
