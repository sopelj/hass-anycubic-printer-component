from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import cast

from homeassistant import core
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util
import voluptuous as vol

from .const import DEFAULT_NAME, DEFAULT_PORT, DOMAIN
from .utils import AnycubicPrinter

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required(CONF_IP_ADDRESS): cv.matches_regex(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'),
                        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                    }
                )
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)


class AnycubicDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"anycubic-{config.entry_id}",
            update_interval=timedelta(seconds=interval),
        )
        self._printer = AnycubicPrinter(
            config.data[CONF_IP_ADDRESS],
            config.data.get(CONF_PORT, DEFAULT_PORT)
        )
        self.data = {"info": {}, "status": {}, "last_read_time": None, "name": DEFAULT_NAME}

    async def _async_update_data(self):
        try:
            sys_info = await self._printer.get_sys_info()
        except asyncio.TimeoutError as e:
            raise UpdateFailed(e) from e
        status = await self._printer.get_status()
        name = await self._printer.get_name()
        return {"info": sys_info, "status": status, "last_read_time": dt_util.utcnow(), 'name': name}

    @property
    def device_info(self) -> DeviceInfo:
        unique_id = cast(str, self.config_entry.unique_id)
        return DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=self.data['name'],
            model=self.data['info'].get('model', None),
            sw_version=self.data['info'].get('firmware', None),
            manufacturer="Anycubic",
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Anycubic Printer from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    coordinator = AnycubicDataUpdateCoordinator(hass, entry, 60)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Anycubic component."""
    return True
