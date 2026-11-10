from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)

from .const import DOMAIN


class WeatherXMQualitySensor(CoordinatorEntity, SensorEntity):
    """WeatherXM Quality of Data Sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, device_id, alias):
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Quality Score"
        self._attr_unique_id = f"{alias}_quality_score"

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
        """Return the state of the sensor."""
        device = self._get_device_data()
        if device:
            metrics = device.get("metrics") or {}
            return metrics.get("qod_score")
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        device = self._get_device_data()
        if device:
            metrics = device.get("metrics") or {}
            return {
                "quality_score": metrics.get("qod_score"),
                "penalty_reason": metrics.get("pol_reason"),
                "last_metric_update": metrics.get("ts"),
            }
        return {}

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        device = self._get_device_data()
        if device:
            score = (device.get("metrics") or {}).get("qod_score")
            if score is None:
                return "mdi:help-circle"
            if score >= 80:
                return "mdi:check-decagram"
            elif score >= 60:
                return "mdi:alert-circle"
            else:
                return "mdi:alert-octagon"
        return "mdi:help-circle"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )
