from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from typing import Callable, Any
from .const import DOMAIN, CONF_FILTER_OWNED_DEVICES

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

        alias = device['attributes'].get('friendlyName', device['name'])
        entities.append(entity_initializer(alias, device))

    return entities
