from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    OPT_TEMP_ENTITY_ID,
    OPT_HUMIDITY_ENTITY_ID,
    OPT_MOISTURE_ENTITY_ID,
)


class PlantCareOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        # IMPORTANT: don't assign to self.config_entry (read-only property in HA)
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            new_options = dict(self._config_entry.options)

            # Store "" for not set
            new_options[OPT_TEMP_ENTITY_ID] = user_input.get(OPT_TEMP_ENTITY_ID) or ""
            new_options[OPT_HUMIDITY_ENTITY_ID] = (
                user_input.get(OPT_HUMIDITY_ENTITY_ID) or ""
            )
            new_options[OPT_MOISTURE_ENTITY_ID] = (
                user_input.get(OPT_MOISTURE_ENTITY_ID) or ""
            )

            return self.async_create_entry(title="", data=new_options)

        def _opt_with_default(opt_key: str):
            """Return vol.Optional(key, default=...) only if default is a non-empty entity_id."""
            val = (self._config_entry.options.get(opt_key) or "").strip()
            if val:
                return vol.Optional(opt_key, default=val)
            return vol.Optional(opt_key)

        schema = vol.Schema(
            {
                _opt_with_default(OPT_TEMP_ENTITY_ID): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                _opt_with_default(OPT_HUMIDITY_ENTITY_ID): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                _opt_with_default(OPT_MOISTURE_ENTITY_ID): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
