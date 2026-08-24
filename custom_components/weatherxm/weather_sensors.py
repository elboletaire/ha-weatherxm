"""Generic sensors exposing single WeatherXM current_weather values."""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import SensorEntity, SensorStateClass

from .const import DOMAIN

class WeatherXMWeatherValueSensor(CoordinatorEntity, SensorEntity):
    """Sensor exposing a single value from a device's current_weather data."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator,
        device_id,
        alias,
        data_key,
        name_suffix,
        device_class=None,
        native_unit_of_measurement=None,
        icon=None,
    ):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._data_key = data_key
        self._attr_name = f"{alias} {name_suffix}"
        self._attr_unique_id = f"{alias}_{data_key}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_icon = icon

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
        """Return the current value for this sensor's data key."""
        device = self._get_device_data()
        if device:
            return device.get('current_weather', {}).get(self._data_key)
        return None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )
