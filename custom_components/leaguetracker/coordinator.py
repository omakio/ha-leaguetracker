"""DataUpdateCoordinator for League Tracker."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EspnStandingsError, fetch_standings, parse_standings
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class LeagueStandingsCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Polls ESPN once per league and fans out division data to sensors."""

    def __init__(
        self,
        hass: HomeAssistant,
        league_id: str,
        scan_interval: timedelta,
    ) -> None:
        self.league_id = league_id
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{league_id}",
            update_interval=scan_interval,
        )

    async def _async_update_data(self) -> list[dict[str, Any]]:
        try:
            raw = await fetch_standings(self.hass, self.league_id)
            return parse_standings(self.league_id, raw)
        except EspnStandingsError as err:
            raise UpdateFailed(str(err)) from err
