# -*- coding: utf-8 -*-
"""Tests for optional calendar engines."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from mystilink_bazi.calendar_engine import (
    CalendarEngineError,
    compute_bazi_from_calendar_basis,
    compute_bazi_with_lunar,
    lunar_available,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_external_basis_pillars() -> None:
    basis = json.loads((FIXTURES / "calendar.basis.v0.json").read_text(encoding="utf-8"))
    out = compute_bazi_from_calendar_basis(basis)
    assert out["calendar_engine"] == "external_basis"
    assert out["pillars"]["day"]["text"] == "丙寅"
    assert out["pillars"]["day"]["ganzhi"] == "丙寅"
    assert out["birth_date"] == "1990-05-15"
    assert out["effective_hour"] == 12
    assert out["calendar_basis"]["schema_version"] == "mystilink.calendar_basis/0.1"
    assert "ganzhi" in out["calendar_basis"]


def test_external_basis_missing_ganzhi() -> None:
    with pytest.raises(CalendarEngineError, match="ganzhi"):
        compute_bazi_from_calendar_basis(
            {
                "schema_version": "mystilink.calendar_basis/0.1",
                "solar": {
                    "datetime": "1990-05-15T12:00:00+08:00",
                    "timezone": "Asia/Shanghai",
                },
                "lunar": {"year": 1990, "month": 4, "day": 21, "is_leap_month": False},
            }
        )


@pytest.mark.skipif(not lunar_available(), reason="mystilink-lunar not installed")
def test_lunar_engine_requires_timezone_and_runs() -> None:
    out = compute_bazi_with_lunar(
        date(1990, 5, 15),
        12,
        0,
        timezone="Asia/Shanghai",
    )
    assert out["calendar_engine"] == "lunar"
    assert out["pillars"]["day"]["text"] == out["pillars"]["day"]["ganzhi"]
    assert "stem_index" in out["pillars"]["year"]
    assert out["calendar_basis"]["rules"]["year_boundary"] == "lichun_exact"
    assert "birth" in out
