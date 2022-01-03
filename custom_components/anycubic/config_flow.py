import asyncio
from typing import Any, Optional

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT
import voluptuous as vol

from . import _LOGGER
from .const import DEFAULT_PORT, DOMAIN
from .utils import AnycubicPrinter

CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): str,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): str,
})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: dict[str, str] = {}
        _LOGGER.debug(f'{user_input}')
        if user_input is not None:
            try:
                return await self._finalize(user_input)
            except data_entry_flow.AbortFlow as err:
                raise err from None
            except asyncio.TimeoutError:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    async def _finalize(self, user_input: dict[str, Any]):
        printer = AnycubicPrinter(user_input[CONF_IP_ADDRESS], user_input.get(CONF_PORT, DEFAULT_PORT))
        info = await printer.get_sys_info()
        await self.async_set_unique_id(info['identifier'], raise_on_progress=False)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=info['model'], data=user_input)

    async def async_step_import(self, user_input):
        return await self.async_step_user(user_input)
