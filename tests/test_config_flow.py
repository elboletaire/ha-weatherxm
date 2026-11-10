"""Config flow against a real WeatherXMAPI talking to a local fake server."""

import copy

import pytest
from aiohttp import web
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.weatherxm.const import DOMAIN


@pytest.fixture
def fake_app(device):
    """Serve the login, devices and forecast endpoints; only password "good" is accepted."""
    dev = device()
    forecast = [{"date": "2026-11-10", "daily": {"timestamp": "2026-11-10T00:00:00+00:00"}}]

    async def login(request):
        body = await request.json()
        if body.get("password") != "good":
            return web.json_response({"code": "InvalidCredentials"}, status=401)
        return web.json_response({"token": "t", "refreshToken": "r"})

    async def devices(request):
        assert request.headers["Authorization"] == "Bearer t"
        return web.json_response([copy.deepcopy(dev)])

    async def forecast_handler(request):
        return web.json_response(forecast)

    app = web.Application()
    app.router.add_post("/api/v1/auth/login", login)
    app.router.add_get("/api/v1/me/devices", devices)
    app.router.add_get("/api/v1/me/devices/{id}/forecast", forecast_handler)
    return app


def user_input(host: str, password: str) -> dict:
    return {
        "host": host,
        "username": "user@example.com",
        "password": password,
        "filter_owned": True,
    }


async def start_flow(hass):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_successful_login_creates_loaded_entry(hass, serve, fake_app):
    base_url = await serve(fake_app)
    flow = await start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        flow["flow_id"], user_input(base_url, "good")
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert entry.state is config_entries.ConfigEntryState.LOADED
    assert hass.states.get("sensor.garden_temperature").state == "18.2"

    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_bad_password_shows_invalid_auth(hass, serve, fake_app):
    base_url = await serve(fake_app)
    flow = await start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        flow["flow_id"], user_input(base_url, "bad")
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}
    assert hass.config_entries.async_entries(DOMAIN) == []
