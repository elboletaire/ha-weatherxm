from homeassistant.components.weather import (
    WeatherEntity,
    WeatherEntityFeature,
    Forecast,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.const import (
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from .const import DOMAIN
from .utils import async_setup_entities_list

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    entities = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMWeather(
        coordinator=hass.data[DOMAIN][entry.entry_id],
        entity_id=generate_entity_id("weather.{}", alias, hass=hass),
        device_id=device['id'],
        alias=alias,
        address=device['address'],
        current_weather=device['current_weather'],
        forecast=device.get('forecast', [])
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
    """ WeatherXM Weather Entity """

    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, entity_id, device_id, alias, address, current_weather, forecast):
        """Initialize."""
        super().__init__(coordinator)
        self.entity_id = entity_id
        self._device_id = device_id
        self._address = address
        self._alias = alias
        self._current_weather = current_weather
        self._forecast = forecast
        self._attr_name = alias
        self._attr_unique_id = alias

    @property
    def native_apparent_temperature(self):
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
    def native_dew_point(self):
        return self._current_weather.get("dew_point")

    @property
    def humidity(self):
        return self._current_weather.get("humidity")

    @property
    def native_precipitation(self):
        return self._current_weather.get("precipitation")

    @property
    def native_precipitation_accumulated(self):
        return self._current_weather.get("precipitation_accumulated")

    @property
    def native_pressure(self):
        return self._current_weather.get("pressure")

    @property
    def solar_irradiance(self):
        return self._current_weather.get("solar_irradiance")

    @property
    def native_temperature(self):
        return self._current_weather.get("temperature")

    @property
    def uv_index(self):
        return self._current_weather.get("uv_index")

    @property
    def wind_bearing(self):
        return self._current_weather.get("wind_direction")

    @property
    def native_wind_gust_speed(self):
        return self._current_weather.get("wind_gust")

    @property
    def native_wind_speed(self):
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
            "native_apparent_temperature": self.native_apparent_temperature,
            "condition": self.condition,
            "datetime": self.datetime,
            "native_dew_point": self.native_dew_point,
            "humidity": self.humidity,
            "native_precipitation": self.native_precipitation,
            "native_precipitation_accumulated": self.native_precipitation_accumulated,
            "native_pressure": self.native_pressure,
            "solar_irradiance": self.solar_irradiance,
            "native_temperature": self.native_temperature,
            "uv_index": self.uv_index,
            "wind_bearing": self.wind_bearing,
            "native_wind_speed": self.native_wind_speed,
            "native_wind_gust_speed": self.native_wind_gust_speed,
        })
        return data

    @property
    def forecast(self):
        return {
            "hourly": self.forecast_hourly[:24],  # Limit to 24 hourly forecasts
            "daily": self.forecast_daily[:7],  # Limit to 7 daily forecasts
        }

    @property
    def forecast_hourly(self):
        forecasts = []
        for daily in self._forecast:
            for hourly in daily.get("hourly", []):
                hourly_forecast = {
                    "datetime": hourly.get("timestamp"),
                    "native_temperature": hourly.get("temperature"),
                    "native_precipitation": hourly.get("precipitation"),
                    "precipitation_probability": hourly.get("precipitation_probability"),
                    "native_wind_speed": hourly.get("wind_speed"),
                    "wind_bearing": hourly.get("wind_direction"),
                    "condition": ICON_TO_CONDITION_MAP.get(hourly.get("icon"), "unknown"),
                }
                forecasts.append(hourly_forecast)
        return forecasts

    @property
    def forecast_daily(self):
        forecasts = []
        for daily in self._forecast:
            day_data = daily.get("daily", {})
            daily_forecast = {
                "datetime": day_data.get("timestamp"),
                "native_temperature": day_data.get("temperature_max"),
                "native_templow": day_data.get("temperature_min"),
                "native_precipitation": day_data.get("precipitation_intensity"),
                "precipitation_probability": day_data.get("precipitation_probability"),
                "native_wind_speed": day_data.get("wind_speed"),
                "wind_bearing": day_data.get("wind_direction"),
                "condition": ICON_TO_CONDITION_MAP.get(day_data.get("icon"), "unknown"),
            }
            forecasts.append(daily_forecast)
        return forecasts

    @property
    def state(self):
        return self.condition

    async def async_forecast_daily(self):
        return self.forecast_daily[:7]

    async def async_forecast_hourly(self):
        return self.forecast_hourly[:24]
