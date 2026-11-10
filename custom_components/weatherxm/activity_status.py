from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorEntity,
)

from .const import DOMAIN


class WeatherXMActivityStatusSensor(CoordinatorEntity, SensorEntity):
    """WeatherXM Activity Status Sensor."""

    def __init__(self, coordinator, device_id, alias):
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Activity Status"
        self._attr_unique_id = f"{alias}_activity_status"

    def _get_device_data(self):
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return None
        for device in self.coordinator.data:
            if device["id"] == self._device_id:
                return device
        return None

    @property
    def state(self):
        """Return the state of the sensor."""
        device = self._get_device_data()
        if not device:
            return None
        return "active" if device["attributes"].get("isActive", False) else "inactive"

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        device = self._get_device_data()
        if not device:
            return "mdi:help-circle"
        if device["attributes"].get("isActive", False):
            return "mdi:check-circle"
        return "mdi:alert-circle"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )
