"""Services for updating Mug information."""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from homeassistant.const import CONF_NAME
from homeassistant.core import ServiceCall
import voluptuous as vol

from .const import COMMAND_PRINT, CONF_PRINT_CMD, CONF_PRINT_FILE_NAME, EXPOSED_COMMANDS

if TYPE_CHECKING:
    from .sensor import AnycubicPrintStatusSensor


_LOGGER = logging.getLogger(__name__)

SET_PRINTER_NAME_SCHEMA = {
    vol.Required(CONF_NAME): str,
}

SEND_COMMAND_SCHEMA = {
    vol.Required(CONF_PRINT_CMD): vol.In(EXPOSED_COMMANDS),
    vol.Optional(CONF_PRINT_FILE_NAME, default=""): str,
}


async def set_printer_name(
    entity: AnycubicPrintStatusSensor,
    service_call: ServiceCall,
) -> None:
    """Set name of Printer."""
    name: str = service_call.data[CONF_NAME]
    _LOGGER.debug(f"Service called to set name to '{name}'")
    await entity.coordinator.printer.set_name(name)


async def send_command(
    entity: AnycubicPrintStatusSensor,
    service_call: ServiceCall,
) -> None:
    """Send a supported command to the printer."""
    command: str = service_call.data[CONF_PRINT_CMD]
    current_status = entity.coordinator.data["status"]
    _LOGGER.debug(f"Service called run command: '{command}'")
    assert current_status.get("code", None) != command, "Already in desired state"
    if command == COMMAND_PRINT:
        # Ensure filename was provided
        if not (file_name := service_call.data.get(CONF_PRINT_FILE_NAME)):
            raise ValueError("File name is required to start a print")
        # Lookup the numeric version of the filename if that's not what was provided
        if not re.match(r"[0-9]+.pwms", file_name):
            file_name = entity.coordinator.data["files"][file_name]
        await entity.coordinator.printer.start_print(file_name)
    else:
        await entity.coordinator.printer.set_status(command)
