from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Optional, Any

from homeassistant.components.sensor import PLATFORM_SCHEMA, Entity
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME, CONF_PORT

from homeassistant.helpers import config_validation as cv
import voluptuous as vol
from homeassistant.helpers.typing import HomeAssistantType, ConfigType, DiscoveryInfoType

from custom_components.anycubic.anycubic import AnycubicPrinter

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP_ADDRESS): cv.matches_regex(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'),
        vol.Optional(CONF_PORT, default=6000): cv.port,
    }
)


class AnycubicEntity(Entity):
    def __init__(self, ip_address: str, port: int) -> None:
        super().__init__()
        self.ip_address = ip_address
        self.port = port
        self.attrs: dict[str, Any] = {}
        self._unique_id = f"anycubic_{ip_address.replace('.', '_')}"
        self._name: Optional[str] = None
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> dict[str, Any]:
        return self.attrs

    async def async_update(self) -> None:
        printer = AnycubicPrinter(self.ip_address, self.port)
        try:
            attrs = await printer.get_sys_info()
        except asyncio.TimeoutError:
            self._available = False
            return
        self._available = True
        status = await printer.get_status()
        self._state = status['status']
        attrs.update(**status)
        self.attrs = attrs


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        [AnycubicEntity(config[CONF_IP_ADDRESS], config.get(CONF_PORT, 6000))],
        update_before_add=True
    )
