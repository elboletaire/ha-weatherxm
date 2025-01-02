"""The WeatherXM integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .weatherxm_api import WeatherXMAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.WEATHER, Platform.GEO_LOCATION]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WeatherXM from a config entry."""

    username = entry.data["username"]
    password = entry.data["password"]
    host = entry.data["host"]

    api = WeatherXMAPI(host)
    if not await api.authenticate(username, password):
        return False

    async def async_update_data():
        """Fetch data from API endpoint."""
        try:
            _LOGGER.debug("Starting WeatherXM data update")
            devices = await api.get_devices()
            for device in devices:
                _LOGGER.debug("Fetching forecast for device %s", device['id'])
                device['forecast'] = await api.get_forecast_data(device['id'])
                _LOGGER.debug(
                    "Device %s data - Temperature: %s, Humidity: %s, Wind: %s",
                    device['id'],
                    device['current_weather'].get('temperature'),
                    device['current_weather'].get('humidity'),
                    device['current_weather'].get('wind_speed')
                )
            _LOGGER.debug("WeatherXM data update completed successfully")
            return devices
        except Exception as err:
            _LOGGER.error("Error updating WeatherXM data: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="weatherxm",
        update_method=async_update_data,
        update_interval=timedelta(minutes=5),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        'coordinator': coordinator,
        'api': api
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        api = hass.data[DOMAIN][entry.entry_id]['api']
        await api.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
