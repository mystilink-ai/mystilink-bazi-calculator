# -*- coding: utf-8 -*-
"""Parse mystilink.birth/0.1 BirthProfile JSON (no runtime schema package dependency)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class BirthProfileError(ValueError):
    """Invalid BirthProfile document."""


def parse_birth_profile(data: Dict[str, Any]) -> Tuple[date, int, int, Optional[str], Optional[float]]:
    """
    Return (civil_date, hour, minute, timezone, longitude).

    Accepts mystilink.birth/0.1. Longitude may come from birth.longitude or place.lon.
    """
    if not isinstance(data, dict):
        raise BirthProfileError("birth profile must be a JSON object")

    version = data.get("schema_version")
    if version is not None and version != "mystilink.birth/0.1":
        raise BirthProfileError(
            f"unsupported schema_version {version!r}; expected mystilink.birth/0.1"
        )

    birth = data.get("birth")
    if not isinstance(birth, dict):
        raise BirthProfileError("birth object is required")

    timezone = birth.get("timezone")
    if not timezone or not isinstance(timezone, str):
        raise BirthProfileError("birth.timezone is required (IANA name)")

    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise BirthProfileError(f"unknown IANA timezone: {timezone!r}") from exc

    dt_raw = birth.get("datetime")
    if not isinstance(dt_raw, str) or not dt_raw.strip():
        raise BirthProfileError("birth.datetime is required (ISO-8601 with offset)")

    try:
        # fromisoformat handles +08:00; replace Z
        normalized = dt_raw.strip().replace("Z", "+00:00")
        instant = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise BirthProfileError(f"invalid birth.datetime: {dt_raw!r}") from exc

    if instant.tzinfo is None:
        raise BirthProfileError("birth.datetime must include a timezone offset")

    # Use the ISO wall-clock fields as civil birth time in birth.timezone.
    # (Avoid re-folding through historical DST, which surprises form-style inputs.)
    civil = date(instant.year, instant.month, instant.day)
    hour = instant.hour
    minute = instant.minute

    longitude: Optional[float] = None
    if birth.get("longitude") is not None:
        try:
            longitude = float(birth["longitude"])
        except (TypeError, ValueError) as exc:
            raise BirthProfileError("birth.longitude must be a number") from exc
    else:
        place = data.get("place")
        if isinstance(place, dict) and place.get("lon") is not None:
            try:
                longitude = float(place["lon"])
            except (TypeError, ValueError) as exc:
                raise BirthProfileError("place.lon must be a number") from exc

    return civil, hour, minute, timezone, longitude
