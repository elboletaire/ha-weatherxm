import logging
from homeassistant.components.weather import WeatherEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    devices = coordinator.data

    weather_entities = []
    for device in devices:
        alias = device['attributes'].get('friendlyName', device['name'])
        weather_entities.append(WeatherXMWeather(coordinator, device['id'], alias, device['current_weather']))

    async_add_entities(weather_entities, True)

class WeatherXMWeather(CoordinatorEntity, WeatherEntity):
    def __init__(self, coordinator, device_id, alias, current_weather):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._current_weather = current_weather
        self._attr_name = f"{alias} Weather"
        self._attr_unique_id = f"{alias}_weather"

    @property
    def temperature(self):
        return self._current_weather.get("temperature")

    @property
    def humidity(self):
        return self._current_weather.get("humidity")

    @property
    def wind_speed(self):
        return self._current_weather.get("wind_speed")

    @property
    def wind_bearing(self):
        return self._current_weather.get("wind_direction")

    @property
    def pressure(self):
        return self._current_weather.get("pressure")

    @property
    def condition(self):
        icon = self._current_weather.get("icon")
        if icon:
            return icon.replace("_", "-")
        return None

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    @property
    def attribution(self):
        return "Data provided by WeatherXM"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state_attributes(self):
        """Return the state attributes."""
        data = super().state_attributes
        data.update({
            "temperature": self.temperature,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "wind_bearing": self.wind_bearing,
            "pressure": self.pressure,
            "condition": self.condition,
        })
        return data
