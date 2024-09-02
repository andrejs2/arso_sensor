import requests
import logging
from datetime import timedelta, datetime
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import UnitOfTemperature, UnitOfLength, UnitOfPressure, UnitOfSpeed
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

CONF_LOCATIONS = "locations"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)  # Privzeti interval 30 minut

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_LOCATIONS): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    locations = config[CONF_LOCATIONS]
    scan_interval = config[CONF_SCAN_INTERVAL]
    
    sensors = []
    for location in locations:
        sensors.append(ArsoWeatherSensor(location, scan_interval))
    add_entities(sensors, True)

class ArsoWeatherSensor(Entity):
    def __init__(self, location, scan_interval):
        self._location = location
        self._state = None
        self._attributes = {}
        self._last_update = None
        self.update = Throttle(scan_interval)(self.update)

    def update(self):
        url = f"https://vreme.arso.gov.si/api/1.0/location/?location={self._location}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            all_forecasts = data['forecast3h']['features'][0]['properties']['days']
            current_forecast = all_forecasts[0]['timeline'][0]

            # Nastavi stanje senzorja - trenutno oblačnost in temperaturo
            current_temperature = current_forecast['t']
            current_clouds = current_forecast['clouds_shortText']
            self._state = f"{current_clouds.capitalize()}, {current_temperature}°C"

            # Zabeleži čas zadnje osvežitve
            self._last_update = datetime.now().isoformat()

            # Atributi za trenutne podatke
            attributes = {
                "Temperature": current_temperature,
                "Humidity": current_forecast['rh'],
                "Pressure": current_forecast['msl'],
                "Wind Speed": current_forecast['ff_val'],
                "Wind Direction": current_forecast['dd_shortText'],
                "Clouds": current_clouds,
                "Last Update": self._last_update
            }

            # Dodajanje napovedi za vse dni in časovne intervale kot ločeni atributi
            for day in all_forecasts:
                date = day['date']
                for timeline in day['timeline']:
                    time_offset = timeline['valid'][11:13]  # Ura iz 'valid' polja
                    forecast_time = f"{date} {time_offset}:00"

                    # Dodajanje posameznih atributov za vsako napoved
                    attributes[f"{forecast_time} Temperature (°C)"] = timeline['t']
                    attributes[f"{forecast_time} Humidity (%)"] = timeline['rh']
                    attributes[f"{forecast_time} Pressure (hPa)"] = timeline['msl']
                    attributes[f"{forecast_time} Wind Speed (km/h)"] = timeline['ff_val']
                    attributes[f"{forecast_time} Wind Direction"] = timeline['dd_shortText']
                    attributes[f"{forecast_time} Clouds"] = timeline['clouds_shortText']
                    attributes[f"{forecast_time} Weather Description"] = timeline.get('nn_shortText', "")
                    attributes[f"{forecast_time} Precipitation (mm)"] = timeline.get('tp_acc', 0)
                    attributes[f"{forecast_time} Weather Icon"] = timeline.get('nn_icon', "")
                    attributes[f"{forecast_time} Clouds and Weather Icon"] = f"{timeline['clouds_shortText']} {timeline.get('nn_icon', '')}"

            self._attributes = attributes

    @property
    def name(self):
        return f"ARSO Weather {self._location}"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes
