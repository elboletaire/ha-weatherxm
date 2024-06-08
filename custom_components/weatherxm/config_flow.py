"""Config flow for WeatherXM integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

import requests
import json

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, DEFAULT_HOST, CONF_FILTER_OWNED_DEVICES

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_FILTER_OWNED_DEVICES, default=False): bool,
    }
)

class WeatherXMHub:
    """WeatherXM class for authentication and device data retrieval."""

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {'username': username, 'password': password}
        try:
            r = requests.post(f'{self.host}/api/v1/auth/login', data=json.dumps(payload), headers=headers)
            if r.status_code == requests.codes.ok:
                self.auth_token = r.json()['token']
                return True
            else:
                _LOGGER.error("Authentication failed: %s", r.text)
                return False
        except requests.RequestException as e:
            _LOGGER.error("Error during authentication: %s", e)
            return False


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    hub = WeatherXMHub(data[CONF_HOST])

    if not await hass.async_add_executor_job(hub.authenticate, data[CONF_USERNAME], data[CONF_PASSWORD]):
        raise InvalidAuth

    return {"title": "WeatherXM Account"}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WeatherXM."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input, options=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    # commented for now since I'm not able to make it work as I would like
    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry):
    #     return WeatherXMOptionsFlowHandler(config_entry)

class WeatherXMOptionsFlowHandler(OptionsFlow):
    """Handle options flow for WeatherXM."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=STEP_USER_DATA_SCHEMA.extend({
                vol.Required(CONF_HOST, default=self.config_entry.data.get(CONF_HOST, DEFAULT_HOST)): str,
                vol.Required(CONF_USERNAME, default=self.config_entry.data.get(CONF_USERNAME)): str,
                vol.Required(CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD)): str,
                vol.Optional(CONF_FILTER_OWNED_DEVICES, default=self.config_entry.options.get(CONF_FILTER_OWNED_DEVICES, True)): bool,
            }),
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
