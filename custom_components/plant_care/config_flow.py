from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    CONF_PLANT_ID,
    CONF_PLANT_NAME,
    DEFAULT_OPTIONS,
    OPT_WATERING_INTERVAL_DAYS,
    OPT_FERTILIZING_INTERVAL_DAYS,
    OPT_MOISTURE_MIN,
    OPT_MOISTURE_MAX,
    OPT_HUMIDITY_MIN,
    OPT_HUMIDITY_MAX,
    OPT_TEMP_MIN,
    OPT_TEMP_MAX,
    OPT_LIGHT_MIN,
    OPT_LIGHT_MAX,
    OPT_TEMP_ENTITY_ID,
    OPT_HUMIDITY_ENTITY_ID,
    OPT_MOISTURE_ENTITY_ID,
)

STEP_USER_SCHEMA = vol.Schema(
    {
        # Only required field
        vol.Required(CONF_PLANT_NAME): selector.TextSelector(),
        # Defaults for this plant
        vol.Optional(
            OPT_WATERING_INTERVAL_DAYS,
            default=int(DEFAULT_OPTIONS[OPT_WATERING_INTERVAL_DAYS]),
        ): vol.All(vol.Coerce(int), vol.Range(min=0)),
        vol.Optional(
            OPT_FERTILIZING_INTERVAL_DAYS,
            default=int(DEFAULT_OPTIONS[OPT_FERTILIZING_INTERVAL_DAYS]),
        ): vol.All(vol.Coerce(int), vol.Range(min=0)),
        vol.Optional(
            OPT_MOISTURE_MIN, default=int(DEFAULT_OPTIONS[OPT_MOISTURE_MIN])
        ): vol.Coerce(int),
        vol.Optional(
            OPT_MOISTURE_MAX, default=int(DEFAULT_OPTIONS[OPT_MOISTURE_MAX])
        ): vol.Coerce(int),
        vol.Optional(
            OPT_HUMIDITY_MIN, default=int(DEFAULT_OPTIONS[OPT_HUMIDITY_MIN])
        ): vol.Coerce(int),
        vol.Optional(
            OPT_HUMIDITY_MAX, default=int(DEFAULT_OPTIONS[OPT_HUMIDITY_MAX])
        ): vol.Coerce(int),
        vol.Optional(
            OPT_TEMP_MIN, default=float(DEFAULT_OPTIONS[OPT_TEMP_MIN])
        ): vol.Coerce(float),
        vol.Optional(
            OPT_TEMP_MAX, default=float(DEFAULT_OPTIONS[OPT_TEMP_MAX])
        ): vol.Coerce(float),
        vol.Optional(
            OPT_LIGHT_MIN, default=int(DEFAULT_OPTIONS[OPT_LIGHT_MIN])
        ): vol.Coerce(int),
        vol.Optional(
            OPT_LIGHT_MAX, default=int(DEFAULT_OPTIONS[OPT_LIGHT_MAX])
        ): vol.Coerce(int),
        # Optional external sensors (entity_ids)
        # IMPORTANT: default=None so the selector is truly optional (no forced selection)
        vol.Optional(OPT_TEMP_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Optional(OPT_HUMIDITY_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Optional(OPT_MOISTURE_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
    }
)


class PlantCareConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        from .options_flow import PlantCareOptionsFlowHandler

        return PlantCareOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA)

        plant_name = user_input[CONF_PLANT_NAME].strip()
        plant_id = slugify(plant_name)

        # Use plant_id as unique_id so it stays stable even if the entry title/name changes later
        await self.async_set_unique_id(plant_id)
        self._abort_if_unique_id_configured()

        # Optional sensors: store "" when not selected
        temp_entity = (user_input.get(OPT_TEMP_ENTITY_ID) or "").strip()
        humidity_entity = (user_input.get(OPT_HUMIDITY_ENTITY_ID) or "").strip()
        moisture_entity = (user_input.get(OPT_MOISTURE_ENTITY_ID) or "").strip()

        options = {
            OPT_WATERING_INTERVAL_DAYS: int(user_input[OPT_WATERING_INTERVAL_DAYS]),
            OPT_FERTILIZING_INTERVAL_DAYS: int(
                user_input[OPT_FERTILIZING_INTERVAL_DAYS]
            ),
            OPT_MOISTURE_MIN: int(user_input[OPT_MOISTURE_MIN]),
            OPT_MOISTURE_MAX: int(user_input[OPT_MOISTURE_MAX]),
            OPT_HUMIDITY_MIN: int(user_input[OPT_HUMIDITY_MIN]),
            OPT_HUMIDITY_MAX: int(user_input[OPT_HUMIDITY_MAX]),
            OPT_TEMP_MIN: float(user_input[OPT_TEMP_MIN]),
            OPT_TEMP_MAX: float(user_input[OPT_TEMP_MAX]),
            OPT_LIGHT_MIN: int(user_input[OPT_LIGHT_MIN]),
            OPT_LIGHT_MAX: int(user_input[OPT_LIGHT_MAX]),
            # store optional entity_ids
            OPT_TEMP_ENTITY_ID: temp_entity,
            OPT_HUMIDITY_ENTITY_ID: humidity_entity,
            OPT_MOISTURE_ENTITY_ID: moisture_entity,
        }

        data = {
            CONF_PLANT_NAME: plant_name,
            CONF_PLANT_ID: plant_id,
        }

        return self.async_create_entry(title=plant_name, data=data, options=options)
