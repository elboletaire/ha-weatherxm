
# WeatherXM Home Assistant Integration

WeatherXM Home Assistant integration connects WeatherXM weather stations with Home Assistant, providing real-time weather data from around the world to your home automation system.

> Note: A WeatherXM account is required, but owning a device is not necessary; you can get data of any followed device.

## Installation

### HACS Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=elboletaire&repository=ha-weatherxm&category=integration)

1.  **Add Custom Repository:**
    -   Go to HACS in Home Assistant.
    -   Click on `Integrations` > `top three dot menu` > `Custom repositories`.
    -   Add `https://github.com/elboletaire/ha-weatherxm` as Repository and select `Integration` as the Category.

2.  **Install the Integration:**
    -   Search for "WeatherXM" in HACS and install.

### Manual Installation

1.  **Clone the Repository:**

~~~bash
git clone https://github.com/elboletaire/ha-weatherxm.git
~~~

2.  **Copy to Home Assistant:** Copy the `custom_components/weatherxm` directory to your Home Assistant `custom_components` directory.
3.  **Restart Home Assistant:** Restart Home Assistant to load the new integration.

## Configuration

1.  Go to the Home Assistant web interface.
2.  Navigate to `Configuration` > `Integrations`.
3.  Click on `Add Integration` and search for "WeatherXM".
4.  Follow the on-screen instructions to configure the integration.

> **Note:** A WeatherXM account is required, but owning a device is not necessary; you can follow any WeatherXM device and they will be populating your sensors.

## Usage

Once configured, you can access WeatherXM data in your Home Assistant dashboard and use it in your automations.

### Entities

The integration creates the following sensors:

- `weather.<alias>`, with all the weather and forecast information.
- `sensor.<alias>_battery`, with the battery level of the device.
- `sensor.<alias>_firmware`, with the firmware version of the device.
- `sensor.<alias>_rewards`, with the rewards of the device (also has total_rewards as additional attribute).
- `sensor.<alias>_total_rewards`, with the total rewards generated to date from that device.

`<alias>` is the alias of the device defined via the WeatherXM app. If you have not defined an alias, the device ID will be used instead.

## License

This project is licensed under the MIT License. See the [LICENSE] file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.

## Support

For support or feature requests, please open an issue on the [GitHub repository](https://github.com/elboletaire/ha-weatherxm/issues).

[LICENSE]: ./LICENSE
