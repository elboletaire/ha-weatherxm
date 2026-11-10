"""WeatherXMAPI token refresh and error handling against a local fake server."""

import logging

import pytest
from aiohttp import web

from custom_components.weatherxm.weatherxm_api import WeatherXMAPI, WeatherXMError


def build_app(device: dict, retry_devices_status: int) -> web.Application:
    """The first devices call with token "t1" is rejected with 401, the retry uses token "t2"."""

    async def login(request):
        body = await request.json()
        if body.get("password") != "secret":
            return web.json_response({"code": "InvalidCredentials"}, status=401)
        return web.json_response({"token": "t1", "refreshToken": "r1"})

    async def refresh(request):
        body = await request.json()
        if body.get("refreshToken") != "r1":
            return web.json_response({}, status=401)
        return web.json_response({"token": "t2", "refreshToken": "r2"})

    async def devices(request):
        token = request.headers["Authorization"].removeprefix("Bearer ")
        if token == "t1":
            return web.json_response({}, status=401)
        if retry_devices_status != 200:
            return web.Response(status=retry_devices_status, text="boom")
        return web.json_response([device])

    app = web.Application()
    app.router.add_post("/api/v1/auth/login", login)
    app.router.add_post("/api/v1/auth/refresh", refresh)
    app.router.add_get("/api/v1/me/devices", devices)
    return app


async def test_get_devices_refreshes_token_after_401(serve, device):
    dev = device()
    api = WeatherXMAPI(await serve(build_app(dev, retry_devices_status=200)))
    try:
        assert await api.authenticate("user@example.com", "secret")
        assert await api.get_devices() == [dev]
        assert api._auth_token == "t2"
        assert api._refresh_token == "r2"
    finally:
        await api.close()


async def test_failed_retry_raises(serve, device, caplog):
    api = WeatherXMAPI(await serve(build_app(device(), retry_devices_status=500)))
    try:
        assert await api.authenticate("user@example.com", "secret")
        with caplog.at_level(logging.ERROR), pytest.raises(WeatherXMError):
            await api.get_devices()
    finally:
        await api.close()

    assert any("status 500" in r.getMessage() for r in caplog.records)


async def test_rejected_refresh_raises(serve, device):
    app = build_app(device(), retry_devices_status=200)
    api = WeatherXMAPI(await serve(app))
    try:
        assert await api.authenticate("user@example.com", "secret")
        api._refresh_token = "stale"
        with pytest.raises(WeatherXMError):
            await api.get_devices()
        assert api._auth_token is None
    finally:
        await api.close()


async def test_rejected_credentials_return_false(serve, device):
    api = WeatherXMAPI(await serve(build_app(device(), retry_devices_status=200)))
    try:
        assert not await api.authenticate("user@example.com", "wrong")
    finally:
        await api.close()


async def test_connection_error_raises_on_authenticate(socket_enabled, unused_tcp_port):
    api = WeatherXMAPI(f"http://127.0.0.1:{unused_tcp_port}")
    try:
        with pytest.raises(WeatherXMError):
            await api.authenticate("user@example.com", "secret")
    finally:
        await api.close()


async def test_login_without_tokens_raises(socket_enabled, serve):
    app = web.Application()

    async def login(request):
        return web.json_response({"message": "ok"})

    app.router.add_post("/api/v1/auth/login", login)
    api = WeatherXMAPI(await serve(app))
    try:
        with pytest.raises(WeatherXMError):
            await api.authenticate("user@example.com", "secret")
    finally:
        await api.close()
