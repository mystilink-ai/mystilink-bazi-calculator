# -*- coding: utf-8 -*-
"""Validate compute_bazi output against shared mystilink-metaphysics-schema when present."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from mystilink_bazi.calculate import compute_bazi

SCHEMA_ROOT = (
    Path(__file__).resolve().parents[2] / "mystilink-metaphysics-schema" / "schemas" / "v0"
)


def _shared_available() -> bool:
    return (SCHEMA_ROOT / "systems" / "bazi.chart.schema.json").is_file()


@pytest.mark.skipif(not _shared_available(), reason="sibling mystilink-metaphysics-schema not present")
def test_compute_bazi_validates_shared_chart_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    referencing = pytest.importorskip("referencing")
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012

    registry = Registry()
    for path in SCHEMA_ROOT.rglob("*.schema.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        registry = registry.with_resource(
            data["$id"],
            Resource.from_contents(data, default_specification=DRAFT202012),
        )
    schema = json.loads(
        (SCHEMA_ROOT / "systems" / "bazi.chart.schema.json").read_text(encoding="utf-8")
    )
    out = compute_bazi(date(1990, 5, 15), hour_interval=12, minute=0, timezone="Asia/Shanghai")
    Draft202012Validator(schema, registry=registry).validate(out)


def test_day_master_matches_day_pillar() -> None:
    out = compute_bazi(date(1990, 5, 15), 12)
    assert "day_master" in out
    assert out["day_master"] == out["pillars"]["day"]
