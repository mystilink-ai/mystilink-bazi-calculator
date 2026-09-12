# MystiLink BaZi Calculator

> Languages: [English](README.md) | [简体中文](README.zh-CN.md)

## Overview

Compute Chinese BaZi (Four Pillars) charts, decade fortunes (DaYun), and annual fortunes (LiuNian). Results are structured JSON suitable for applications and scripts. Image or CDN assets are not included.

## Platforms and languages

| Target | Delivery |
|--------|----------|
| Python | Installable package `mystilink-bazi-calculator` and CLI `mystilink-bazi` |
| JavaScript / Node | npm package under `bindings/js` (spawns CLI; browser via injectable `runCli`) |
| C | Header + library that invokes the CLI and returns JSON |
| C++ | Thin wrapper over the C API |
| C# | Process wrapper over the CLI |
| Java | ProcessBuilder wrapper over the CLI |

All non-Python bindings call the `mystilink-bazi` executable on `PATH` (or `MYSTILINK_BAZI_CLI`).

## Requirements

- Python 3.9 or newer
- For language bindings: the CLI must be installed and available on `PATH`

## Install and quick start

```bash
# after obtaining the repository locally
cd mystilink-bazi-calculator
python3 -m pip install -e .
mystilink-bazi calculate --date 1990-05-15 --hour 12
```

Also:

```bash
python3 -m mystilink_bazi calculate --date 1990-05-15 --hour 12
```

## CLI

Always prints JSON to stdout on success.

```bash
mystilink-bazi calculate --date YYYY-MM-DD [--hour N] [--minute N] [--timezone IANA] [--longitude N]
mystilink-bazi dayun --date YYYY-MM-DD --gender male|female [--count N]
mystilink-bazi liunian --year YYYY [--day-stem STEM] [--pillars-json JSON]
mystilink-bazi version
```

### calculate

| Option | Description |
|--------|-------------|
| `--date` | Birth date `YYYY-MM-DD` (required) |
| `--hour` | Birth hour `0-23` (default `11` if omitted) |
| `--minute` | Birth minute `0-59` (default `0`) |
| `--timezone` | IANA timezone for true solar time (e.g. `Asia/Shanghai`) |
| `--longitude` | Longitude in degrees, east positive |

True solar time applies only when both `--timezone` and `--longitude` are set.

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
from mystilink_bazi import compute_bazi, compute_dayun, compute_liunian

pillars = compute_bazi(date(1990, 5, 15), hour_interval=12, minute=0)
dayun = compute_dayun(date(1990, 5, 15), "male", count=8)
liunian = compute_liunian(2024, day_stem=pillars["pillars"]["day"]["stem"])
```

## Examples

Runnable samples live under `examples/{c,cpp,csharp,java,js,node,python}/`. Binding sources live under `bindings/`.

Schemas for CLI JSON shapes are in `schema/`.

## Limits

- Solar-term dates for DaYun start-age use approximate civil calendar days, not ephemeris precision.
- True solar time uses Equation of Time plus longitude; accuracy depends on timezone and longitude inputs.
- This package does not ship fonts, images, or remote asset lookups.

## License

MIT. See [LICENSE](LICENSE).

## Feedback

Report defects with: CLI version (`mystilink-bazi version`), exact command line (use fictional dates only), and stderr/stdout JSON.
