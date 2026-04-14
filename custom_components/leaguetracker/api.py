"""ESPN standings API client."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import HomeAssistant

from .const import (
    DEFAULT_TIMEOUT,
    ESPN_API_BASE,
    LEAGUE_MAP,
    STAT_NAME_MAP,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


class EspnStandingsError(Exception):
    """Raised when the ESPN standings fetch fails."""


async def fetch_standings(hass: HomeAssistant, league_id: str) -> dict[str, Any]:
    """Fetch raw standings JSON for a league from ESPN.

    Returns the ESPN response dict unchanged. Use `parse_standings` to normalize.
    """
    meta = LEAGUE_MAP.get(league_id)
    if meta is None:
        raise EspnStandingsError(f"Unknown league_id: {league_id}")

    url = f"{ESPN_API_BASE}/{meta['sport']}/{meta['path']}/standings"
    params = {"level": "3"} if meta["divisions"] else {}
    headers = {"User-Agent": USER_AGENT}

    session = async_get_clientsession(hass)
    try:
        async with session.get(
            url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT
        ) as resp:
            resp.raise_for_status()
            return await resp.json()
    except Exception as err:
        raise EspnStandingsError(f"ESPN fetch failed for {league_id}: {err}") from err


def parse_standings(league_id: str, raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten ESPN's standings response into a list of division/league tables.

    Returns a list of dicts, one per division (divisional leagues) or one total
    (flat leagues). Each dict has: division_id, division_name, conference, teams[].
    """
    meta = LEAGUE_MAP[league_id]
    results: list[dict[str, Any]] = []

    if meta["divisions"]:
        for conf in raw.get("children", []):
            conf_name = conf.get("name", "")
            conf_abbr = conf.get("abbreviation", "")
            for div in conf.get("children", []):
                div_name = div.get("name", "")
                div_id = _slugify(f"{conf_abbr}_{div_name}")
                entries = (div.get("standings") or {}).get("entries", [])
                results.append(
                    {
                        "division_id": div_id,
                        "division_name": div_name,
                        "conference": conf_name,
                        "conference_abbr": conf_abbr,
                        "teams": [_parse_entry(e, i + 1) for i, e in enumerate(entries)],
                    }
                )
    else:
        entries = (raw.get("children", [{}])[0].get("standings") or {}).get("entries", [])
        results.append(
            {
                "division_id": None,
                "division_name": raw.get("name", league_id),
                "conference": None,
                "conference_abbr": None,
                "teams": [_parse_entry(e, i + 1) for i, e in enumerate(entries)],
            }
        )

    return results


def _parse_entry(entry: dict[str, Any], fallback_rank: int) -> dict[str, Any]:
    """Convert a single ESPN standings entry to our normalized shape."""
    team = entry.get("team", {})
    logos = team.get("logos") or []
    logo = logos[0].get("href") if logos else None

    stats: dict[str, Any] = {}
    for stat in entry.get("stats", []):
        key = STAT_NAME_MAP.get(stat.get("name", ""))
        if key is None:
            continue
        value = stat.get("value")
        if value is None:
            value = stat.get("displayValue")
        stats[key] = value

    return {
        "rank": int(stats.get("rank") or fallback_rank),
        "abbr": team.get("abbreviation"),
        "name": team.get("displayName"),
        "short_name": team.get("shortDisplayName"),
        "logo": logo,
        **{k: v for k, v in stats.items() if k != "rank"},
    }


def _slugify(value: str) -> str:
    return (
        value.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "")
        .replace("'", "")
    )
