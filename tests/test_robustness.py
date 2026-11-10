"""The integration must load, and log no errors, when API fields are missing or null."""

import logging

import pytest
from homeassistant.config_entries import ConfigEntryState

NULLABLE_KEYS = [
    "attributes",
    "current_weather",
    "rewards",
    "bat_state",
    "location",
    "bundle",
    "metrics",
    "address",
    "name",
]


def error_records(caplog) -> list[str]:
    return [
        f"{r.name}: {r.getMessage()}"
        for r in caplog.records
        if r.levelno >= logging.ERROR
    ]


@pytest.mark.parametrize("key", NULLABLE_KEYS)
@pytest.mark.parametrize("mode", ["missing", "null"])
async def test_entry_loads_without_errors(hass, device, setup_integration, caplog, key, mode):
    dev = device()
    if mode == "missing":
        dev.pop(key)
    else:
        dev[key] = None

    entry = await setup_integration([dev])

    assert entry.state is ConfigEntryState.LOADED
    assert error_records(caplog) == []


async def test_bare_device_next_to_full_device(hass, device, setup_integration, caplog):
    bare = {"id": "bare", "relation": "owned"}

    entry = await setup_integration([device(), bare])

    assert entry.state is ConfigEntryState.LOADED
    assert error_records(caplog) == []
    assert hass.states.get("sensor.garden_battery").state == "100.0"
    assert hass.states.get("sensor.bare_battery").state == "unknown"
    assert hass.states.get("sensor.bare_network").state == "unknown"
    assert hass.states.get("binary_sensor.bare_online").state == "off"
