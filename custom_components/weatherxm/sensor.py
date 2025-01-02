from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .utils import async_setup_entities_list
from .battery import WeatherXMBatteryLevelSensor
from .rewards import WeatherXMRewardsSensor, WeatherXMTotalRewardsSensor
from .firmware import WeatherXMFirmwareSensor
from .last_update import WeatherXMLastUpdateSensor

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]['coordinator']

    # Battery indicators
    batteries = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMBatteryLevelSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias,
        bat_state=device['bat_state'],
        is_active=device['attributes'].get('isActive', False)
    ))
    async_add_entities(batteries, True)

    # Rewards sensors
    rewards = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMRewardsSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias,
        actual_reward=device['rewards']['actual_reward'],
        total_rewards=device['rewards']['total_rewards']
    ))
    async_add_entities(rewards, True)

    # Total rewards sensors
    trewards = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMTotalRewardsSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias,
        total_rewards=device['rewards']['total_rewards']
    ))
    async_add_entities(trewards, True)

    # Firmware sensors
    firmware = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMFirmwareSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias,
        firmware=device['attributes']['firmware']
    ))
    async_add_entities(firmware, True)

    # Last update sensors
    last_update = await async_setup_entities_list(hass, entry, lambda alias, device: WeatherXMLastUpdateSensor(
        coordinator=coordinator,
        device_id=device['id'],
        alias=alias
    ))
    async_add_entities(last_update, True)
