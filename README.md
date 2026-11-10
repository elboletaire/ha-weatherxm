
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

The integration creates the following entities per device:

| Entity | Description |
| --- | --- |
| `weather.<alias>` | Current weather condition plus hourly and daily forecast. |
| `sensor.<alias>_battery` | Battery level of the device (`battery_state` and `is_active` as attributes). |
| `sensor.<alias>_firmware` | Current firmware version (`assigned_version` as an attribute). |
| `sensor.<alias>_rewards` | Current reward (`total_rewards` as an attribute). |
| `sensor.<alias>_total_rewards` | Total rewards generated to date from that device. |
| `sensor.<alias>_last_update` | Timestamp of the last weather observation received from the station. |
| `sensor.<alias>_last_station_activity` | Timestamp of the last weather station activity (`last_active_at` as an attribute). |
| `sensor.<alias>_activity_status` | Activity status of the weather station (`active`/`inactive`). |
| `sensor.<alias>_quality_score` | Quality of data score (0-100). |
| `sensor.<alias>_network` | Network/connectivity type, with hardware details as attributes. |
| `sensor.<alias>_relation` | Device ownership relation (`owned`/`followed`). |
| `sensor.<alias>_precipitation` | Current precipitation rate, in mm/h. |
| `sensor.<alias>_daily_precipitation` | Precipitation accumulated today, in mm. |
| `sensor.<alias>_temperature` | Current temperature. |
| `sensor.<alias>_feels_like` | Apparent ("feels like") temperature. |
| `sensor.<alias>_humidity` | Relative humidity. |
| `sensor.<alias>_dew_point` | Dew point. |
| `sensor.<alias>_wind_speed` | Wind speed. |
| `sensor.<alias>_wind_gust` | Wind gust speed. |
| `sensor.<alias>_wind_direction` | Wind direction, in degrees. |
| `sensor.<alias>_pressure` | Barometric pressure. |
| `sensor.<alias>_uv_index` | UV index. |
| `sensor.<alias>_solar_irradiance` | Solar irradiance, in W/m². |
| `binary_sensor.<alias>_online` | Whether the station is currently active/online. |
| `geo_location.<alias>` | Device location on the map, with the current weather data as attributes. |

`<alias>` is the alias of the device defined via the WeatherXM app. If you have not defined an alias, the device ID will be used instead.

#### Activity Status Sensor

The activity status sensor provides monitoring capabilities for your weather station:

- **State**: `active` or `inactive`

This sensor is useful for:
- Monitoring station health
- Detecting connectivity issues
- Creating automations for inactive stations

**Example automation:**
```yaml
automation:
  - alias: "Weather Station Inactive Alert"
    triggers:
      - trigger: state
        entity_id: sensor.my_station_activity_status
        to: "inactive"
        for:
          hours: 1
    actions:
      - action: notify.mobile_app
        data:
          message: "Weather station has been inactive for 1 hour"
```

#### Last Station Activity Sensor

The last station activity sensor tracks when the weather station last transmitted data:

- **State**: Timestamp of the last weather station activity
- **Attributes**:
  - `last_active_at`: Timestamp of the last station connection

This sensor is useful for:
- Tracking station data freshness
- Detecting communication delays
- Correlating with data quality metrics

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

- **State**: Connectivity type (`wifi`, `lorawan` or `helium`)
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
    triggers:
      - trigger: numeric_state
        entity_id: sensor.my_station_quality_score
        below: 60
    actions:
      - action: notify.mobile_app
        data:
          message: "Weather station data quality is low ({{ states('sensor.my_station_quality_score') }})"
```

## Development

Run the test suite from the repository root with Python 3.14:

```bash
pip install -r requirements_test.txt
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE] file for more details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes or improvements.

## Support

For support or feature requests, please open an issue on the [GitHub repository](https://github.com/elboletaire/ha-weatherxm/issues).

[LICENSE]: ./LICENSE
