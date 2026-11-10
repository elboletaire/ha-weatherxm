from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfPrecipitationDepth, UnitOfVolumetricFlux

from .const import DOMAIN

class WeatherXMPrecipitationSensor(CoordinatorEntity, SensorEntity):
    """WeatherXM current precipitation rate sensor."""

    _attr_device_class = SensorDeviceClass.PRECIPITATION_INTENSITY
    _attr_native_unit_of_measurement = UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, device_id, alias):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Precipitation"
        self._attr_unique_id = f"{alias}_precipitation"

    def _get_device_data(self):
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return None
        for device in self.coordinator.data:
            if device['id'] == self._device_id:
                return device
        return None

    @property
    def state(self):
        """Return the current precipitation rate."""
        device = self._get_device_data()
        if device:
            return device.get('current_weather', {}).get('precipitation')
        return None

    @property
    def icon(self):
        return "mdi:weather-rainy"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )

class WeatherXMDailyPrecipitationSensor(CoordinatorEntity, SensorEntity):
    """WeatherXM daily accumulated precipitation sensor."""

    _attr_device_class = SensorDeviceClass.PRECIPITATION
    _attr_native_unit_of_measurement = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, device_id, alias):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Daily Precipitation"
        self._attr_unique_id = f"{alias}_daily_precipitation"

    def _get_device_data(self):
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return None
        for device in self.coordinator.data:
            if device['id'] == self._device_id:
                return device
        return None

    @property
    def state(self):
        """Return the accumulated precipitation for today."""
        device = self._get_device_data()
        if device:
            return device.get('current_weather', {}).get('precipitation_accumulated')
        return None

    @property
    def icon(self):
        return "mdi:weather-pouring"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )
