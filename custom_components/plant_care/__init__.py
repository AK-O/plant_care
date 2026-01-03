from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_call_later, async_track_time_change

from .const import DOMAIN, PLATFORMS, DEFAULT_OPTIONS
from .coordinator import PlantCareCoordinator
from .storage import PlantCareStorage

# Config-entry-only integration (no YAML setup)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Ensure domain storage exists even without async_setup()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("storage", PlantCareStorage(hass))

    storage: PlantCareStorage = hass.data[DOMAIN]["storage"]

    if hasattr(storage, "async_setup"):
        await storage.async_setup()

    # Initialize options on first setup (backward compatible)
    if not entry.options:
        init_opts = dict(DEFAULT_OPTIONS)
        for k in DEFAULT_OPTIONS:
            if k in entry.data:
                init_opts[k] = entry.data[k]
        hass.config_entries.async_update_entry(entry, options=init_opts)

    coordinator = PlantCareCoordinator(hass, entry, storage)

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "storage": storage,
    }

    # Forward platforms first so CoordinatorEntity listeners get attached
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # IMPORTANT: ensure the periodic scheduler starts even if listeners attach later
    # (dummy listener; removed automatically on unload)
    unsub_listener = coordinator.async_add_listener(lambda: None)
    entry.async_on_unload(unsub_listener)

    # Refresh immediately on setup/startup (now entities exist + scheduler will run)
    await coordinator.async_config_entry_first_refresh()

    # Optional: delayed refresh so sensors that come online after boot are picked up
    async def _delayed_refresh(_now) -> None:
        await coordinator.async_refresh()

    entry.async_on_unload(async_call_later(hass, 60, _delayed_refresh))

    # Daily refresh 03:00 (dates/tasks)
    async def _daily_refresh(_now) -> None:
        await coordinator.async_refresh()

    unsub_daily = async_track_time_change(hass, _daily_refresh, hour=3, minute=0, second=0)
    entry.async_on_unload(unsub_daily)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
