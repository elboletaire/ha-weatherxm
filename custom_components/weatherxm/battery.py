from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

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
        self._bat_state = bat_state
        self._is_active = is_active
        self._attr_name = f"{alias} Battery"
        self._attr_unique_id = f"{alias}_battery"
        self._attr_state_class = SensorDeviceClass.BATTERY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def state(self):
        if not self._is_active:
            return BATTERY_LEVEL_MAP["off"]
        return BATTERY_LEVEL_MAP.get(self._bat_state, 0.0)

    @property
    def unit_of_measurement(self):
        return "%"

    @property
    def extra_state_attributes(self):
        return {
            "battery_state": self._bat_state,
            "is_active": self._is_active
        }

    @property
    def icon(self):
        if not self._is_active:
            return "mdi:battery-alert"
        return "mdi:battery" if self._bat_state == "ok" else "mdi:battery-alert"
