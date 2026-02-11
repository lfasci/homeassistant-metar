import logging
from datetime import timedelta
from aiohttp import ClientSession
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import Throttle
from metar import Metar

BASE_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/"
SCAN_INTERVAL = timedelta(seconds=3600)
_LOGGER = logging.getLogger(__name__)

class MetarData:
    def __init__(self, hass, airport):
        self._airport_code = airport["code"]
        self._session: ClientSession = async_get_clientsession(hass)
        self.sensor_data = None

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
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