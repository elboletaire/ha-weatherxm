from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)

from .const import DOMAIN


class WeatherXMLastStationActivitySensor(CoordinatorEntity, SensorEntity):
    """WeatherXM Last Station Activity Sensor."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, device_id, alias):
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Last Station Activity"
        self._attr_unique_id = f"{alias}_last_station_activity"

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
        if device:
            last_activity = device["attributes"].get("lastWeatherStationActivity")
            if last_activity:
                return last_activity
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        device = self._get_device_data()
        if device:
            return {"last_active_at": device["attributes"].get("lastActiveAt")}
        return {}

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:clock-check"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )
