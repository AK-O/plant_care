from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import (
    DOMAIN,
    TASK_WATERING,
    TASK_FERTILIZING,
    OPT_TEMP_ENTITY_ID,
    OPT_HUMIDITY_ENTITY_ID,
    OPT_MOISTURE_ENTITY_ID,
)
from .device import PlantCareEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            # Due tasks
            PlantCareDueBinarySensor(entry, coordinator, TASK_WATERING),
            PlantCareDueBinarySensor(entry, coordinator, TASK_FERTILIZING),
            # Env bounds (disabled-by-default if no external sensor configured)
            PlantCareEnvOutOfRangeBinarySensor(entry, coordinator, "temperature"),
            PlantCareEnvOutOfRangeBinarySensor(entry, coordinator, "humidity"),
            PlantCareEnvOutOfRangeBinarySensor(entry, coordinator, "moisture"),
        ]
    )


class PlantCareDueBinarySensor(PlantCareEntity, BinarySensorEntity):
    _attr_device_class = "problem"

    def __init__(self, entry, coordinator, task_type: str):
        super().__init__(entry, coordinator)
        self.task_type = task_type
        plant_id = entry.data.get("plant_id", entry.entry_id)
        plant_name = entry.data.get("plant_name", "Plant")

        if task_type == TASK_WATERING:
            self._attr_name = f"{plant_name} Watering Due"
            self._attr_unique_id = f"{plant_id}_watering_due"
            self._attr_suggested_object_id = f"{plant_id}_watering_due"
            self._attr_icon = "mdi:watering-can-outline"
        else:
            self._attr_name = f"{plant_name} Fertilizing Due"
            self._attr_unique_id = f"{plant_id}_fertilizing_due"
            self._attr_suggested_object_id = f"{plant_id}_fertilizing_due"
            self._attr_icon = "mdi:bottle-tonic-outline"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data["tasks"][self.task_type].is_due)

    @property
    def extra_state_attributes(self):
        t = self.coordinator.data["tasks"][self.task_type]
        return {
            "next_due_date": t.next_due_date.isoformat() if t.next_due_date else None,
            "days_overdue": t.days_overdue,
        }


class PlantCareEnvOutOfRangeBinarySensor(PlantCareEntity, BinarySensorEntity):
    """Binary sensor that turns on when the selected env sensor is out of bounds.

    UX:
    - Always created so users can discover it
    - Disabled by default if no source sensor is configured
    - Unavailable if not configured or source state invalid
    """

    _attr_device_class = "problem"

    def __init__(self, entry, coordinator, metric: str):
        super().__init__(entry, coordinator)
        self.metric = metric

        plant_id = entry.data.get("plant_id", entry.entry_id)
        plant_name = entry.data.get("plant_name", "Plant")

        pretty = {
            "temperature": "Temperature",
            "humidity": "Humidity",
            "moisture": "Moisture",
        }[metric]

        self._attr_name = f"{plant_name} {pretty} Out of range"
        self._attr_unique_id = f"{plant_id}_{metric}_out_of_range"
        self._attr_suggested_object_id = f"{plant_id}_{metric}_out_of_range"

        # Disabled by default if no external sensor configured
        opt_key = {
            "temperature": OPT_TEMP_ENTITY_ID,
            "humidity": OPT_HUMIDITY_ENTITY_ID,
            "moisture": OPT_MOISTURE_ENTITY_ID,
        }[metric]
        is_configured = bool((entry.options.get(opt_key) or "").strip())
        self._attr_entity_registry_enabled_default = is_configured

        # Icons: default + alert
        self._icon_ok = {
            "temperature": "mdi:thermometer",
            "humidity": "mdi:water-percent",
            "moisture": "mdi:flower",
        }[metric]
        self._icon_bad = {
            "temperature": "mdi:thermometer-alert",
            "humidity": "mdi:water-alert",
            "moisture": "mdi:flower-outline",
        }[metric]

    def _metric_data(self) -> dict:
        data = (self.coordinator.data or {}).get("env", {})
        return data.get(self.metric, {})

    @property
    def available(self) -> bool:
        # out_of_range == None means unavailable (no configured sensor / invalid value)
        oor = self._metric_data().get("out_of_range")
        return oor is not None

    @property
    def is_on(self) -> bool:
        oor = self._metric_data().get("out_of_range")
        return bool(oor) if oor is not None else False

    @property
    def icon(self) -> str | None:
        return self._icon_bad if self.is_on else self._icon_ok

    @property
    def extra_state_attributes(self):
        m = self._metric_data()
        return {
            "value": m.get("value"),
            "min": m.get("min"),
            "max": m.get("max"),
            "deviation": m.get("deviation"),
        }
