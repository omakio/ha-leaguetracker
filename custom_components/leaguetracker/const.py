"""Constants for the League Tracker integration.

Inspired by ha-teamtracker by @vasqued2 (https://github.com/vasqued2/ha-teamtracker).
League ID vocabulary mirrors teamtracker so users familiar with that integration
find configuration here intuitive.
"""
from datetime import timedelta
from homeassistant.const import Platform

DOMAIN = "leaguetracker"
PLATFORMS = [Platform.SENSOR]

# API
ESPN_API_BASE = "https://site.api.espn.com/apis/v2/sports"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/15.0 Safari/605.1.15"
)
DEFAULT_TIMEOUT = 30

# Polling
DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)
MIN_SCAN_INTERVAL = timedelta(minutes=5)

# Config keys
CONF_LEAGUE_ID = "league_id"
CONF_DIVISION_ID = "division_id"
CONF_NAME = "name"
CONF_SCAN_INTERVAL = "scan_interval"

# Sports
FOOTBALL = "football"
BASKETBALL = "basketball"
BASEBALL = "baseball"
HOCKEY = "hockey"
SOCCER = "soccer"

# League map — (sport_path, league_path, has_divisions)
# Has_divisions=True: use ?level=3, create one sensor per division
# Has_divisions=False: flat table, single sensor per league
LEAGUE_MAP = {
    "NFL":    {"sport": FOOTBALL,   "path": "nfl",                      "divisions": True},
    "NBA":    {"sport": BASKETBALL, "path": "nba",                      "divisions": True},
    "WNBA":   {"sport": BASKETBALL, "path": "wnba",                     "divisions": True},
    "MLB":    {"sport": BASEBALL,   "path": "mlb",                      "divisions": True},
    "NHL":    {"sport": HOCKEY,     "path": "nhl",                      "divisions": True},
    "NCAAF":  {"sport": FOOTBALL,   "path": "college-football",         "divisions": True},
    "NCAAM":  {"sport": BASKETBALL, "path": "mens-college-basketball",  "divisions": True},
    "NCAAW":  {"sport": BASKETBALL, "path": "womens-college-basketball","divisions": True},
    "MLS":    {"sport": SOCCER,     "path": "usa.1",                    "divisions": False},
    "EPL":    {"sport": SOCCER,     "path": "eng.1",                    "divisions": False},
    "LALIGA": {"sport": SOCCER,     "path": "esp.1",                    "divisions": False},
    "BUNDES": {"sport": SOCCER,     "path": "ger.1",                    "divisions": False},
    "SERIEA": {"sport": SOCCER,     "path": "ita.1",                    "divisions": False},
    "LIGUE1": {"sport": SOCCER,     "path": "fra.1",                    "divisions": False},
    "UCL":    {"sport": SOCCER,     "path": "uefa.champions",           "divisions": False},
    "UEL":    {"sport": SOCCER,     "path": "uefa.europa",              "divisions": False},
}

# Stat name normalization — ESPN stat names → our clean attribute keys
STAT_NAME_MAP = {
    "wins": "wins",
    "losses": "losses",
    "ties": "ties",
    "winPercent": "pct",
    "gamesBehind": "games_behind",
    "gamesPlayed": "games_played",
    "streak": "streak",
    "pointsFor": "points_for",
    "pointsAgainst": "points_against",
    "differential": "differential",
    "pointDifferential": "point_differential",
    "points": "points",
    "clincher": "clinched",
    "playoffSeed": "playoff_seed",
    "rank": "rank",
}
