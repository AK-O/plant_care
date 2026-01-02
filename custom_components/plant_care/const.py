from __future__ import annotations

DOMAIN = "plant_care"

PLATFORMS = ["sensor", "binary_sensor", "button", "number"]

# Entry data keys
CONF_PLANT_ID = "plant_id"
CONF_PLANT_NAME = "plant_name"

# Task types
TASK_WATERING = "watering"
TASK_FERTILIZING = "fertilizing"
TASKS = (TASK_WATERING, TASK_FERTILIZING)

# Option keys (stored in config_entry.options)
OPT_WATERING_INTERVAL_DAYS = "watering_interval_days"
OPT_FERTILIZING_INTERVAL_DAYS = "fertilizing_interval_days"

OPT_MOISTURE_MIN = "moisture_min"
OPT_MOISTURE_MAX = "moisture_max"

OPT_HUMIDITY_MIN = "humidity_min"
OPT_HUMIDITY_MAX = "humidity_max"

OPT_TEMP_MIN = "temp_min"
OPT_TEMP_MAX = "temp_max"

OPT_LIGHT_MIN = "light_min"
OPT_LIGHT_MAX = "light_max"

# Optional external source sensors (entity_ids)
OPT_TEMP_ENTITY_ID = "temp_entity_id"
OPT_HUMIDITY_ENTITY_ID = "humidity_entity_id"
OPT_MOISTURE_ENTITY_ID = "moisture_entity_id"

# Mixed-type defaults: numbers + strings
# (Intervals support 0 to disable; entity_id empty string means "not configured")
DEFAULT_OPTIONS: dict[str, float | str] = {
    OPT_WATERING_INTERVAL_DAYS: 7,
    OPT_FERTILIZING_INTERVAL_DAYS: 30,
    OPT_MOISTURE_MIN: 0,
    OPT_MOISTURE_MAX: 100,
    OPT_HUMIDITY_MIN: 0,
    OPT_HUMIDITY_MAX: 100,
    OPT_TEMP_MIN: 10,
    OPT_TEMP_MAX: 30,
    OPT_LIGHT_MIN: 0,
    OPT_LIGHT_MAX: 100000,
    OPT_TEMP_ENTITY_ID: "",
    OPT_HUMIDITY_ENTITY_ID: "",
    OPT_MOISTURE_ENTITY_ID: "",
}

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}_state"


def plant_object_id(entry, suffix: str) -> str:
    plant_id = entry.data.get(CONF_PLANT_ID, entry.entry_id)
    return f"{plant_id}_{suffix}"
