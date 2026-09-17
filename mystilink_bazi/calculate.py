# -*- coding: utf-8 -*-
"""BaZi four-pillar calculation. Returns structured JSON-ready dicts."""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

STEM_ELEMENTS = {
    "甲": "Wood", "乙": "Wood", "丙": "Fire", "丁": "Fire", "戊": "Earth", "己": "Earth",
    "庚": "Metal", "辛": "Metal", "壬": "Water", "癸": "Water",
}
BRANCH_ELEMENTS: Dict[str, str] = {
    "寅": "Wood", "卯": "Wood", "巳": "Fire", "午": "Fire",
    "辰": "Earth", "戌": "Earth", "丑": "Earth", "未": "Earth",
    "申": "Metal", "酉": "Metal", "亥": "Water", "子": "Water",
}
ZODIAC_ANIMALS = {
    "子": "Rat", "丑": "Ox", "寅": "Tiger", "卯": "Rabbit", "辰": "Dragon", "巳": "Snake",
    "午": "Horse", "未": "Goat", "申": "Monkey", "酉": "Rooster", "戌": "Dog", "亥": "Pig",
}

MONTH_STEM_RULES = {
    "甲": ["丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁"],
    "乙": ["戊", "己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"],
    "丙": ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛"],
    "丁": ["壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"],
    "戊": ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "甲", "乙"],
    "己": ["丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁"],
    "庚": ["戊", "己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"],
    "辛": ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛"],
    "壬": ["壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"],
    "癸": ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "甲", "乙"],
}

HOUR_STEM_RULES = {
    "甲": ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "甲", "乙"],
    "乙": ["丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁"],
    "丙": ["戊", "己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"],
    "丁": ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛"],
    "戊": ["壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"],
    "己": ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "甲", "乙"],
    "庚": ["丙", "丁", "戊", "己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁"],
    "辛": ["戊", "己", "庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"],
    "壬": ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛"],
    "癸": ["壬", "癸", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"],
}

STEM_PINYIN = {
    "甲": "jia", "乙": "yi", "丙": "bing", "丁": "ding", "戊": "wu", "己": "ji",
    "庚": "geng", "辛": "xin", "壬": "ren", "癸": "gui",
}
BRANCH_PINYIN = {
    "子": "zi", "丑": "chou", "寅": "yin", "卯": "mao", "辰": "chen", "巳": "si",
    "午": "wu", "未": "wei", "申": "shen", "酉": "you", "戌": "xu", "亥": "hai",
}


def stem_polarity(stem: str) -> str:
    i = _index_of(HEAVENLY_STEMS, stem)
    return "YANG" if i >= 0 and i % 2 == 0 else "YIN"


def branch_polarity(branch: str) -> str:
    i = _index_of(EARTHLY_BRANCHES, branch)
    return "YANG" if i >= 0 and i % 2 == 0 else "YIN"


def element_key_from_en(el: Optional[str]) -> str:
    if not el:
        return "earth"
    return {
        "Wood": "wood",
        "Fire": "fire",
        "Earth": "earth",
        "Metal": "metal",
        "Water": "water",
    }.get(el, "earth")


def build_bazi_grid_cells(
    stems_branches: List[str],
    slot_labels: List[str],
) -> List[Dict[str, Any]]:
    """Eight cells: year/month/day/hour stem then branch."""
    cells: List[Dict[str, Any]] = []
    for idx in range(8):
        ch = stems_branches[idx]
        is_stem = idx % 2 == 0
        kind = "stem" if is_stem else "branch"
        py_key = STEM_PINYIN.get(ch) if is_stem else BRANCH_PINYIN.get(ch)
        el_en = STEM_ELEMENTS.get(ch) if is_stem else BRANCH_ELEMENTS.get(ch)
        polarity = stem_polarity(ch) if is_stem else branch_polarity(ch)
        cells.append(
            {
                "index": idx,
                "row": 0 if is_stem else 1,
                "column": idx // 2,
                "slot": slot_labels[idx],
                "kind": kind,
                "char": ch,
                "pinyin": (py_key or "").upper(),
                "polarity": polarity,
                "element": el_en,
                "element_key": element_key_from_en(el_en),
            }
        )
    return cells


@dataclass
class Pillar:
    stem: str
    branch: str

    def to_dict(self) -> Dict[str, Any]:
        stem_index = _index_of(HEAVENLY_STEMS, self.stem)
        branch_index = _index_of(EARTHLY_BRANCHES, self.branch)
        text = self.stem + self.branch
        return {
            "stem_index": stem_index,
            "branch_index": branch_index,
            "stem": self.stem,
            "branch": self.branch,
            "text": text,
            "ganzhi": text,  # legacy alias of text
            "stem_element": STEM_ELEMENTS.get(self.stem),
            "branch_element": BRANCH_ELEMENTS.get(self.branch),
            "zodiac": ZODIAC_ANIMALS.get(self.branch),
        }


def _index_of(arr: List[str], value: str) -> int:
    try:
        return arr.index(value)
    except ValueError:
        return -1


def calculate_year_pillar(birth_date: date) -> Pillar:
    year, month, day = birth_date.year, birth_date.month, birth_date.day
    if month < 2 or (month == 2 and day < 4):
        year -= 1
    stem_index = (year - 4) % 10
    branch_index = (year - 4) % 12
    return Pillar(HEAVENLY_STEMS[stem_index], EARTHLY_BRANCHES[branch_index])


def calculate_month_pillar(birth_date: date, year_pillar: Pillar) -> Pillar:
    month, day = birth_date.month, birth_date.day
    if (month == 2 and day >= 4) or (month == 3 and day < 5):
        branch = "寅"
    elif (month == 3 and day >= 5) or (month == 4 and day < 5):
        branch = "卯"
    elif (month == 4 and day >= 5) or (month == 5 and day < 6):
        branch = "辰"
    elif (month == 5 and day >= 6) or (month == 6 and day < 6):
        branch = "巳"
    elif (month == 6 and day >= 6) or (month == 7 and day < 7):
        branch = "午"
    elif (month == 7 and day >= 7) or (month == 8 and day < 8):
        branch = "未"
    elif (month == 8 and day >= 8) or (month == 9 and day < 8):
        branch = "申"
    elif (month == 9 and day >= 8) or (month == 10 and day < 9):
        branch = "酉"
    elif (month == 10 and day >= 9) or (month == 11 and day < 8):
        branch = "戌"
    elif (month == 11 and day >= 8) or (month == 12 and day < 7):
        branch = "亥"
    elif (month == 12 and day >= 7) or (month == 1 and day < 6):
        branch = "子"
    else:
        branch = "丑"

    month_stems = MONTH_STEM_RULES[year_pillar.stem]
    branch_index = _index_of(EARTHLY_BRANCHES, branch)
    month_index = (branch_index - 2) % 12
    return Pillar(month_stems[month_index], branch)


def calculate_day_pillar(birth_date: date, hour: int) -> Pillar:
    d = birth_date
    if hour >= 23:
        d = d + timedelta(days=1)
    base_date = date(1900, 1, 31)
    days_diff = (d - base_date).days
    stem_index = (days_diff % 10 + 10) % 10
    branch_index = ((days_diff + 4) % 12 + 12) % 12
    return Pillar(HEAVENLY_STEMS[stem_index], EARTHLY_BRANCHES[branch_index])


def calculate_equation_of_time_minutes(local_dt: datetime) -> float:
    """Equation of Time: apparent vs mean solar time (minutes)."""
    day_of_year = local_dt.timetuple().tm_yday
    hour_fraction = local_dt.hour + local_dt.minute / 60.0 + local_dt.second / 3600.0
    gamma = 2.0 * math.pi / 365.0 * (day_of_year - 1 + (hour_fraction - 12.0) / 24.0)
    return 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2.0 * gamma)
        - 0.040849 * math.sin(2.0 * gamma)
    )


def apply_true_solar_time(local_dt: datetime, longitude: float) -> tuple[datetime, float]:
    """Correct local clock time to true solar time using longitude and Equation of Time."""
    utc_offset = local_dt.utcoffset()
    if utc_offset is None:
        raise ValueError("Timezone-aware datetime is required to compute true solar time.")
    tz_offset_hours = utc_offset.total_seconds() / 3600.0
    eq_time = calculate_equation_of_time_minutes(local_dt)
    delta_minutes = eq_time + 4.0 * longitude - 60.0 * tz_offset_hours
    adjusted = local_dt + timedelta(minutes=delta_minutes)
    return adjusted, delta_minutes


def hour_minute_to_shichen(hour: int, minute: int = 0) -> int:
    """Convert hour:minute to 时辰 index (0=子 .. 11=亥)."""
    total = hour * 60 + minute
    return ((total + 60) % 1440) // 120


def compute_bazi(
    birth_date: date,
    hour_interval: int,
    minute: int = 0,
    *,
    true_solar_enabled: bool = False,
    true_solar_delta_minutes: float = 0.0,
    timezone: Optional[str] = None,
    calendar_engine: str = "builtin",
) -> Dict[str, Any]:
    """Compute four pillars from (possibly true-solar-corrected) date/hour/minute."""
    hi = hour_interval
    if hi < 0 or hi > 23:
        hi = 11
    mi = max(0, min(59, minute))

    year_p = calculate_year_pillar(birth_date)
    month_p = calculate_month_pillar(birth_date, year_p)
    day_p = calculate_day_pillar(birth_date, hi)

    shichen_index = hour_minute_to_shichen(hi, mi)
    shichen_branch = EARTHLY_BRANCHES[shichen_index]
    hour_stems = HOUR_STEM_RULES[day_p.stem]
    hour_p = Pillar(hour_stems[shichen_index], shichen_branch)

    ganzhi_line = (
        f"{year_p.stem}{year_p.branch} {month_p.stem}{month_p.branch} "
        f"{day_p.stem}{day_p.branch} {hour_p.stem}{hour_p.branch}"
    )

    time_desc = f"{hi:02d}:{mi:02d}"
    summary_parts = [
        f"出生日期：{birth_date.isoformat()}，时间：{time_desc}",
    ]
    if true_solar_enabled:
        summary_parts.append(f"（真太阳时修正 {true_solar_delta_minutes:+.1f} 分钟）")
    summary_parts.append(
        f"\n四柱：{ganzhi_line}\n"
        f"年柱：{year_p.stem}{year_p.branch}（干五行 {STEM_ELEMENTS.get(year_p.stem)}，"
        f"生肖 {ZODIAC_ANIMALS.get(year_p.branch)}）\n"
        f"月柱：{month_p.stem}{month_p.branch}\n"
        f"日柱：{day_p.stem}{day_p.branch}\n"
        f"时柱：{hour_p.stem}{hour_p.branch}"
    )

    slot_labels = ["年干", "年支", "月干", "月支", "日干", "日支", "时干", "时支"]
    stems_branches = [
        year_p.stem, year_p.branch,
        month_p.stem, month_p.branch,
        day_p.stem, day_p.branch,
        hour_p.stem, hour_p.branch,
    ]

    out: Dict[str, Any] = {
        "schema_version": "mystilink.bazi.chart/0.1",
        "bazi_schema_version": "1.0",  # legacy
        "calendar_engine": calendar_engine,
        "birth_date": birth_date.isoformat(),
        "hour_interval": hi,
        "effective_hour": hi,
        "effective_minute": mi,
        "true_solar_time_enabled": true_solar_enabled,
        "true_solar_time_delta_minutes": round(true_solar_delta_minutes, 2),
        "pillars": {
            "year": year_p.to_dict(),
            "month": month_p.to_dict(),
            "day": day_p.to_dict(),
            "hour": hour_p.to_dict(),
        },
        "bazi_ganzhi": ganzhi_line,
        "summary_zh": "".join(summary_parts),
        "bazi_grid_cells": build_bazi_grid_cells(stems_branches, slot_labels),
        "bazi_details": [
            {"item": "八字年柱-天干", "value": year_p.stem},
            {"item": "八字年柱-地支", "value": year_p.branch},
            {"item": "八字月柱-天干", "value": month_p.stem},
            {"item": "八字月柱-地支", "value": month_p.branch},
            {"item": "八字日柱-天干", "value": day_p.stem},
            {"item": "八字日柱-地支", "value": day_p.branch},
            {"item": "八字时柱-天干", "value": hour_p.stem},
            {"item": "八字时柱-地支", "value": hour_p.branch},
        ],
    }
    if timezone:
        out["birth"] = {
            "datetime": (
                f"{birth_date.isoformat()}T{hi:02d}:{mi:02d}:00"
            ),
            "timezone": timezone,
        }
        # Prefer offset-aware ISO when timezone is known
        try:
            local = datetime(
                birth_date.year,
                birth_date.month,
                birth_date.day,
                hi,
                mi,
                tzinfo=ZoneInfo(timezone),
            )
            out["birth"]["datetime"] = local.isoformat()
        except Exception:
            pass
    return out


def resolve_birth_datetime(
    birth: date,
    hour: int,
    minute: int,
    timezone_name: Optional[str] = None,
    longitude: Optional[float] = None,
) -> tuple[date, int, int, bool, float]:
    """Optionally apply true solar time; return (date, hour, minute, enabled, delta)."""
    hi = max(0, min(23, hour))
    mi = max(0, min(59, minute))
    if timezone_name is None or longitude is None:
        return birth, hi, mi, False, 0.0
    tz = ZoneInfo(timezone_name)
    local_dt = datetime(birth.year, birth.month, birth.day, hi, mi, tzinfo=tz)
    corrected_dt, delta = apply_true_solar_time(local_dt, longitude)
    return corrected_dt.date(), corrected_dt.hour, corrected_dt.minute, True, delta


def parse_date(s: str) -> date:
    parts = s.strip().replace("/", "-").split("-")
    if len(parts) != 3:
        raise ValueError("date must be YYYY-MM-DD")
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    return date(y, m, d)
