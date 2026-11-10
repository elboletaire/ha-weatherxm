from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
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
from .last_station_activity import WeatherXMLastStationActivitySensor
from .activity_status import WeatherXMActivityStatusSensor
from .quality import WeatherXMQualitySensor
from .network import WeatherXMNetworkSensor
from .relation import WeatherXMRelationSensor
from .precipitation import WeatherXMPrecipitationSensor, WeatherXMDailyPrecipitationSensor
from .weather_sensors import WeatherXMWeatherValueSensor

# (data_key, name suffix, device_class, unit, icon, state_class)
WEATHER_VALUE_SENSORS = [
    ("temperature", "Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None, SensorStateClass.MEASUREMENT),
    ("feels_like", "Feels Like", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None, SensorStateClass.MEASUREMENT),
    ("humidity", "Humidity", SensorDeviceClass.HUMIDITY, PERCENTAGE, None, SensorStateClass.MEASUREMENT),
    ("dew_point", "Dew Point", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None, SensorStateClass.MEASUREMENT),
    ("wind_speed", "Wind Speed", SensorDeviceClass.WIND_SPEED, UnitOfSpeed.METERS_PER_SECOND, None, SensorStateClass.MEASUREMENT),
    ("wind_gust", "Wind Gust", SensorDeviceClass.WIND_SPEED, UnitOfSpeed.METERS_PER_SECOND, None, SensorStateClass.MEASUREMENT),
    ("wind_direction", "Wind Direction", SensorDeviceClass.WIND_DIRECTION, DEGREE, None, SensorStateClass.MEASUREMENT_ANGLE),
    ("pressure", "Pressure", SensorDeviceClass.PRESSURE, UnitOfPressure.HPA, None, SensorStateClass.MEASUREMENT),
    ("uv_index", "UV Index", None, None, "mdi:weather-sunny-alert", SensorStateClass.MEASUREMENT),
    ("solar_irradiance", "Solar Irradiance", SensorDeviceClass.IRRADIANCE, UnitOfIrradiance.WATTS_PER_SQUARE_METER, None, SensorStateClass.MEASUREMENT),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Battery indicators
    batteries = await async_setup_entities_list(
        hass,
        entry,
        lambda alias, device: WeatherXMBatteryLevelSensor(
            coordinator=coordinator,
            device_id=device["id"],
            alias=alias,
            bat_state=device["bat_state"],
            is_active=device["attributes"].get("isActive", False),
        ),
    )
    async_add_entities(batteries, True)

    # Rewards sensors
    rewards = await async_setup_entities_list(
        hass,
        entry,
        lambda alias, device: WeatherXMRewardsSensor(
            coordinator=coordinator,
            device_id=device["id"],
            alias=alias,
            actual_reward=device["rewards"]["actual_reward"],
            total_rewards=device["rewards"]["total_rewards"],
        ),
    )
    async_add_entities(rewards, True)

    # Total rewards sensors
    trewards = await async_setup_entities_list(
        hass,
        entry,
        lambda alias, device: WeatherXMTotalRewardsSensor(
            coordinator=coordinator,
            device_id=device["id"],
            alias=alias,
            total_rewards=device["rewards"]["total_rewards"],
        ),
    )
    async_add_entities(trewards, True)

    # Firmware sensors
    firmware = await async_setup_entities_list(
        hass,
        entry,
        lambda alias, device: WeatherXMFirmwareSensor(
            coordinator=coordinator,
            device_id=device["id"],
            alias=alias,
            firmware=device["attributes"]["firmware"],
        ),
    )
    async_add_entities(firmware, True)

    # Last update sensors
    last_update = await async_setup_entities_list(
        hass,
        entry,
        lambda alias, device: WeatherXMLastUpdateSensor(
            coordinator=coordinator, device_id=device["id"], alias=alias
        ),
    )
    async_add_entities(last_update, True)

    # Last station activity sensors
    last_station_activity = await async_setup_entities_list(
        hass,
        entry,
        lambda alias, device: WeatherXMLastStationActivitySensor(
            coordinator=coordinator, device_id=device["id"], alias=alias
        ),
    )
    async_add_entities(last_station_activity, True)

    # Activity status sensors
    activity_status = await async_setup_entities_list(
        hass,
        entry,
        lambda alias, device: WeatherXMActivityStatusSensor(
            coordinator=coordinator, device_id=device["id"], alias=alias
        ),
    )
    async_add_entities(activity_status, True)

    # Quality sensors
    quality = await async_setup_entities_list(
        hass,
        entry,
        lambda alias, device: WeatherXMQualitySensor(
            coordinator=coordinator, device_id=device["id"], alias=alias
        ),
    )
    async_add_entities(quality, True)

    # Network sensors
    network = await async_setup_entities_list(
        hass,
        entry,
        lambda alias, device: WeatherXMNetworkSensor(
            coordinator=coordinator, device_id=device["id"], alias=alias
        ),
    )
    async_add_entities(network, True)

    # Relation sensors
    relation = await async_setup_entities_list(
        hass,
        entry,
        lambda alias, device: WeatherXMRelationSensor(
            coordinator=coordinator, device_id=device["id"], alias=alias
        ),
    )
    async_add_entities(relation, True)

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
    for data_key, name_suffix, device_class, unit, icon, state_class in WEATHER_VALUE_SENSORS:
        values = await async_setup_entities_list(
            hass, entry, lambda alias, device, data_key=data_key, name_suffix=name_suffix, device_class=device_class, unit=unit, icon=icon, state_class=state_class: WeatherXMWeatherValueSensor(
                coordinator=coordinator,
                device_id=device['id'],
                alias=alias,
                data_key=data_key,
                name_suffix=name_suffix,
                device_class=device_class,
                native_unit_of_measurement=unit,
                icon=icon,
                state_class=state_class,
            )
        )
        async_add_entities(values, True)
