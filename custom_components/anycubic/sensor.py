"""Sensor entities for component."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import _LOGGER, AnycubicDataUpdateCoordinator
from .const import (
    DOMAIN,
    SERVICE_SEND_COMMAND,
    SERVICE_SET_PRINTER_NAME,
    STATUS_FINISHED,
    STATUS_LABELS,
    STATUS_PAUSED,
    STATUS_PRINTING,
)
from .services import (
    SEND_COMMAND_SCHEMA,
    SET_PRINTER_NAME_SCHEMA,
    send_command,
    set_printer_name,
)


class AnycubicSensorBase(CoordinatorEntity):
    """Base entity for all sensors."""

    coordinator: AnycubicDataUpdateCoordinator

    def __init__(
        self,
        coordinator: AnycubicDataUpdateCoordinator,
        sensor_type: str,
        device_id: str,
    ) -> None:
        """Set sensor names and attributes."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"Anycubic Printer {sensor_type}"
        self._attr_unique_id = f"{sensor_type}-{device_id}".lower()

    @property
    def device_info(self) -> DeviceInfo:
        """Device info."""
        return self.coordinator.device_info

    @property
    def available(self) -> bool:
        """Check availability."""
        return self.coordinator.last_update_success and self.coordinator.data["status"]


class AnycubicPrintStatusSensor(AnycubicSensorBase):
    """Anycubic Printer State."""

    _attr_icon = "mdi:printer-3d"

    def __init__(
        self,
        coordinator: AnycubicDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Set up state sensor."""
        super().__init__(coordinator, "State", device_id)

    @property
    def state(self) -> str | None:
        """State of printer."""
        status: dict[str, Any] = self.coordinator.data["status"]
        status_code = status.get("code")
        return STATUS_LABELS.get(status_code, status_code) or None

    @property
    def state_attributes(self) -> dict[str, Any]:
        """Return a list of attributes."""
        return {
            "name": self.coordinator.data["name"],
            "file_list": list(self.coordinator.data["files"]),
            **self.coordinator.data["info"],
            **self.coordinator.data["status"],
        }


class AnycubicPrintJobPercentageSensor(AnycubicSensorBase, SensorEntity):
    """Printer Progress Sensor."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:file-percent"

    def __init__(
        self,
        coordinator: AnycubicDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Set up printer progress sensor."""
        super().__init__(coordinator, "Job Percentage", device_id)

    @property
    def native_value(self) -> int | None:
        """Job progress value."""
        status: dict[str, Any] = self.coordinator.data["status"]
        _LOGGER.info(f"{status}")
        if status["code"] not in (STATUS_PRINTING, STATUS_PAUSED, STATUS_FINISHED):
            return None
        if status["code"] == STATUS_FINISHED:
            return 100
        return status.get("progress", 0)


class AnycubicPrintEstimatedFinishTimeSensor(AnycubicSensorBase, SensorEntity):
    """Estimated Print End Time Sensor."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: AnycubicDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Set up Estimated Print End Time Sensor."""
        super().__init__(coordinator, "Estimated Finish Time", device_id)

    @property
    def native_value(self) -> datetime | None:
        """Return Estimated print time."""
        status: dict[str, Any] = self.coordinator.data["status"]
        if status["code"] not in (STATUS_PRINTING, STATUS_PAUSED):
            return None
        read_time = self.coordinator.data["last_read_time"]
        return read_time + timedelta(seconds=status.get("time_remaining", 0))


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator: AnycubicDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]
    device_id = config_entry.unique_id
    assert device_id is not None
    entities: list[SensorEntity] = [
        AnycubicPrintStatusSensor(coordinator, device_id),
        AnycubicPrintJobPercentageSensor(coordinator, device_id),
        AnycubicPrintEstimatedFinishTimeSensor(coordinator, device_id),
    ]
    async_add_entities(entities)

    # Setup Services
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SET_PRINTER_NAME,
        SET_PRINTER_NAME_SCHEMA,
        set_printer_name,
    )
    platform.async_register_entity_service(
        SERVICE_SEND_COMMAND,
        SEND_COMMAND_SCHEMA,
        send_command,
    )
