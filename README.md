# League Tracker for Home Assistant

A Home Assistant custom integration that creates sensors for **league standings** — division tables for NFL/NBA/MLB/NHL, and flat league tables for EPL, MLS, La Liga, and others.

Data is pulled from ESPN's public standings API. One poll per league returns data for all divisions in that league, so tracking all 8 NFL divisions costs the same as tracking one.

> **Note:** This integration provides the *data*. In phase 1, display it with Home Assistant's built-in [markdown card](https://www.home-assistant.io/dashboards/markdown/) or [entities card](https://www.home-assistant.io/dashboards/entities/). A companion custom Lovelace card ([`ha-leaguetracker-card`](https://github.com/omakio/ha-leaguetracker-card)) is planned for phase 2.

## Supported leagues

| League | ID | Structure |
|---|---|---|
| NFL | `NFL` | 8 divisions |
| NBA | `NBA` | 6 divisions |
| WNBA | `WNBA` | 2 conferences |
| MLB | `MLB` | 6 divisions |
| NHL | `NHL` | 4 divisions |
| NCAA Football | `NCAAF` | conferences |
| NCAA Men's Basketball | `NCAAM` | conferences |
| NCAA Women's Basketball | `NCAAW` | conferences |
| MLS | `MLS` | flat table |
| English Premier League | `EPL` | flat table |
| La Liga | `LALIGA` | flat table |
| Bundesliga | `BUNDES` | flat table |
| Serie A | `SERIEA` | flat table |
| Ligue 1 | `LIGUE1` | flat table |
| UEFA Champions League | `UCL` | flat table |
| UEFA Europa League | `UEL` | flat table |

## Installation

### HACS (recommended)

1. HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/omakio/ha-leaguetracker`, category **Integration**
3. Install **League Tracker**
4. Restart Home Assistant
5. Settings → Devices & Services → **+ Add Integration** → **League Tracker**

### Manual

Copy `custom_components/leaguetracker/` into your Home Assistant `config/custom_components/` directory, restart, then add via the UI as above.

## Setup

The integration is UI-configured. For each league/division you want to track, add the integration again:

1. **Settings → Devices & Services → Add Integration → League Tracker**
2. Pick a league (e.g. NFL)
3. For leagues with divisions: pick a specific division, or "All divisions" to create one sensor per division in one go
4. Done — sensors appear immediately

### Update interval

Default: **30 minutes**. Change it per-entry: Integration tile → **Configure** → Update interval (minutes). Minimum 5 minutes.

## Entity shape

### Divisional league (NFL example)

```yaml
entity: sensor.nfl_nfc_east
state: "DAL"
attributes:
  league: "NFL"
  sport: "football"
  division_id: "nfc_east"
  division_name: "NFC East"
  conference: "National Football Conference"
  conference_abbr: "NFC"
  teams:
    - rank: 1
      abbr: "DAL"
      name: "Dallas Cowboys"
      logo: "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png"
      wins: 12
      losses: 5
      ties: 0
      pct: 0.706
      games_behind: 0
      streak: "W3"
      points_for: 490
      points_against: 320
      differential: "+170"
    - rank: 2, ...
```

### Flat league (EPL example)

```yaml
entity: sensor.premier_league
state: "Arsenal"
attributes:
  league: "EPL"
  sport: "soccer"
  teams:
    - rank: 1
      abbr: "ARS"
      name: "Arsenal"
      games_played: 32
      wins: 21
      ties: 7
      losses: 4
      points: 70
    - rank: 2, ...
```

## Dashboard usage (phase 1)

Until the companion card ships, use a markdown card:

```yaml
type: markdown
title: NFC East
content: |
  {% for t in state_attr('sensor.nfl_nfc_east', 'teams')[:5] %}
  {{ loop.index }}. **{{ t.abbr }}** — {{ t.wins }}-{{ t.losses }} ({{ t.streak }})
  {% endfor %}
```

## Credits & inspiration

- [**ha-teamtracker**](https://github.com/vasqued2/ha-teamtracker) by [@vasqued2](https://github.com/vasqued2) — this integration mirrors its config vocabulary (league IDs, HACS conventions, architectural pattern) so users familiar with teamtracker find it intuitive.

## Related projects

- [**ha-teamtracker**](https://github.com/vasqued2/ha-teamtracker) — per-team live game data (scores, quarter, play-by-play). Pairs well with this integration.

## License

MIT
