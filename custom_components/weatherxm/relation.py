from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorEntity,
)

from .const import DOMAIN


class WeatherXMRelationSensor(CoordinatorEntity, SensorEntity):
    """WeatherXM Device Relation Sensor."""

    def __init__(self, coordinator, device_id, alias):
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Relation"
        self._attr_unique_id = f"{alias}_relation"

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
            relation = device.get("relation")
            if relation:
                return relation
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        device = self._get_device_data()
        if device:
            attributes = device.get("attributes", {})
            return {
                "relation": device.get("relation"),
                "claimed_at": attributes.get("claimedAt"),
                "device_id": device.get("id"),
                "name": device.get("name"),
                "label": device.get("label"),
                "address": device.get("address"),
                "timezone": device.get("timezone"),
            }
        return {}

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        device = self._get_device_data()
        if device:
            relation = device.get("relation")
            if relation == "owned":
                return "mdi:star"
            elif relation == "followed":
                return "mdi:star-outline"
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
