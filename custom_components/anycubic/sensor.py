from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import _LOGGER, AnycubicDataUpdateCoordinator
from .const import DOMAIN


class AnycubicSensorBase(CoordinatorEntity, SensorEntity):
    coordinator: AnycubicDataUpdateCoordinator

    def __init__(
        self,
        coordinator: AnycubicDataUpdateCoordinator,
        sensor_type: str,
        device_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"Anycubic {sensor_type}"
        self._attr_unique_id = f"{sensor_type}-{device_id}"

    @property
    def device_info(self):
        return self.coordinator.device_info


class AnycubicPrintStatusSensor(AnycubicSensorBase):
    _attr_icon = "mdi:printer-3d"

    def __init__(self, coordinator: AnycubicDataUpdateCoordinator, device_id: str) -> None:
        super().__init__(coordinator, "Current State", device_id)

    @property
    def native_value(self):
        status: dict[str, Any] = self.coordinator.data["status"]
        return status['code'] if status else None

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self.coordinator.data["status"]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AnycubicDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    device_id = config_entry.unique_id
    assert device_id is not None
    entities: list[SensorEntity] = [
        AnycubicPrintStatusSensor(coordinator, device_id)
    ]
    async_add_entities(entities)
