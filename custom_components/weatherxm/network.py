from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorEntity,
)

from .const import DOMAIN


class WeatherXMNetworkSensor(CoordinatorEntity, SensorEntity):
    """WeatherXM Network/Connectivity Sensor."""

    def __init__(self, coordinator, device_id, alias):
        """Initialize."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Network"
        self._attr_unique_id = f"{alias}_network"

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
            bundle = device.get("bundle", {})
            connectivity = bundle.get("connectivity")
            if connectivity:
                return connectivity
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        device = self._get_device_data()
        if device:
            bundle = device.get("bundle", {})
            return {
                "connectivity": bundle.get("connectivity"),
                "weather_station_model": bundle.get("ws_model"),
                "gateway_model": bundle.get("gw_model"),
                "profile": device.get("profile"),
                "bundle_name": bundle.get("name"),
                "bundle_title": bundle.get("title"),
                "documentation_url": bundle.get("url"),
            }
        return {}

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        device = self._get_device_data()
        if device:
            connectivity = device.get("bundle", {}).get("connectivity")
            if connectivity == "wifi":
                return "mdi:wifi"
            elif connectivity == "lorawan":
                return "mdi:access-point-network"
        return "mdi:help-network"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )
