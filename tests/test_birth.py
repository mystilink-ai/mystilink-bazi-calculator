# -*- coding: utf-8 -*-
"""Tests for BirthProfile parsing."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from mystilink_bazi.birth import BirthProfileError, parse_birth_profile


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_minimal_birth_profile() -> None:
    data = {
        "schema_version": "mystilink.birth/0.1",
        "birth": {
            "datetime": "1990-05-15T14:30:00+08:00",
            "timezone": "Asia/Shanghai",
        },
    }
    civil, hour, minute, tz, lon = parse_birth_profile(data)
    assert civil.isoformat() == "1990-05-15"
    assert hour == 14
    assert minute == 30
    assert tz == "Asia/Shanghai"
    assert lon is None


def test_parse_fixture_with_longitude() -> None:
    data = json.loads((FIXTURES / "birth.profile.v0.json").read_text(encoding="utf-8"))
    civil, hour, minute, tz, lon = parse_birth_profile(data)
    assert civil.isoformat() == "1990-05-15"
    assert hour == 12
    assert minute == 0
    assert tz == "Asia/Shanghai"
    assert lon == pytest.approx(121.47)


def test_longitude_from_place() -> None:
    data = {
        "schema_version": "mystilink.birth/0.1",
        "birth": {
            "datetime": "1990-05-15T12:00:00+08:00",
            "timezone": "Asia/Shanghai",
        },
        "place": {"lon": 120.5},
    }
    _, _, _, _, lon = parse_birth_profile(data)
    assert lon == pytest.approx(120.5)


def test_rejects_wrong_schema_version() -> None:
    with pytest.raises(BirthProfileError, match="unsupported schema_version"):
        parse_birth_profile(
            {
                "schema_version": "mystilink.birth/9.9",
                "birth": {
                    "datetime": "1990-05-15T12:00:00+08:00",
                    "timezone": "Asia/Shanghai",
                },
            }
        )


def test_rejects_naive_datetime() -> None:
    with pytest.raises(BirthProfileError, match="timezone offset"):
        parse_birth_profile(
            {
                "schema_version": "mystilink.birth/0.1",
                "birth": {
                    "datetime": "1990-05-15T12:00:00",
                    "timezone": "Asia/Shanghai",
                },
            }
        )
