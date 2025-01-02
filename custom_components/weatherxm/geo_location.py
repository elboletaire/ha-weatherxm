import logging
from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import generate_entity_id, DeviceInfo

from .const import DOMAIN
from .utils import async_setup_entities_list

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    entities = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMGeolocation(
        coordinator=hass.data[DOMAIN][entry.entry_id]['coordinator'],
        entity_id=generate_entity_id("geo_location.{}", alias, hass=hass),
        device_id=device['id'],
        alias=alias,
        location=device['location'],
        last_activity=device['attributes'].get('lastWeatherStationActivity'),
        current_weather=device['current_weather']
    ))
    async_add_entities(entities, True)

class WeatherXMGeolocation(CoordinatorEntity, GeolocationEvent):
    def __init__(self, coordinator, entity_id, device_id, alias, location, last_activity, current_weather):
        super().__init__(coordinator)
        self.entity_id = entity_id
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Location"
        self._attr_unique_id = f"{alias}_location"

    def _get_device_data(self):
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return None
        for device in self.coordinator.data:
            if device['id'] == self._device_id:
                return device
        return None

    @property
    def _location(self):
        """Get location from coordinator data."""
        device = self._get_device_data()
        return device['location'] if device else {}

    @property
    def _last_activity(self):
        """Get last activity from coordinator data."""
        device = self._get_device_data()
        return device['attributes'].get('lastWeatherStationActivity') if device else None

    @property
    def _current_weather(self):
        """Get current weather from coordinator data."""
        device = self._get_device_data()
        return device['current_weather'] if device else {}

    @property
    def latitude(self):
        return self._location.get("lat")

    @property
    def longitude(self):
        return self._location.get("lon")

    @property
    def source(self):
        return DOMAIN

    @property
    def state(self):
        """Return the state of the sensor."""
        # Use the timestamp of the last weather station activity as the state
        return self._last_activity

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        data = {
            "source": self.source,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }
        if self._current_weather:
            data.update(self._current_weather)
        return data

    @property
    def icon(self):
        return "mdi:map-marker"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )
