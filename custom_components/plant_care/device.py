from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class PlantCareEntity(CoordinatorEntity):
    """Base entity for Plant Care entities (subscribes to the coordinator)."""

    def __init__(self, entry, coordinator) -> None:
        super().__init__(coordinator)
        self.entry = entry

        plant_id = entry.data.get("plant_id", entry.entry_id)
        plant_name = entry.data.get("plant_name", "Plant")

        # All entities under one device per plant
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, plant_id)},
            name=plant_name,
            manufacturer="Plant Care",
            model="Plant",
        )
