import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, CONF_AIRPORT_NAME, CONF_AIRPORT_CODE, CONF_MONITORED_CONDITIONS, SENSOR_TYPES

class MetarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_AIRPORT_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_AIRPORT_NAME, default="Pisa"): str,
                vol.Required(CONF_AIRPORT_CODE, default="LIRP"): str,
                vol.Optional(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES.keys())):
                    cv.multi_select(list(SENSOR_TYPES.keys()))
            })
        )