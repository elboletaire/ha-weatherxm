import logging
from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import generate_entity_id

from .const import DOMAIN
from .utils import async_setup_entities_list

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    entities = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMGeolocation(
        coordinator=hass.data[DOMAIN][entry.entry_id],
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
        self._location = location
        self._last_activity = last_activity
        self._current_weather = current_weather
        self._attr_name = f"{alias} Location"
        self._attr_unique_id = f"{alias}_location"

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
