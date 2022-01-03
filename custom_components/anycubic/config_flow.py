import asyncio
from typing import Any

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DEFAULT_PORT, DOMAIN
from .utils import AnycubicPrinter


def _schema_with_defaults(ip_address: str = "", port: int = DEFAULT_PORT):
    return vol.Schema(
        {
            vol.Required(CONF_IP_ADDRESS, default=ip_address): cv.matches_regex(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'),
            vol.Optional(CONF_PORT, default=port): cv.port,
        },
        extra=vol.ALLOW_EXTRA,
    )


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self.discovery_schema = None
        self._user_input = None

    async def async_step_user(self, user_input=None):
        if user_input is None and self._user_input:
            user_input = self._user_input

        if user_input is None:
            data = self.discovery_schema or _schema_with_defaults()
            return self.async_show_form(step_id="user", data_schema=data)

        errors = {}
        try:
            return await self._finish_config(user_input)
        except data_entry_flow.AbortFlow as err:
            raise err from None
        except asyncio.TimeoutError:  # pylint: disable=broad-except
            errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=_schema_with_defaults(
                user_input.get(CONF_IP_ADDRESS),
                user_input.get(CONF_PORT),
            ),
        )

    async def _finish_config(self, user_input: dict[str, Any]):
        printer = AnycubicPrinter(user_input[CONF_IP_ADDRESS], user_input.get(CONF_PORT, DEFAULT_PORT))
        info = await printer.get_sys_info()
        await self.async_set_unique_id(info['identifier'], raise_on_progress=False)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=info['model'], data=user_input)

    async def async_step_import(self, user_input):
        return await self.async_step_user(user_input)
