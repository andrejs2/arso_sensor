# Custom ARSO Weather Component for Home Assistant

This custom component integrates weather data from the Slovenian Environment Agency (ARSO) into Home Assistant. It uses the ARSO API feed to retrieve current weather conditions and parses the data into usable attributes for Home Assistant entities.

## Installation

**Manual Installation:**
   - Copy the contents of the `custom_components/arso_sensor` directory into your Home Assistant's `custom_components/` folder.
   - Restart Home Assistant.

## Configuration

Add the following configuration to your `configuration.yaml` file:

sensor:
  - platform: arso_sensor
    locations:
      - "Ljubljana"
      - "Celje"
      - "Bohinjska Češnjica"
      - "Logatec"
    scan_interval: 01:00:00 #pick refresh interval. ARSO updates data hourly


