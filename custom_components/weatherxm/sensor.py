import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import (
    PERCENTAGE,
    UV_INDEX,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)

from .const import DOMAIN

SENSOR_TYPES = {
    "timestamp": ["Timestamp", None, "mdi:clock"],
    "temperature": ["Temperature", UnitOfTemperature.CELSIUS, "mdi:thermometer"],
    "humidity": ["Humidity", PERCENTAGE, "mdi:water-percent"],
    "wind_speed": ["Wind Speed", UnitOfSpeed.METERS_PER_SECOND, "mdi:weather-windy"],
    "wind_gust": ["Wind Gust", UnitOfSpeed.METERS_PER_SECOND, "mdi:weather-windy"],
    "wind_direction": ["Wind Direction", "°", "mdi:compass"],
    "solar_irradiance": ["Solar Irradiance", "W/m²", "mdi:weather-sunny"],
    "uv_index": ["UV Index", UV_INDEX, "mdi:weather-sunny-alert"],
    "precipitation": ["Precipitation", UnitOfLength.MILLIMETERS, "mdi:weather-rainy"],
    "pressure": ["Pressure", UnitOfPressure.HPA, "mdi:gauge"],
    "dew_point": ["Dew Point", UnitOfTemperature.CELSIUS, "mdi:thermometer"],
    "precipitation_accumulated": ["Precipitation Accumulated", UnitOfLength.MILLIMETERS, "mdi:weather-rainy"],
    "feels_like": ["Feels Like", UnitOfTemperature.CELSIUS, "mdi:thermometer"],
    "icon": ["Icon", None, None],  # Special handling for icon
}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    devices = coordinator.data
    sensors = []
    for device in devices:
        alias = device['attributes'].get('friendlyName', device['name'])
        for sensor_type, value in device['current_weather'].items():
            if sensor_type in SENSOR_TYPES and sensor_type != "icon":
                sensor_name, unit, icon = SENSOR_TYPES.get(sensor_type, [sensor_type, None, "mdi:alert-circle"])
                sensors.append(WeatherXMSensor(coordinator, device['id'], alias, sensor_type, sensor_name, value, unit, icon))

    async_add_entities(sensors, True)

class WeatherXMSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_id, alias, sensor_type, sensor_name, value, unit, icon):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._sensor_type = sensor_type
        self._sensor_name = sensor_name
        self._value = value
        self._unit = unit
        self._icon = icon
        self._attr_name = f"{alias} {sensor_name}"
        self._attr_unique_id = f"{device_id}_{sensor_type}"

    @property
    def state(self):
        device = next((d for d in self.coordinator.data if d['id'] == self._device_id), None)
        if device:
            self._value = device['current_weather'][self._sensor_type]
        return self._value

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def icon(self):
        if self._sensor_type == "icon":
            return f"mdi:weather-{self._value.replace('_', '-')}"
        return self._icon
