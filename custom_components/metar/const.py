DOMAIN = "metar"

CONF_AIRPORT_NAME = "airport_name"
CONF_AIRPORT_CODE = "airport_code"
CONF_MONITORED_CONDITIONS = "monitored_conditions"

DEFAULT_MONITORED = ["time", "temperature", "wind", "pressure", "visibility", "precipitation", "sky"]

SENSOR_TYPES = {
    "time": ["Updated", None],
    "weather": ["Condition", None],
    "temperature": ["Temperature", "C"],
    "wind": ["Wind speed", None],
    "pressure": ["Pressure", None],
    "visibility": ["Visibility", "m"],
    "precipitation": ["Precipitation", "in"],
    "sky": ["Sky", None]
}