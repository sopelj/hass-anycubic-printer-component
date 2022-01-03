import asyncio
from typing import Any, Optional

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DEFAULT_PORT, DOMAIN
from .utils import AnycubicPrinter

CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS, default=''): cv.matches_regex(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'),
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                printer = AnycubicPrinter(user_input[CONF_IP_ADDRESS], user_input.get(CONF_PORT, DEFAULT_PORT))
                info = await printer.get_sys_info()
                await self.async_set_unique_id(info['identifier'], raise_on_progress=False)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info['model'], data=user_input)
            except data_entry_flow.AbortFlow as err:
                raise err from None
            except asyncio.TimeoutError:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    async def async_step_import(self, user_input):
        return await self.async_step_user(user_input)
