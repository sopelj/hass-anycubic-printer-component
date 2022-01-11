"""Binary Sensor entities for component."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AnycubicDataUpdateCoordinator
from .const import DOMAIN, STATUS_PRINTING


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the available binary sensors."""
    coordinator: AnycubicDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]
    device_id = config_entry.unique_id
    assert device_id is not None
    entities: list[BinarySensorEntity] = [
        AnycubicPrintingBinarySensor(coordinator, device_id),
    ]
    async_add_entities(entities)


class AnycubicPrintingBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor indicting if its currently printing."""

    coordinator: AnycubicDataUpdateCoordinator

    def __init__(
        self,
        coordinator: AnycubicDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Set basic attributes and names for sensors."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = "Anycubic Printing"
        self._attr_unique_id = f"printing-{device_id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Device info."""
        return self.coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        """Return true if printing right now."""
        if not (status := self.coordinator.data["status"]):
            return None
        return bool(status.get("code") == STATUS_PRINTING)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data["status"]
