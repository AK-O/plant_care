from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, TASK_WATERING, TASK_FERTILIZING
from .device import PlantCareEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    storage = hass.data[DOMAIN][entry.entry_id]["storage"]

    async_add_entities(
        [
            PlantCareMarkDoneButton(entry, coordinator, storage, TASK_WATERING),
            PlantCareMarkDoneButton(entry, coordinator, storage, TASK_FERTILIZING),
        ]
    )


class PlantCareMarkDoneButton(PlantCareEntity, ButtonEntity):
    def __init__(self, entry, coordinator, storage, task_type: str):
        super().__init__(entry, coordinator)
        self.storage = storage
        self.task_type = task_type

        plant_id = entry.data.get("plant_id", entry.entry_id)
        plant_name = entry.data.get("plant_name", "Plant")

        if task_type == TASK_WATERING:
            self._attr_name = f"{plant_name} Watering Mark watered"
            self._attr_icon = "mdi:watering-can"
            self._attr_unique_id = f"{plant_id}_watering_mark_watered"
            self._attr_suggested_object_id = f"{plant_id}_watering_mark_watered"
        else:
            self._attr_name = f"{plant_name} Fertilizing Mark fertilized"
            self._attr_icon = "mdi:bottle-tonic"
            self._attr_unique_id = f"{plant_id}_fertilizing_mark_fertilized"
            self._attr_suggested_object_id = f"{plant_id}_fertilizing_mark_fertilized"

    async def async_press(self) -> None:
        now = dt_util.now()
        iso = dt_util.as_local(now).isoformat()
        await self.storage.set_last_done(self.entry.entry_id, self.task_type, iso)
        await self.coordinator.async_refresh()
