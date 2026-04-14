"""Sensor platform for League Tracker."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DIVISION_ID, CONF_LEAGUE_ID, DOMAIN, LEAGUE_MAP
from .coordinator import LeagueStandingsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: LeagueStandingsCoordinator = hass.data[DOMAIN][entry.entry_id]
    league_id: str = entry.data[CONF_LEAGUE_ID]
    wanted_division: str | None = entry.data.get(CONF_DIVISION_ID)

    await coordinator.async_config_entry_first_refresh()

    entities: list[StandingsSensor] = []
    for table in coordinator.data or []:
        if wanted_division and table["division_id"] != wanted_division:
            continue
        entities.append(StandingsSensor(coordinator, entry, league_id, table["division_id"]))

    async_add_entities(entities)


class StandingsSensor(CoordinatorEntity[LeagueStandingsCoordinator], SensorEntity):
    """One sensor per division (or one per league for flat leagues)."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:trophy"

    def __init__(
        self,
        coordinator: LeagueStandingsCoordinator,
        entry: ConfigEntry,
        league_id: str,
        division_id: str | None,
    ) -> None:
        super().__init__(coordinator)
        self._league_id = league_id
        self._division_id = division_id

        suffix = f"_{division_id}" if division_id else ""
        self._attr_unique_id = f"{entry.entry_id}_{league_id.lower()}{suffix}"
        self._attr_translation_key = "standings"

    @property
    def name(self) -> str:
        table = self._table()
        if not table:
            return self._league_id
        if table["division_id"]:
            return f"{self._league_id} - {table['division_name']}"
        return table["division_name"]

    @property
    def native_value(self) -> str | None:
        """Leader's abbreviation."""
        table = self._table()
        if not table or not table["teams"]:
            return None
        return table["teams"][0].get("abbr")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        table = self._table()
        if not table:
            return {}
        meta = LEAGUE_MAP.get(self._league_id, {})
        return {
            "league": self._league_id,
            "sport": meta.get("sport"),
            "league_path": meta.get("path"),
            "division_id": table["division_id"],
            "division_name": table["division_name"],
            "conference": table["conference"],
            "conference_abbr": table["conference_abbr"],
            "teams": table["teams"],
        }

    @callback
    def _table(self) -> dict[str, Any] | None:
        for t in self.coordinator.data or []:
            if t["division_id"] == self._division_id:
                return t
        return None
