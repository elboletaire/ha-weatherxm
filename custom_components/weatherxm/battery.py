from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from .const import DOMAIN

BATTERY_LEVEL_MAP = {
    "ok": 100.0,
    "low": 3.0,
    "off": 0.0
}

class WeatherXMBatteryLevelSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_id, alias, bat_state, is_active):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Battery"
        self._attr_unique_id = f"{alias}_battery"
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE

    def _get_device_data(self):
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return None
        for device in self.coordinator.data:
            if device['id'] == self._device_id:
                return device
        return None

    @property
    def _bat_state(self):
        """Get battery state from coordinator data."""
        device = self._get_device_data()
        return device.get('bat_state') if device else None

    @property
    def _is_active(self):
        """Get active state from coordinator data."""
        device = self._get_device_data()
        return (device.get('attributes') or {}).get('isActive', False) if device else False

    @property
    def native_value(self):
        """Return the battery level, unknown while inactive or unrecognised."""
        if not self._is_active or self._bat_state not in BATTERY_LEVEL_MAP:
            return None
        return BATTERY_LEVEL_MAP[self._bat_state]

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "battery_state": self._bat_state,
            "is_active": self._is_active
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if not self._is_active:
            return "mdi:battery-alert"
        return "mdi:battery" if self._bat_state == "ok" else "mdi:battery-alert"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )
