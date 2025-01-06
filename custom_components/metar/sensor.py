import logging
from datetime import timedelta
import voluptuous as vol
from aiohttp import ClientSession
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.util import Throttle
from homeassistant.const import CONF_MONITORED_CONDITIONS
import homeassistant.helpers.config_validation as cv
from metar import Metar

DOMAIN = 'metar'
CONF_AIRPORT_NAME = 'airport_name'
CONF_AIRPORT_CODE = 'airport_code'
SCAN_INTERVAL = timedelta(seconds=3600)
BASE_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/"

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    'time': ['Updated', None],
    'weather': ['Condition', None],
    'temperature': ['Temperature', 'C'],
    'wind': ['Wind speed', None],
    'pressure': ['Pressure', 'hPa'],
    'visibility': ['Visibility', 'm'],
    'sky': ['Sky', None],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_AIRPORT_NAME): cv.string,
    vol.Required(CONF_AIRPORT_CODE): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=[]): vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

async def async_setup_platform(hass: HomeAssistant, config: ConfigType, async_add_entities, discovery_info=None):
    """Set up the METAR sensor platform."""
    airport = {
        'location': str(config[CONF_AIRPORT_NAME]),
        'code': str(config[CONF_AIRPORT_CODE]),
    }

    session = async_get_clientsession(hass)
    data = MetarData(airport, session)
    sensors = [
        MetarSensor(airport, data, sensor_type, SENSOR_TYPES[sensor_type][1])
        for sensor_type in config[CONF_MONITORED_CONDITIONS]
    ]

    async_add_entities(sensors, True)

class MetarSensor(Entity):
    def __init__(self, airport, weather_data, sensor_type, unit_of_measurement):
        """Initialize the sensor."""
        self._state = None
        self._name = SENSOR_TYPES[sensor_type][0]
        self._unit_of_measurement = unit_of_measurement
        self._airport_name = airport["location"]
        self.type = sensor_type
        self.weather_data = weather_data

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} {self._airport_name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    async def async_update(self):
        """Fetch the latest data from METAR."""
        await self.weather_data.async_update()

        if not self.weather_data.sensor_data:
            self._state = None
            return

        try:
            if self.type == 'time':
                self._state = self.weather_data.sensor_data.time.ctime()
            if self.type == 'temperature':
                degree = self.weather_data.sensor_data.temp.string().split(" ")
                self._state = degree[0]
            elif self.type == 'weather':
                self._state = self.weather_data.sensor_data.present_weather()
            elif self.type == 'wind':
                self._state = self.weather_data.sensor_data.wind()
            elif self.type == 'pressure':
                self._state = self.weather_data.sensor_data.press.string("mb")
            elif self.type == 'visibility':
                self._state = self.weather_data.sensor_data.visibility()
            elif self.type == 'sky':
                self._state = self.weather_data.sensor_data.sky_conditions("\n     ")
        except KeyError:
            self._state = None
            _LOGGER.warning("Condition is currently not available: %s", self.type)

class MetarData:
    def __init__(self, airport, session: ClientSession):
        """Initialize the METAR data object."""
        self._airport_code = airport["code"]
        self._session = session
        self.sensor_data = None

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        """Fetch data from the METAR API."""
        url = f"{BASE_URL}{self._airport_code}.TXT"
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
                text = await response.text()

                for line in text.splitlines():
                    if line.startswith(self._airport_code):
                        self.sensor_data = Metar.Metar(line)
                        _LOGGER.info("METAR Data: %s", self.sensor_data.string())
                        return

                _LOGGER.error("No METAR data found for %s", self._airport_code)
        except Exception as exc:
            _LOGGER.error("Error retrieving METAR data for %s: %s", self._airport_code, exc)
