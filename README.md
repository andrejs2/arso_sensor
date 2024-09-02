
# ARSO Weather Sensor for Home Assistant

This custom component integrates ARSO weather data into Home Assistant, allowing users to track weather forecasts for various locations in Slovenia and nearby regions. The component supports multiple locations and provides detailed weather attributes such as temperature, humidity, pressure, wind speed, direction, cloud coverage, and precipitation.

## Installation

1. Download the `arso_sensor` directory and place it in the `custom_components` directory of your Home Assistant configuration.
2. Restart Home Assistant to recognize the new sensor.

## Configuration

To configure the sensor, add the following to your `configuration.yaml` file:

```yaml
sensor:
  - platform: arso_sensor
    locations:
      - "Ljubljana"
      - "Maribor"
    scan_interval: 01:00:00  # Update interval (optional) ARSO updates data hourly

The locations (names of meteorological stations), lat and long data is in ```location_coordinates.csv``` file.

