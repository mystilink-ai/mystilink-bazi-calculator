# -*- coding: utf-8 -*-
"""CLI smoke tests for calculate and --birth-json."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "mystilink_bazi", *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_calculate_legacy() -> None:
    proc = _run("calculate", "--date", "1990-05-15", "--hour", "12")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["schema_version"] == "mystilink.bazi.chart/0.1"
    assert data["pillars"]["day"]["text"] == data["pillars"]["day"]["ganzhi"]
    assert "stem_index" in data["pillars"]["year"]


def test_cli_birth_json_file() -> None:
    path = FIXTURES / "birth.profile.v0.json"
    proc = _run("calculate", "--birth-json", str(path))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["birth_date"] == "1990-05-15"
    assert data["effective_hour"] == 12
    assert data["birth"]["timezone"] == "Asia/Shanghai"
    assert data["calendar_engine"] == "builtin"


def test_cli_birth_json_stdin() -> None:
    payload = (FIXTURES / "birth.profile.v0.json").read_text(encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-m", "mystilink_bazi", "calculate", "--birth-json", "-"],
        cwd=str(ROOT),
        input=payload,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["pillars"]["day"]["stem_index"] >= 0


def test_cli_version() -> None:
    proc = _run("version")
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["version"] == "0.2.3"
    assert data["cli"] == "bazi"


def test_cli_calendar_basis() -> None:
    path = FIXTURES / "calendar.basis.v0.json"
    proc = _run("calculate", "--calendar-basis", str(path))
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["calendar_engine"] == "external_basis"
    assert data["pillars"]["year"]["text"] == "庚午"


def test_cli_lunar_missing_or_runs() -> None:
    from mystilink_bazi.calendar_engine import lunar_available

    proc = _run(
        "calculate",
        "--date",
        "1990-05-15",
        "--hour",
        "12",
        "--timezone",
        "Asia/Shanghai",
        "--calendar-engine",
        "lunar",
    )
    if lunar_available():
        assert proc.returncode == 0, proc.stderr
        data = json.loads(proc.stdout)
        assert data["calendar_engine"] == "lunar"
        assert "calendar_basis" in data
    else:
        assert proc.returncode != 0
        err = json.loads(proc.stderr)
        assert "mystilink-lunar" in err["error"]
