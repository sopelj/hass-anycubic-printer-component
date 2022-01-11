"""Setup config flow to allow configuring via the UI."""
from __future__ import annotations

import asyncio
import socket
from typing import Any

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT
import voluptuous as vol

from . import _LOGGER
from .const import DEFAULT_PORT, DOMAIN
from .utils import AnycubicPrinter

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
    },
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Printer."""

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle flow started via the user interface."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                return await self._finalize(user_input)
            except data_entry_flow.AbortFlow as err:
                raise err from None
            except (asyncio.TimeoutError, AssertionError):
                errors["base"] = "cannot_connect"
            except socket.gaierror:
                errors["base"] = "invalid_ip"
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.error(str(e))
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=CONFIG_SCHEMA,
            errors=errors,
        )

    async def _finalize(self, user_input: dict[str, Any]):
        """Try to fetch required information and configure entitu."""
        printer = AnycubicPrinter(
            user_input[CONF_IP_ADDRESS],
            user_input.get(CONF_PORT, DEFAULT_PORT),
        )
        info = await printer.get_sys_info()
        assert info, "Failed to fetch information"
        await self.async_set_unique_id(info["identifier"], raise_on_progress=False)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=info["model"], data=user_input)

    async def async_step_import(self, user_input: dict[str, Any]):
        """Handle import flow."""
        return await self.async_step_user(user_input)
