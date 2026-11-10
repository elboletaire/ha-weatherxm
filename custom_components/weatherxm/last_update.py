from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)

from .const import DOMAIN
from .utils import parse_timestamp


class WeatherXMLastUpdateSensor(CoordinatorEntity, SensorEntity):
    """WeatherXM Last Update Sensor."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, device_id, alias):
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Last Update"
        self._attr_unique_id = f"{alias}_last_update"

    def _get_device_data(self):
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return None
        for device in self.coordinator.data:
            if device["id"] == self._device_id:
                return device
        return None

    @property
    def native_value(self):
        """Return the timestamp of the last weather observation."""
        device = self._get_device_data()
        if device:
            timestamp = (device.get("current_weather") or {}).get("timestamp")
            return parse_timestamp(timestamp)
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
