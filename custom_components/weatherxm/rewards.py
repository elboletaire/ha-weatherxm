from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

class WeatherXMRewardsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_id, alias, actual_reward, total_rewards):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._actual_reward = actual_reward
        self._total_rewards = total_rewards
        self._attr_name = f"{alias} Rewards"
        self._attr_unique_id = f"{alias}_rewards"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def state(self):
        return self._actual_reward

    @property
    def extra_state_attributes(self):
        return {
            "total_rewards": self._total_rewards
        }

    @property
    def unit_of_measurement(self):
        return "WXM"

    @property
    def icon(self):
        return "mdi:currency-usd"

class WeatherXMTotalRewardsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_id, alias, total_rewards):
        super().__init__(coordinator)
        self._device_id = device_id
        self._alias = alias
        self._total_rewards = total_rewards
        self._attr_name = f"{alias} Total Rewards"
        self._attr_unique_id = f"{alias}_total_rewards"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def state(self):
        return self._total_rewards

    @property
    def unit_of_measurement(self):
        return "WXM"

    @property
    def icon(self):
        return "mdi:currency-usd"
