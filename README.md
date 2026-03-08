
# WeatherXM Home Assistant Integration

WeatherXM Home Assistant integration connects WeatherXM weather stations with Home Assistant, providing real-time weather data from around the world to your home automation system.

> Note: A WeatherXM account is required, but owning a device is not necessary; you can get data of any followed device.

## Installation

### HACS Installation

WeatherXM extension is published on the Home Assistant Community Store (HACS) repository. You can simply search for it in HACS and install it from there, or proceed with a more manual installation:

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
- `sensor.<alias>_quality_score`, with the quality of data score for the device.
- `sensor.<alias>_network`, with the network/connectivity information.
- `sensor.<alias>_relation`, with the device ownership relation (owned/followed).

`<alias>` is the alias of the device defined via the WeatherXM app. If you have not defined an alias, the device ID will be used instead.

#### Quality Score Sensor

The quality score sensor provides insights into the data quality from your weather station:

- **State**: Quality score (0-100)
- **Attributes**:
  - `quality_score`: Quality of data score
  - `penalty_reason`: Reason for any penalties (if applicable)
  - `last_metric_update`: Timestamp of the last metric update

This sensor is useful for:
- Monitoring data quality and reliability
- Identifying stations with poor data quality
- Understanding penalties affecting rewards

#### Network Sensor

The network sensor provides connectivity and hardware information:

- **State**: Connectivity type (`wifi` or `lorawan`)
- **Attributes**:
  - `connectivity`: Type of network connection
  - `weather_station_model`: Weather station model (e.g., WS1001)
  - `gateway_model`: Gateway model (e.g., WG1200)
  - `profile`: Network profile (e.g., Helium, WeatherXM)
  - `bundle_name`: Internal bundle name
  - `bundle_title`: Display name of the bundle
  - `documentation_url`: Link to device documentation

This sensor is useful for:
- Identifying network connection type
- Tracking hardware models and profiles
- Accessing device documentation

#### Relation Sensor

The relation sensor shows your relationship with the device:

- **State**: `owned` or `followed`
- **Attributes**:
  - `relation`: Your relationship to the device
  - `claimed_at`: When the device was claimed (if owned)
  - `device_id`: Unique device identifier
  - `name`: Device name
  - `label`: Device label
  - `address`: Physical address
  - `timezone`: Device timezone

This sensor is useful for:
- Distinguishing between owned and followed stations
- Tracking device metadata and location
- Filtering devices by ownership

**Example automation:**
```yaml
automation:
  - alias: "Low Quality Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.my_station_quality_score
        below: 60
    action:
      - service: notify.mobile_app
        data:
          message: "Weather station data quality is low ({{ states('sensor.my_station_quality_score') }})"
```

## License

This project is licensed under the MIT License. See the [LICENSE] file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.

## Support

For support or feature requests, please open an issue on the [GitHub repository](https://github.com/elboletaire/ha-weatherxm/issues).

[LICENSE]: ./LICENSE
