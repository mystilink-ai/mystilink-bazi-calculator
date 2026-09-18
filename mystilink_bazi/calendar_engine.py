# -*- coding: utf-8 -*-
"""Optional calendar engines: builtin (default), lunar, external_basis."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional, Tuple

from mystilink_bazi.calculate import (
    assemble_bazi_chart,
    pillar_from_ganzhi_fields,
)


class CalendarEngineError(ValueError):
    """Invalid calendar engine selection or calendar-basis payload."""


LUNAR_MISSING_MSG = (
    "calendar_engine=lunar requires optional dependency mystilink-lunar. "
    "Install with: python3 -m pip install 'mystilink-bazi-calculator[lunar]' "
    "(Python 3.10+). Or pass --calendar-basis from mystilink-lunar convert JSON."
)


def lunar_available() -> bool:
    try:
        import mystilink_lunar  # noqa: F401
    except ImportError:
        return False
    return True


def _require_lunar() -> None:
    if not lunar_available():
        raise CalendarEngineError(LUNAR_MISSING_MSG)


def _basis_subset(data: Dict[str, Any]) -> Dict[str, Any]:
    """Keep a compact, JSON-serializable calendar_basis attachment."""
    keys = (
        "schema_version",
        "solar",
        "lunar",
        "ganzhi",
        "zodiac",
        "rules",
        "solar_term",
        "provider",
    )
    out = {k: data[k] for k in keys if k in data}
    if "schema_version" not in out and "ganzhi" in out and "solar" in out:
        out["schema_version"] = "mystilink.calendar_basis/0.1"
    return out


def compute_bazi_with_lunar(
    birth_date: date,
    hour: int,
    minute: int = 0,
    *,
    timezone: str,
    true_solar_enabled: bool = False,
    true_solar_delta_minutes: float = 0.0,
) -> Dict[str, Any]:
    """
    Compute pillars via mystilink-lunar with GanzhiRules.bazi_default().

    Requires the optional [lunar] extra. Timezone is mandatory.
    """
    _require_lunar()
    from mystilink_lunar import GanzhiRules, LunarCalendar

    hi = max(0, min(23, hour))
    mi = max(0, min(59, minute))
    cal = LunarCalendar.from_solar(
        birth_date.year,
        birth_date.month,
        birth_date.day,
        hi,
        mi,
        timezone=timezone,
        rules=GanzhiRules.bazi_default(),
    )
    pillars = cal.ganzhi()
    basis = cal.to_dict()
    basis["schema_version"] = "mystilink.calendar_basis/0.1"
    if "provider" in basis and isinstance(basis["provider"], str):
        if not basis["provider"].startswith("mystilink-lunar"):
            basis["provider"] = f"mystilink-lunar@{basis['provider']}"

    year_p = pillar_from_ganzhi_fields(pillars.year.to_dict())
    month_p = pillar_from_ganzhi_fields(pillars.month.to_dict())
    day_p = pillar_from_ganzhi_fields(pillars.day.to_dict())
    hour_p = pillar_from_ganzhi_fields(pillars.hour.to_dict())

    return assemble_bazi_chart(
        year_p,
        month_p,
        day_p,
        hour_p,
        birth_date,
        hi,
        mi,
        true_solar_enabled=true_solar_enabled,
        true_solar_delta_minutes=true_solar_delta_minutes,
        timezone=timezone,
        calendar_engine="lunar",
        calendar_basis=_basis_subset(basis),
    )


def _parse_solar_from_basis(
    basis: Dict[str, Any],
) -> Tuple[date, int, int, Optional[str]]:
    solar = basis.get("solar")
    if not isinstance(solar, dict):
        raise CalendarEngineError("calendar-basis.solar object is required")

    timezone = solar.get("timezone")
    if timezone is not None and not isinstance(timezone, str):
        raise CalendarEngineError("calendar-basis.solar.timezone must be a string")

    dt_raw = solar.get("datetime")
    if isinstance(dt_raw, str) and dt_raw.strip():
        normalized = dt_raw.strip().replace("Z", "+00:00")
        try:
            instant = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise CalendarEngineError(
                f"invalid calendar-basis.solar.datetime: {dt_raw!r}"
            ) from exc
        return date(instant.year, instant.month, instant.day), instant.hour, instant.minute, timezone

    year = solar.get("year")
    month = solar.get("month")
    day = solar.get("day")
    if year is None or month is None or day is None:
        raise CalendarEngineError(
            "calendar-basis.solar needs datetime or year/month/day"
        )
    return date(int(year), int(month), int(day)), 0, 0, timezone


def compute_bazi_from_calendar_basis(
    basis: Dict[str, Any],
    *,
    birth_date: Optional[date] = None,
    hour: Optional[int] = None,
    minute: Optional[int] = None,
    timezone: Optional[str] = None,
    true_solar_enabled: bool = False,
    true_solar_delta_minutes: float = 0.0,
) -> Dict[str, Any]:
    """
    Build a BaZi chart from an external calendar-basis / lunar convert JSON.

    Does not import mystilink-lunar. Requires basis['ganzhi'] with four pillars.
    """
    if not isinstance(basis, dict):
        raise CalendarEngineError("calendar-basis must be a JSON object")

    version = basis.get("schema_version")
    if version is not None and version != "mystilink.calendar_basis/0.1":
        # Forward-compatible: accept other versions only when ganzhi is present
        if not isinstance(basis.get("ganzhi"), dict):
            raise CalendarEngineError(
                f"unsupported calendar-basis schema_version: {version!r}"
            )

    ganzhi = basis.get("ganzhi")
    if not isinstance(ganzhi, dict):
        raise CalendarEngineError("calendar-basis.ganzhi with four pillars is required")

    for slot in ("year", "month", "day", "hour"):
        if slot not in ganzhi or not isinstance(ganzhi[slot], dict):
            raise CalendarEngineError(f"calendar-basis.ganzhi.{slot} is required")

    solar_date, solar_hour, solar_minute, solar_tz = _parse_solar_from_basis(basis)
    civil = birth_date if birth_date is not None else solar_date
    if hour is not None:
        hi = max(0, min(23, hour))
    elif birth_date is None:
        hi = solar_hour
    else:
        hi = 11
    if minute is not None:
        mi = max(0, min(59, minute))
    elif birth_date is None and hour is None:
        mi = solar_minute
    else:
        mi = 0
    tz = timezone or solar_tz

    year_p = pillar_from_ganzhi_fields(ganzhi["year"])
    month_p = pillar_from_ganzhi_fields(ganzhi["month"])
    day_p = pillar_from_ganzhi_fields(ganzhi["day"])
    hour_p = pillar_from_ganzhi_fields(ganzhi["hour"])

    return assemble_bazi_chart(
        year_p,
        month_p,
        day_p,
        hour_p,
        civil,
        hi,
        mi,
        true_solar_enabled=true_solar_enabled,
        true_solar_delta_minutes=true_solar_delta_minutes,
        timezone=tz,
        calendar_engine="external_basis",
        calendar_basis=_basis_subset(basis),
    )
