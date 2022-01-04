from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AnycubicDataUpdateCoordinator
from .const import DOMAIN


class AnycubicSensorBase(CoordinatorEntity):
    coordinator: AnycubicDataUpdateCoordinator

    def __init__(
        self,
        coordinator: AnycubicDataUpdateCoordinator,
        sensor_type: str,
        device_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"Anycubic Printer {sensor_type}"
        self._attr_unique_id = f"{sensor_type}-{device_id}"

    @property
    def device_info(self):
        return self.coordinator.device_info

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self.coordinator.data["status"]


class AnycubicPrintStatusSensor(AnycubicSensorBase):
    _attr_icon = "mdi:printer-3d"

    def __init__(self, coordinator: AnycubicDataUpdateCoordinator, device_id: str) -> None:
        super().__init__(coordinator, "Current State", device_id)

    @property
    def state(self):
        status: dict[str, Any] = self.coordinator.data["status"]
        return status['code'] if status else None

    @property
    def state_attributes(self) -> dict[str, Any]:
        """Return a list of attributes."""
        return self.coordinator.data["info"] | self.coordinator.data["status"]


class AnycubicPrintJobPercentageSensor(AnycubicSensorBase, SensorEntity):
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:file-percent"

    def __init__(self, coordinator: AnycubicDataUpdateCoordinator, device_id: str) -> None:
        super().__init__(coordinator, "Job Percentage", device_id)

    @property
    def native_value(self) -> int | None:
        status: dict[str, Any] = self.coordinator.data["status"]
        if not status['code'] not in ('print', 'pause', 'finish'):
            return None
        if status['code'] == 'finish':
            return 100
        return status.get('progress', 0)


class AnycubicPrintEstimatedFinishTimeSensor(AnycubicSensorBase, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: AnycubicDataUpdateCoordinator, device_id: str) -> None:
        super().__init__(coordinator, "Estimated Finish Time", device_id)

    @property
    def native_value(self) -> datetime | None:
        status: dict[str, Any] = self.coordinator.data["status"]
        if status['code'] not in ('print', 'pause'):
            return None
        read_time = self.coordinator.data["last_read_time"]
        return read_time + timedelta(seconds=status.get('time_remaining', 0))


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AnycubicDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    device_id = config_entry.unique_id
    assert device_id is not None
    entities: list[SensorEntity] = [
        AnycubicPrintStatusSensor(coordinator, device_id),
        AnycubicPrintJobPercentageSensor(coordinator, device_id),
        AnycubicPrintEstimatedFinishTimeSensor(coordinator, device_id),
    ]
    async_add_entities(entities)
