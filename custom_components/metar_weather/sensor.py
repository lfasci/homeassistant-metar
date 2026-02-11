from homeassistant.helpers.entity import Entity
from .const import SENSOR_TYPES, CONF_AIRPORT_NAME, CONF_AIRPORT_CODE, CONF_MONITORED_CONDITIONS
from .metar_data import MetarData

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = config_entry.data
    airport = {
        "location": config[CONF_AIRPORT_NAME],
        "code": config[CONF_AIRPORT_CODE]
    }

    data = MetarData(hass, airport)
    sensors = [
        MetarSensor(airport, data, sensor_type, SENSOR_TYPES[sensor_type][1])
        for sensor_type in config.get(CONF_MONITORED_CONDITIONS, [])
    ]

    async_add_entities(sensors, True)

class MetarSensor(Entity):
    def __init__(self, airport, weather_data, sensor_type, unit_of_measurement):
        self._state = None
        self._name = SENSOR_TYPES[sensor_type][0]
        self._unit_of_measurement = unit_of_measurement
        self._airport_name = airport["location"]
        self.type = sensor_type
        self.weather_data = weather_data

    @property
    def name(self):
        return f"{self._name} {self._airport_name}"

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    async def async_update(self):
        await self.weather_data.async_update()
        metar = self.weather_data.sensor_data

        if not metar:
            self._state = None
            return

        try:
            if self.type == "time":
                self._state = metar.time.ctime()
            elif self.type == "temperature":
                self._state = metar.temp.string().split(" ")[0]
            elif self.type == "weather":
                self._state = metar.present_weather()
            elif self.type == "wind":
                self._state = metar.wind()
            elif self.type == "pressure":
                self._state = metar.press.string("mb")
            elif self.type == "visibility":
                self._state = metar.visibility()
            elif self.type == "precipitation":
                self._state = metar.precip_1hr
            elif self.type == "sky":
                self._state = metar.sky_conditions("\n     ")
        except Exception:
            self._state = None
                        