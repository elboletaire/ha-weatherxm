from datetime import datetime
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from typing import Callable, Any
from .const import DOMAIN, CONF_FILTER_OWNED_DEVICES


def parse_timestamp(value: str | None) -> datetime | None:
    """Parse an API timestamp, assuming UTC when it has no offset."""
    if not value:
        return None
    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt_util.UTC)


async def async_setup_entities_list(
    hass: HomeAssistant,
    entry: ConfigEntry,
    entity_initializer: Callable[[str, dict[str, Any]], Any]
) -> list:
    """Set up entities list."""
    coordinator = hass.data[DOMAIN][entry.entry_id]['coordinator']
    filter_owned_devices = entry.options.get(CONF_FILTER_OWNED_DEVICES, True)

    devices = coordinator.data
    entities = []

    for device in devices:
        if filter_owned_devices and not device.get('relation') == 'owned':
            continue

        alias = (
            (device.get("attributes") or {}).get("friendlyName")
            or device.get("name")
            or device["id"]
        )
        entities.append(entity_initializer(alias, device))

    return entities
