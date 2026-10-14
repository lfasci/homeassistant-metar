from datetime import timezone

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfLength,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import (
    CONF_AIRPORT_CODE,
    CONF_AIRPORT_NAME,
    CONF_MONITORED_CONDITIONS,
    DOMAIN,
    SENSOR_TYPES,
)
from .metar_data import MetarData

# sensor_type: (device_class, native_unit, state_class)
SENSOR_META = {
    "time": (SensorDeviceClass.TIMESTAMP, None, None),
    "temperature": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT),
    "pressure": (SensorDeviceClass.ATMOSPHERIC_PRESSURE, UnitOfPressure.HPA, SensorStateClass.MEASUREMENT),
    "visibility": (SensorDeviceClass.DISTANCE, UnitOfLength.METERS, SensorStateClass.MEASUREMENT),
    "precipitation": (SensorDeviceClass.PRECIPITATION, UnitOfPrecipitationDepth.INCHES, SensorStateClass.MEASUREMENT),
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    config = config_entry.data
    airport = {
        "location": config[CONF_AIRPORT_NAME],
        "code": config[CONF_AIRPORT_CODE].strip().upper(),  # NOAA file names are upper case
    }

    data = MetarData(hass, airport)
    # Fetch once before adding entities so all sensors start with data
    await data.async_update()

    async_add_entities(
        [
            MetarSensor(config_entry, airport, data, sensor_type)
            for sensor_type in config.get(CONF_MONITORED_CONDITIONS, [])
        ],
        True,
    )


class MetarSensor(SensorEntity):
    def __init__(self, entry, airport, weather_data, sensor_type):
        self.type = sensor_type
        self.weather_data = weather_data

        # Keep the previous naming scheme so existing entity IDs stay the same
        self._attr_name = f"{SENSOR_TYPES[sensor_type][0]} {airport['location']}"

        # unique_id + device_info register the entities in the entity/device registry
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"METAR {airport['code']}",
            model=airport["location"],
            manufacturer="NOAA / NWS",
            entry_type=DeviceEntryType.SERVICE,
        )

        device_class, unit, state_class = SENSOR_META.get(sensor_type, (None, None, None))
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class

    async def async_update(self):
        await self.weather_data.async_update()
        metar = self.weather_data.sensor_data

        if not metar:
            self._attr_native_value = None
            return

        try:
            t = self.type
            if t == "time":
                # METAR observation time is UTC
                self._attr_native_value = metar.time.replace(tzinfo=timezone.utc) if metar.time else None
            elif t == "temperature":
                self._attr_native_value = metar.temp.value("C") if metar.temp else None
            elif t == "pressure":
                self._attr_native_value = round(metar.press.value("HPA"), 1) if metar.press else None
            elif t == "visibility":
                self._attr_native_value = metar.vis.value("M") if metar.vis else None
            elif t == "precipitation":
                self._attr_native_value = metar.precip_1hr.value("IN") if metar.precip_1hr else None
            elif t == "weather":
                self._attr_native_value = metar.present_weather() or None
            elif t == "wind":
                self._attr_native_value = metar.wind() or None
            elif t == "sky":
                self._attr_native_value = metar.sky_conditions("\n     ") or None
        except Exception:
            self._attr_native_value = None
