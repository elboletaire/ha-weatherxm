"""Entity ids, values, units and icons for a full device, in metric and imperial."""

import pytest
from homeassistant.const import STATE_UNKNOWN
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM

SENSOR_ENTITY_IDS = [
    "sensor.garden_activity_status",
    "sensor.garden_last_station_activity",
    "sensor.garden_quality_score",
    "sensor.garden_network",
    "sensor.garden_relation",
    "sensor.garden_precipitation",
    "sensor.garden_daily_precipitation",
    "sensor.garden_temperature",
    "sensor.garden_feels_like",
    "sensor.garden_humidity",
    "sensor.garden_dew_point",
    "sensor.garden_wind_speed",
    "sensor.garden_wind_gust",
    "sensor.garden_wind_direction",
    "sensor.garden_pressure",
    "sensor.garden_uv_index",
    "sensor.garden_solar_irradiance",
    "sensor.garden_battery",
    "sensor.garden_firmware",
    "sensor.garden_rewards",
    "sensor.garden_total_rewards",
    "sensor.garden_last_update",
]


async def test_full_device_creates_every_sensor(hass, device, setup_integration):
    hass.config.units = METRIC_SYSTEM
    await setup_integration([device()])

    for entity_id in SENSOR_ENTITY_IDS:
        assert hass.states.get(entity_id) is not None, entity_id
    assert hass.states.get("binary_sensor.garden_online").state == "on"
    assert hass.states.get("weather.garden") is not None
    assert hass.states.get("geo_location.garden") is not None


async def test_metric_values_and_units(hass, device, setup_integration):
    hass.config.units = METRIC_SYSTEM
    await setup_integration([device()])

    assert float(hass.states.get("sensor.garden_temperature").state) == pytest.approx(18.2)
    wind = hass.states.get("sensor.garden_wind_speed")
    assert float(wind.state) == pytest.approx(7.56)
    assert wind.attributes["unit_of_measurement"] == "km/h"
    assert hass.states.get("sensor.garden_precipitation").attributes["unit_of_measurement"] == "mm/h"


async def test_imperial_values_and_units(hass, device, setup_integration):
    hass.config.units = US_CUSTOMARY_SYSTEM
    await setup_integration([device()])

    temperature = hass.states.get("sensor.garden_temperature")
    assert temperature.attributes["unit_of_measurement"] == "°F"
    assert float(temperature.state) == pytest.approx(64.76, abs=0.01)

    precipitation = hass.states.get("sensor.garden_precipitation")
    assert precipitation.attributes["unit_of_measurement"] == "in/h"
    assert float(precipitation.state) == pytest.approx(0.2 / 25.4, abs=1e-4)


async def test_wind_direction_is_measurement_angle(hass, device, setup_integration):
    await setup_integration([device()])

    state = hass.states.get("sensor.garden_wind_direction")
    assert state.state == "180"
    assert state.attributes["state_class"] == "measurement_angle"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param("2026-11-10T10:00:00+00:00", "2026-11-10T10:00:00+00:00", id="aware"),
        pytest.param("2026-11-10T10:00:00", "2026-11-10T10:00:00+00:00", id="naive-is-utc"),
    ],
)
async def test_last_update_timestamp(hass, device, setup_integration, raw, expected):
    dev = device()
    dev["current_weather"]["timestamp"] = raw
    await setup_integration([dev])

    assert hass.states.get("sensor.garden_last_update").state == expected


async def test_last_station_activity_naive_timestamp_is_utc(hass, device, setup_integration):
    dev = device()
    dev["attributes"]["lastWeatherStationActivity"] = "2026-11-10T09:30:00"
    await setup_integration([dev])

    state = hass.states.get("sensor.garden_last_station_activity")
    assert state.state == "2026-11-10T09:30:00+00:00"
    assert state.attributes["last_active_at"] == "2026-11-10T10:00:00+00:00"


@pytest.mark.parametrize(
    ("bat_state", "is_active", "expected"),
    [
        pytest.param("ok", True, "100.0", id="ok"),
        pytest.param("low", True, "3.0", id="low"),
        pytest.param("ok", False, STATE_UNKNOWN, id="inactive"),
        pytest.param(None, True, STATE_UNKNOWN, id="missing-state"),
    ],
)
async def test_battery_level(hass, device, setup_integration, bat_state, is_active, expected):
    dev = device(bat_state=bat_state)
    dev["attributes"]["isActive"] = is_active
    await setup_integration([dev])

    assert hass.states.get("sensor.garden_battery").state == expected


async def test_quality_score_null_is_unknown(hass, device, setup_integration):
    dev = device(metrics={"qod_score": None, "pol_reason": None, "ts": None})
    await setup_integration([dev])

    state = hass.states.get("sensor.garden_quality_score")
    assert state.state == STATE_UNKNOWN
    assert state.attributes["icon"] == "mdi:help-circle"


async def test_activity_status_is_enum(hass, device, setup_integration):
    await setup_integration([device()])

    state = hass.states.get("sensor.garden_activity_status")
    assert state.state == "active"
    assert state.attributes["options"] == ["active", "inactive"]


async def test_inactive_station_is_offline(hass, device, setup_integration):
    dev = device()
    dev["attributes"]["isActive"] = False
    await setup_integration([dev])

    assert hass.states.get("binary_sensor.garden_online").state == "off"
    assert hass.states.get("sensor.garden_activity_status").state == "inactive"


async def test_helium_network_icon(hass, device, setup_integration):
    await setup_integration([device()])

    state = hass.states.get("sensor.garden_network")
    assert state.state == "helium"
    assert state.attributes["icon"] == "mdi:access-point-network"
    assert state.attributes["weather_station_model"] == "WS2000"


async def test_rewards_and_firmware_attributes(hass, device, setup_integration):
    await setup_integration([device()])

    assert hass.states.get("sensor.garden_rewards").state == "1.5"
    assert hass.states.get("sensor.garden_rewards").attributes["total_rewards"] == 100.2
    assert hass.states.get("sensor.garden_total_rewards").state == "100.2"
    firmware = hass.states.get("sensor.garden_firmware")
    assert firmware.state == "1.0"
    assert firmware.attributes["assigned_version"] == "1.1"

