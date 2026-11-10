from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.util import dt as dt_util

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
    def native_value(self):
        """Return the timestamp of the last station activity."""
        device = self._get_device_data()
        if device:
            last_activity = (device.get("attributes") or {}).get("lastWeatherStationActivity")
            if last_activity:
                parsed = dt_util.parse_datetime(last_activity)
                if parsed and parsed.tzinfo:
                    return parsed
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        device = self._get_device_data()
        if device:
            return {"last_active_at": (device.get("attributes") or {}).get("lastActiveAt")}
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
