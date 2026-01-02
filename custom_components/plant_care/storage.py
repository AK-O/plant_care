from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION, TASK_WATERING, TASK_FERTILIZING


@dataclass
class PlantState:
    last_watered: str | None = None  # ISO datetime string
    last_fertilized: str | None = None  # ISO datetime string


class PlantCareStorage:
    """Small persistent store for per-entry state (last_done timestamps)."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] | None = None

    async def async_load(self) -> dict[str, Any]:
        if self._data is None:
            self._data = await self._store.async_load() or {"entries": {}}
            self._data.setdefault("entries", {})
        return self._data

    async def async_save(self) -> None:
        if self._data is None:
            return
        await self._store.async_save(self._data)

    async def get_entry_state(self, entry_id: str) -> PlantState:
        data = await self.async_load()
        entry = data["entries"].get(entry_id, {})
        return PlantState(
            last_watered=entry.get("last_watered"),
            last_fertilized=entry.get("last_fertilized"),
        )

    async def set_last_done(self, entry_id: str, task_type: str, iso_dt: str) -> None:
        data = await self.async_load()
        entry = data["entries"].setdefault(entry_id, {})
        if task_type == TASK_WATERING:
            entry["last_watered"] = iso_dt
        elif task_type == TASK_FERTILIZING:
            entry["last_fertilized"] = iso_dt
        else:
            raise ValueError(f"Unknown task_type: {task_type}")

        await self.async_save()
