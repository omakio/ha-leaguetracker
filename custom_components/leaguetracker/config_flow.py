"""Config flow for League Tracker."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .api import EspnStandingsError, fetch_standings, parse_standings
from .const import (
    CONF_DIVISION_ID,
    CONF_LEAGUE_ID,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LEAGUE_MAP,
    MIN_SCAN_INTERVAL,
)


class LeagueTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._league_id: str | None = None
        self._divisions: list[dict[str, Any]] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            league_id = user_input[CONF_LEAGUE_ID]
            try:
                raw = await fetch_standings(self.hass, league_id)
                tables = parse_standings(league_id, raw)
            except EspnStandingsError:
                errors["base"] = "cannot_connect"
            else:
                self._league_id = league_id
                meta = LEAGUE_MAP[league_id]
                if meta["divisions"]:
                    self._divisions = tables
                    return await self.async_step_division()
                return self._create_entry(league_id, None, tables[0]["division_name"])

        schema = vol.Schema({vol.Required(CONF_LEAGUE_ID): vol.In(sorted(LEAGUE_MAP.keys()))})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_division(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        assert self._league_id is not None

        if user_input is not None:
            div_id = user_input[CONF_DIVISION_ID] or None
            div_name = next(
                (t["division_name"] for t in self._divisions if t["division_id"] == div_id),
                self._league_id,
            )
            name = f"{self._league_id}" if div_id is None else f"{self._league_id} - {div_name}"
            return self._create_entry(self._league_id, div_id, name)

        choices = {"": "All divisions"}
        for t in self._divisions:
            choices[t["division_id"]] = f"{t['conference_abbr']} {t['division_name']}"

        schema = vol.Schema({vol.Required(CONF_DIVISION_ID, default=""): vol.In(choices)})
        return self.async_show_form(step_id="division", data_schema=schema)

    def _create_entry(
        self, league_id: str, division_id: str | None, title: str
    ) -> FlowResult:
        unique_id = f"{league_id}_{division_id or 'all'}"
        self._abort_if_unique_id_configured = unique_id
        return self.async_create_entry(
            title=title,
            data={
                CONF_LEAGUE_ID: league_id,
                CONF_DIVISION_ID: division_id,
                CONF_NAME: title,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return LeagueTrackerOptionsFlow(config_entry)


class LeagueTrackerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            minutes = max(
                int(user_input[CONF_SCAN_INTERVAL]), int(MIN_SCAN_INTERVAL.total_seconds() / 60)
            )
            return self.async_create_entry(title="", data={CONF_SCAN_INTERVAL: minutes * 60})

        current_seconds = self.entry.options.get(
            CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds())
        )
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=int(current_seconds / 60),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=1440)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
