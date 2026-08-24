from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfIrradiance,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .utils import async_setup_entities_list
from .battery import WeatherXMBatteryLevelSensor
from .rewards import WeatherXMRewardsSensor, WeatherXMTotalRewardsSensor
from .firmware import WeatherXMFirmwareSensor
from .last_update import WeatherXMLastUpdateSensor
from .precipitation import WeatherXMPrecipitationSensor, WeatherXMDailyPrecipitationSensor
from .weather_sensors import WeatherXMWeatherValueSensor

# (data_key, name suffix, device_class, unit, icon)
WEATHER_VALUE_SENSORS = [
    ("temperature", "Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None),
    ("feels_like", "Feels Like", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None),
    ("humidity", "Humidity", SensorDeviceClass.HUMIDITY, PERCENTAGE, None),
    ("dew_point", "Dew Point", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None),
    ("wind_speed", "Wind Speed", SensorDeviceClass.WIND_SPEED, UnitOfSpeed.METERS_PER_SECOND, None),
    ("wind_gust", "Wind Gust", SensorDeviceClass.WIND_SPEED, UnitOfSpeed.METERS_PER_SECOND, None),
    ("wind_direction", "Wind Bearing", SensorDeviceClass.WIND_DIRECTION, DEGREE, None),
    ("pressure", "Pressure", SensorDeviceClass.PRESSURE, UnitOfPressure.HPA, None),
    ("uv_index", "UV Index", None, None, "mdi:weather-sunny-alert"),
    ("solar_irradiance", "Solar Irradiance", SensorDeviceClass.IRRADIANCE, UnitOfIrradiance.WATTS_PER_SQUARE_METER, None),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]['coordinator']

    # Battery indicators
    batteries = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMBatteryLevelSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias,
        bat_state=device['bat_state'],
        is_active=device['attributes'].get('isActive', False)
    ))
    async_add_entities(batteries, True)

    # Rewards sensors
    rewards = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMRewardsSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias,
        actual_reward=device['rewards']['actual_reward'],
        total_rewards=device['rewards']['total_rewards']
    ))
    async_add_entities(rewards, True)

    # Total rewards sensors
    trewards = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMTotalRewardsSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias,
        total_rewards=device['rewards']['total_rewards']
    ))
    async_add_entities(trewards, True)

    # Firmware sensors
    firmware = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMFirmwareSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias,
        firmware=device['attributes']['firmware']
    ))
    async_add_entities(firmware, True)

    # Last update sensors
    last_update = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMLastUpdateSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias
    ))
    async_add_entities(last_update, True)

    # Precipitation sensors
    precipitation = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMPrecipitationSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias
    ))
    async_add_entities(precipitation, True)

    # Daily precipitation sensors
    daily_precipitation = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMDailyPrecipitationSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias
    ))
    async_add_entities(daily_precipitation, True)

    # Current weather value sensors (temperature, humidity, wind, pressure, uv, solar, ...)
    for data_key, name_suffix, device_class, unit, icon in WEATHER_VALUE_SENSORS:
        values = await async_setup_entities_list(
            hass, entry, lambda alias, device, data_key=data_key, name_suffix=name_suffix, device_class=device_class, unit=unit, icon=icon: WeatherXMWeatherValueSensor(
                coordinator=coordinator,
                device_id=device['id'],
                alias=alias,
                data_key=data_key,
                name_suffix=name_suffix,
                device_class=device_class,
                native_unit_of_measurement=unit,
                icon=icon,
            )
        )
        async_add_entities(values, True)
