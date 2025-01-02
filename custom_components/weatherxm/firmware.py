from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity

class WeatherXMFirmwareSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_id, alias, firmware):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Firmware"
        self._attr_unique_id = f"{alias}_firmware"

    def _get_device_data(self):
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return None
        for device in self.coordinator.data:
            if device['id'] == self._device_id:
                return device
        return None

    @property
    def _firmware(self):
        """Get firmware data from coordinator."""
        device = self._get_device_data()
        return device['attributes'].get('firmware', {}) if device else {}

    @property
    def state(self):
        """Return the current firmware version."""
        return self._firmware.get("current")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "assigned_version": self._firmware.get("assigned")
        }

    @property
    def icon(self):
        return "mdi:chip"
