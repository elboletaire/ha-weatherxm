from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity

class WeatherXMFirmwareSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_id, alias, firmware):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._firmware = firmware
        self._attr_name = f"{alias} Firmware"
        self._attr_unique_id = f"{alias}_firmware"

    @property
    def state(self):
        return self._firmware.get("current")

    @property
    def extra_state_attributes(self):
        return {
            "assigned_version": self._firmware.get("assigned")
        }

    @property
    def icon(self):
        return "mdi:chip"
