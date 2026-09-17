# -*- coding: utf-8 -*-
"""Unit tests for BaZi calculate output alignment (0.2.0)."""
from __future__ import annotations

from datetime import date

from mystilink_bazi.calculate import compute_bazi


def test_pillar_has_ganzhi_indices_and_text() -> None:
    out = compute_bazi(date(1990, 5, 15), hour_interval=12, minute=0)
    day = out["pillars"]["day"]
    assert "stem_index" in day
    assert "branch_index" in day
    assert day["text"] == day["stem"] + day["branch"]
    assert day["ganzhi"] == day["text"]
    assert 0 <= day["stem_index"] <= 9
    assert 0 <= day["branch_index"] <= 11
    assert day["stem"] == ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"][day["stem_index"]]


def test_schema_version_and_calendar_engine() -> None:
    out = compute_bazi(date(1990, 5, 15), 12)
    assert out["schema_version"] == "mystilink.bazi.chart/0.1"
    assert out["bazi_schema_version"] == "1.0"
    assert out["calendar_engine"] == "builtin"


def test_birth_block_when_timezone_given() -> None:
    # Use a post-DST year so Asia/Shanghai offset is stably +08:00
    out = compute_bazi(
        date(1995, 5, 15),
        12,
        0,
        timezone="Asia/Shanghai",
    )
    assert out["birth"]["timezone"] == "Asia/Shanghai"
    assert out["birth"]["datetime"].startswith("1995-05-15T12:00:00")
    assert "+" in out["birth"]["datetime"] or out["birth"]["datetime"].endswith("Z")


def test_legacy_fields_still_present() -> None:
    out = compute_bazi(date(1990, 5, 15), 12)
    assert "birth_date" in out
    assert "bazi_ganzhi" in out
    assert "stem" in out["pillars"]["year"]
    assert "branch" in out["pillars"]["year"]
    assert "ganzhi" in out["pillars"]["year"]
