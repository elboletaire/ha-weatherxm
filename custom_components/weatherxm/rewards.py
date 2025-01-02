from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .const import DOMAIN

class WeatherXMRewardsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_id, alias, actual_reward, total_rewards):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Rewards"
        self._attr_unique_id = f"{alias}_rewards"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    def _get_device_data(self):
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return None
        for device in self.coordinator.data:
            if device['id'] == self._device_id:
                return device
        return None

    @property
    def _rewards_data(self):
        """Get rewards data from coordinator."""
        device = self._get_device_data()
        return device['rewards'] if device else {}

    @property
    def state(self):
        """Return the current reward value."""
        return self._rewards_data.get('actual_reward', 0)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "total_rewards": self._rewards_data.get('total_rewards', 0)
        }

    @property
    def unit_of_measurement(self):
        return "WXM"

    @property
    def icon(self):
        return "mdi:currency-usd"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )

class WeatherXMTotalRewardsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_id, alias, total_rewards):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._attr_name = f"{alias} Total Rewards"
        self._attr_unique_id = f"{alias}_total_rewards"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    def _get_device_data(self):
        """Get device data from coordinator."""
        if not self.coordinator.data:
            return None
        for device in self.coordinator.data:
            if device['id'] == self._device_id:
                return device
        return None

    @property
    def _rewards_data(self):
        """Get rewards data from coordinator."""
        device = self._get_device_data()
        return device['rewards'] if device else {}

    @property
    def state(self):
        """Return the total rewards value."""
        return self._rewards_data.get('total_rewards', 0)

    @property
    def unit_of_measurement(self):
        return "WXM"

    @property
    def icon(self):
        return "mdi:currency-usd"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._alias,
            manufacturer="WeatherXM",
            model="Weather Station",
        )
