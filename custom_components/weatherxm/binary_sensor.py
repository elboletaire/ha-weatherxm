from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .utils import async_setup_entities_list

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]['coordinator']

    online = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMOnlineSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias
    ))
    async_add_entities(online, True)

class WeatherXMOnlineSensor(CoordinatorEntity, BinarySensorEntity):
    """WeatherXM station online/offline status."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, device_id, alias):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Online"
        self._attr_unique_id = f"{alias}_online"

    def _get_device_data(self):
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return None
        for device in self.coordinator.data:
            if device['id'] == self._device_id:
                return device
        return None

    @property
    def is_on(self):
        """Return True if the station is active."""
        device = self._get_device_data()
        return device['attributes'].get('isActive', False) if device else False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )
