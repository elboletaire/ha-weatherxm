"""Weather entity: condition mapping, unknown icons and forecast shapes."""

import logging

import pytest
from homeassistant.const import STATE_UNKNOWN

import custom_components.weatherxm.weather as weather_module


@pytest.fixture(autouse=True)
def reset_unknown_icon_cache():
    """The unknown-icon warning is deduplicated module-wide, so reset it for each test."""
    weather_module._UNKNOWN_ICONS.clear()
    yield
    weather_module._UNKNOWN_ICONS.clear()


async def get_forecasts(hass, entity_id: str, kind: str) -> list[dict]:
    response = await hass.services.async_call(
        "weather",
        "get_forecasts",
        {"entity_id": entity_id, "type": kind},
        blocking=True,
        return_response=True,
    )
    return response[entity_id]["forecast"]


async def test_current_condition_maps_overcast_night_to_cloudy(hass, device, setup_integration):
    await setup_integration([device()])

    assert hass.states.get("weather.garden").state == "cloudy"


async def test_unknown_icon_is_unknown_and_warned_once(hass, device, setup_integration, caplog):
    dev = device()
    dev["current_weather"]["icon"] = "brand-new-icon"
    forecast = [
        {
            "date": "2026-11-10",
            "daily": {"timestamp": "2026-11-10T00:00:00+00:00", "icon": "brand-new-icon"},
            "hourly": [{"timestamp": "2026-11-10T11:00:00+00:00", "icon": "brand-new-icon"}],
        }
    ]
    with caplog.at_level(logging.WARNING):
        await setup_integration([dev], forecast=forecast)
        await get_forecasts(hass, "weather.garden", "daily")
        await get_forecasts(hass, "weather.garden", "hourly")

    assert hass.states.get("weather.garden").state == STATE_UNKNOWN
    warnings = [r for r in caplog.records if "brand-new-icon" in r.getMessage()]
    assert len(warnings) == 1
    assert warnings[0].levelno == logging.WARNING


async def test_valid_forecasts_are_returned(hass, device, setup_integration):
    await setup_integration([device()])

    daily = await get_forecasts(hass, "weather.garden", "daily")
    hourly = await get_forecasts(hass, "weather.garden", "hourly")

    assert len(daily) == 1
    assert daily[0]["datetime"] == "2026-11-10T00:00:00+00:00"
    assert daily[0]["condition"] == "cloudy"
    assert daily[0]["temperature"] == 20
    assert daily[0]["templow"] == 10
    assert len(hourly) == 1
    assert hourly[0]["datetime"] == "2026-11-10T11:00:00+00:00"
    assert hourly[0]["condition"] == "rainy"


@pytest.mark.parametrize(
    "forecast",
    [
        pytest.param({}, id="empty-dict"),
        pytest.param([], id="empty-list"),
        pytest.param([None], id="none-item"),
        pytest.param([{"daily": None}], id="daily-null"),
        pytest.param({"code": "x"}, id="error-payload"),
    ],
)
async def test_malformed_forecast_yields_no_entries(hass, device, setup_integration, forecast):
    await setup_integration([device()], forecast=forecast)

    assert await get_forecasts(hass, "weather.garden", "daily") == []
    assert await get_forecasts(hass, "weather.garden", "hourly") == []
