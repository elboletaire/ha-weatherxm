import logging
from homeassistant.components.weather import WeatherEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import generate_entity_id

from .const import DOMAIN
from .utils import async_setup_entities_list

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    entities = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMWeather(
        coordinator=hass.data[DOMAIN][entry.entry_id],
        entity_id=generate_entity_id("weather.{}", alias, hass=hass),
        device_id=device['id'],
        alias=alias,
        address=device['address'],
        current_weather=device['current_weather']
    ))
    async_add_entities(entities, True)

ICON_TO_CONDITION_MAP = {
    "blizzard": "snowy",
    "clear-day": "sunny",
    "clear-night": "clear-night",
    "clear": "sunny",
    "cloudy": "cloudy",
    "cold-day": "snowy",
    "cold-night": "clear-night",
    "cold": "snowy",
    "drizzle": "rainy",
    "dust-day": "fog",
    "dust-night": "fog",
    "dust": "fog",
    "flurries": "snowy",
    "fog": "fog",
    "freezing-drizzle": "snowy-rainy",
    "freezing-rain": "snowy-rainy",
    "hail": "hail",
    "hailstorm": "hail",
    "haze": "fog",
    "hot-day": "sunny",
    "hot-night": "clear-night",
    "hot": "sunny",
    "hurricane": "exceptional",
    "isolated-showers": "rainy",
    "isolated-thunderstorms": "lightning",
    "mist": "fog",
    "mostly-sunny": "sunny",
    "mostlycloudy": "cloudy",
    "overcast": "cloudy",
    "partly-cloudy-day": "partlycloudy",
    "partly-cloudy-night": "partlycloudy",
    "partlycloudy": "partlycloudy",
    "rain-and-sleet": "snowy-rainy",
    "rain-and-snow": "snowy-rainy",
    "rain-showers": "rainy",
    "rain": "rainy",
    "sand": "fog",
    "sandstorm-day": "fog",
    "sandstorm-night": "fog",
    "scattered-showers": "rainy",
    "scattered-thunderstorms": "lightning",
    "sleet": "snowy-rainy",
    "smoke": "fog",
    "snow-showers": "snowy",
    "snow-thunderstorm": "snowy-rainy",
    "snow": "snowy",
    "sunny": "sunny",
    "thunderstorm-with-hail": "hail",
    "thunderstorm-with-rain": "lightning-rainy",
    "thunderstorm-with-snow": "snowy-rainy",
    "thunderstorm": "lightning",
    "thunderstorms": "lightning",
    "tornado": "tornado",
    "volcanic-ash": "fog",
    "wind": "windy",
    "windy-variant": "windy-variant",
}

class WeatherXMWeather(CoordinatorEntity, WeatherEntity):
    def __init__(self, coordinator, entity_id, device_id, alias, address, current_weather):
        """Initialize."""
        super().__init__(coordinator)
        self.entity_id = entity_id
        self._device_id = device_id
        self._address = address
        self._alias = alias
        self._current_weather = current_weather
        self._attr_name = alias
        self._attr_unique_id = alias

    @property
    def apparent_temperature(self):
        return self._current_weather.get("feels_like")

    @property
    def condition(self):
        icon = self._current_weather.get("icon")
        if icon:
            return ICON_TO_CONDITION_MAP.get(icon, "unknown")
        return None

    @property
    def datetime(self):
        return self._current_weather.get("timestamp")

    @property
    def dew_point(self):
        return self._current_weather.get("dew_point")

    @property
    def humidity(self):
        return self._current_weather.get("humidity")

    @property
    def precipitation(self):
        return self._current_weather.get("precipitation")

    @property
    def precipitation_accumulated(self):
        return self._current_weather.get("precipitation_accumulated")

    @property
    def pressure(self):
        return self._current_weather.get("pressure")

    @property
    def temperature(self):
        return self._current_weather.get("temperature")

    @property
    def uv_index(self):
        return self._current_weather.get("uv_index")

    @property
    def wind_bearing(self):
        return self._current_weather.get("wind_direction")

    @property
    def wind_gust_speed(self):
        return self._current_weather.get("wind_gust")

    @property
    def wind_speed(self):
        return self._current_weather.get("wind_speed")

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    @property
    def attribution(self):
        return f"Data provided by WeatherXM (device {self._device_id})"

    @property
    def name(self):
        return f"{self._attr_name}, {self._address}"

    @property
    def unique_id(self):
        return self._alias

    @property
    def state_attributes(self):
        """Return the state attributes."""
        data = super().state_attributes
        data.update({
            "apparent_temperature": self.apparent_temperature,
            "condition": self.condition,
            "datetime": self.datetime,
            "dew_point": self.dew_point,
            "humidity": self.humidity,
            "precipitation": self.precipitation,
            "precipitation_accumulated": self.precipitation_accumulated,
            "pressure": self.pressure,
            "temperature": self.temperature,
            "uv_index": self.uv_index,
            "wind_bearing": self.wind_bearing,
            "wind_speed": self.wind_speed,
            "wind_gust_speed": self.wind_gust_speed,
        })
        return data
