import aiohttp
import logging
from homeassistant.components.weather import WeatherEntity
from homeassistant.const import UnitOfTemperature, UnitOfPressure, UnitOfSpeed
from .const import API_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

WIND_DIRECTION_MAP = {
    "S": "S",
    "J": "S",
    "SZ": "NW",
    "SV": "NE",
    "Z": "W",
    "V": "E",
    "JZ": "SW",
    "JV": "SE",
    "N": "N"
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up ARSO Weather entity based on a config entry."""
    async_add_entities([ArsoWeather(config_entry.data["location"])])

class ArsoWeather(WeatherEntity):
    """Representation of ARSO Weather condition."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_pressure_unit = UnitOfPressure.HPA
    _attr_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_visibility_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_precipitation_unit = "mm"

    def __init__(self, location):
        """Initialize the ARSO Weather entity."""
        self._location = location
        self._attr_name = f"ARSO Weather {location}"
        self._attr_native_temperature = None  # Pravilno opredeljen atribut za temperaturo
        self._attr_condition = None
        self._attr_native_pressure = None
        self._attr_humidity = None
        self._attr_native_wind_speed = None
        self._attr_wind_bearing = None
        self._attr_native_precipitation = None

    async def async_update(self):
        """Fetch new state data for the sensor."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}?location={self._location}") as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug(f"Full API response: {data}")
                    latest_data = None
                    
                    if "forecast24h" in data:
                        latest_day = data["forecast24h"]["features"][0]["properties"]["days"][0]
                        latest_data = latest_day["timeline"][-1]  # Zadnji časovni interval

                    if not latest_data and "forecast3h" in data:
                        latest_day = data["forecast3h"]["features"][0]["properties"]["days"][0]
                        latest_data = latest_day["timeline"][-1]  # Zadnji časovni interval

                    if latest_data:
                        temperature = latest_data.get('t')
                        if temperature is not None:
                            try:
                                self._attr_native_temperature = float(temperature)
                            except ValueError:
                                _LOGGER.error(f"Failed to convert temperature value {temperature} to float.")
                                self._attr_native_temperature = None
                        else:
                            self._attr_native_temperature = None

                        self._attr_condition = latest_data.get('clouds_shortText')
                        self._attr_native_pressure = self._safe_cast(latest_data.get('msl'), float)
                        self._attr_humidity = self._safe_cast(latest_data.get('rh'), float)
                        self._attr_native_wind_speed = self._safe_cast(latest_data.get('ff_val'), float)
                        wind_bearing_slovene = latest_data.get('dd_shortText')
                        self._attr_wind_bearing = WIND_DIRECTION_MAP.get(wind_bearing_slovene, wind_bearing_slovene)
                        self._attr_native_precipitation = self._safe_cast(latest_data.get('tp_acc'), float)
                    else:
                        _LOGGER.debug("No valid forecast data found.")
                        self._reset_attributes()

    def _reset_attributes(self):
        """Reset all attributes to None."""
        self._attr_native_temperature = None
        self._attr_condition = None
        self._attr_native_pressure = None
        self._attr_humidity = None
        self._attr_native_wind_speed = None
        self._attr_wind_bearing = None
        self._attr_native_precipitation = None

    def _safe_cast(self, val, to_type, default=None):
        """Safely cast a value to a specified type."""
        try:
            return to_type(val)
        except (ValueError, TypeError):
            _LOGGER.debug(f"Failed to cast value {val} to {to_type}")
            return default

    @property
    def native_temperature(self):
        return self._attr_native_temperature

    @property
    def native_temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def native_pressure(self):
        return self._attr_native_pressure

    @property
    def native_pressure_unit(self):
        return UnitOfPressure.HPA

    @property
    def humidity(self):
        return self._attr_humidity

    @property
    def native_wind_speed(self):
        return self._attr_native_wind_speed

    @property
    def native_wind_speed_unit(self):
        return UnitOfSpeed.KILOMETERS_PER_HOUR

    @property
    def wind_bearing(self):
        return self._attr_wind_bearing

    @property
    def native_precipitation(self):
        return self._attr_native_precipitation

    @property
    def native_precipitation_unit(self):
        return "mm"

    @property
    def condition(self):
        return self._attr_condition
