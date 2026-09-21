# Mystilink BaZi Calculator

> Languages: [English](README.md) | [简体中文](docs/i18n/README.zh-CN.md) | [繁體中文](docs/i18n/README.zh-TW.md) | [日本語](docs/i18n/README.ja.md) | [한국어](docs/i18n/README.ko.md) | [Français](docs/i18n/README.fr.md) | [Español](docs/i18n/README.es.md)

## Overview

Compute Chinese BaZi (Four Pillars) charts, decade fortunes (DaYun), and annual fortunes (LiuNian). Results are structured JSON suitable for applications and scripts. Image or CDN assets are not included.

## Platforms and languages

| Target | Delivery |
|--------|----------|
| Python | Installable package `mystilink-bazi-calculator` and CLI `bazi` |
| JavaScript / Node | npm package under `bindings/js` (spawns CLI; browser via injectable `runCli`) |
| C | Header + library that invokes the CLI and returns JSON |
| C++ | Thin wrapper over the C API |
| C# | Process wrapper over the CLI |
| Java | ProcessBuilder wrapper over the CLI |

All non-Python bindings call the `bazi` executable on `PATH` (or `MYSTILINK_BAZI_CLI`). The long alias `mystilink-bazi` remains installed for compatibility.

## Requirements

- Python 3.9 or newer
- For language bindings: the CLI must be installed and available on `PATH`

## Install and quick start

```bash
# after obtaining the repository locally
cd mystilink-bazi-calculator
python3 -m pip install -e .
bazi calculate --date 1990-05-15 --hour 12

# optional lunar engine (Python 3.10+)
python3 -m pip install -e '.[lunar]'
bazi calculate --date 1990-05-15 --hour 12 --timezone Asia/Shanghai --calendar-engine lunar
```

Also:

```bash
python3 -m mystilink_bazi calculate --date 1990-05-15 --hour 12
```

## CLI

Always prints JSON to stdout on success.

```bash
bazi calculate --date YYYY-MM-DD [--hour N] [--minute N] [--timezone IANA] [--longitude N]
bazi calculate --birth-json path/or/-/inline.json
bazi calculate --calendar-basis path/or/-/basis.json
bazi calculate --date YYYY-MM-DD --hour N --timezone IANA --calendar-engine lunar
bazi dayun --date YYYY-MM-DD --gender male|female [--count N]
bazi liunian --year YYYY [--day-stem STEM] [--pillars-json JSON]
bazi version
```

### calculate

| Option | Description |
|--------|-------------|
| `--date` | Birth date `YYYY-MM-DD` (required unless `--birth-json` or `--calendar-basis`) |
| `--hour` | Birth hour `0-23` (default `11` if omitted) |
| `--minute` | Birth minute `0-59` (default `0`) |
| `--timezone` | IANA timezone (true solar time / lunar engine / optional `birth` block) |
| `--longitude` | Longitude in degrees, east positive |
| `--birth-json` | BirthProfile (`mystilink.birth/0.1`): file path, `-` (stdin), or inline JSON |
| `--calendar-engine` | `builtin` (default), `lunar` (optional extra), or `external_basis` |
| `--calendar-basis` | External calendar-basis / lunar convert JSON; does not import lunar |

True solar time applies only when both `--timezone` and `--longitude` are set (legacy CLI), or when BirthProfile sets `birth.true_solar_time` **and** timezone/longitude are available.

Each pillar includes `stem_index`, `branch_index`, `text`, plus legacy `stem` / `branch` / `ganzhi` (`ganzhi` equals `text`). Top-level `schema_version` is `mystilink.bazi.chart/0.1`; `bazi_schema_version` remains `1.0` for older consumers. `calendar_engine` reports `builtin`, `lunar`, or `external_basis`.

### dayun

| Option | Description |
|--------|-------------|
| `--date` | Birth date (required) |
| `--gender` | `male` or `female` (required) |
| `--count` | Number of decade periods (default `8`) |

### liunian

| Option | Description |
|--------|-------------|
| `--year` | Target solar year (required) |
| `--day-stem` | Day stem for ten-god (十神) labeling |
| `--pillars-json` | Original four pillars JSON for interaction hints |

## Python API

```python
from datetime import date
from mystilink_bazi import (
    compute_bazi,
    compute_bazi_from_calendar_basis,
    compute_bazi_with_lunar,
    compute_dayun,
    compute_liunian,
)

pillars = compute_bazi(date(1990, 5, 15), hour_interval=12, minute=0)
# optional: compute_bazi_with_lunar(..., timezone="Asia/Shanghai")
# optional: compute_bazi_from_calendar_basis(basis_dict)
dayun = compute_dayun(date(1990, 5, 15), "male", count=8)
liunian = compute_liunian(2024, day_stem=pillars["pillars"]["day"]["stem"])
```

## Compatibility

- Install alone: no hard dependency on `mystilink-lunar` or metaphysics-schema packages.
- Optional lunar: `pip install 'mystilink-bazi-calculator[lunar]'` (requires Python 3.10+).
- Orchestration without import: `mystilink-lunar convert ... --json` → `mystilink-bazi calculate --calendar-basis …`.
- Contract alignment: output fields match `mystilink.bazi.chart/0.1` / Ganzhi shapes; BirthProfile input matches `mystilink.birth/0.1` by field convention only.
- See [CHANGELOG.md](CHANGELOG.md).

## Examples

Runnable samples live under `examples/{c,cpp,csharp,java,js,node,python}/`. Binding sources live under `bindings/`.

Schemas for CLI JSON shapes are in `schema/`. Samples:

- BirthProfile: `tests/fixtures/birth.profile.v0.json`
- Calendar basis: `tests/fixtures/calendar.basis.v0.json`

```bash
bazi calculate --birth-json tests/fixtures/birth.profile.v0.json
bazi calculate --calendar-basis tests/fixtures/calendar.basis.v0.json
```


Optional `--envelope` wraps the result as `mystilink.envelope/0.1` (default remains bare JSON).

## Limits

- Solar-term dates for DaYun start-age use approximate civil calendar days, not ephemeris precision.
- True solar time uses Equation of Time plus longitude; accuracy depends on timezone and longitude inputs.
- This package does not ship fonts, images, or remote asset lookups.
- Built-in calendar rules are approximate; they are not a substitute for a dedicated lunar/ephemeris library.

## License

MIT. See [LICENSE](LICENSE).

## Feedback

Report defects with: CLI version (`mystilink-bazi version`), exact command line (use fictional dates only), and stderr/stdout JSON.
