# -*- coding: utf-8 -*-
"""BaZi DaYun (decade fortune) calculation."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from mystilink_bazi.calculate import (
    BRANCH_ELEMENTS,
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    MONTH_STEM_RULES,
    STEM_ELEMENTS,
    parse_date,
)

JIEQI_APPROXIMATE: List[tuple[int, int]] = [
    (2, 4),
    (3, 6),
    (4, 5),
    (5, 6),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 8),
    (10, 8),
    (11, 7),
    (12, 7),
    (1, 6),
]


def _jieqi_dates_for_year(year: int) -> List[date]:
    dates = []
    for month, day in JIEQI_APPROXIMATE:
        y = year if month >= 2 else year + 1
        dates.append(date(y, month, day))
    dates.sort()
    return dates


def compute_start_age(birth_date: date, forward: bool) -> tuple[int, int, int]:
    year = birth_date.year
    all_jieqi: List[date] = []
    for y in range(year - 1, year + 2):
        all_jieqi.extend(_jieqi_dates_for_year(y))
    all_jieqi.sort()

    if forward:
        target = None
        for jq in all_jieqi:
            if jq > birth_date:
                target = jq
                break
        if target is None:
            target = birth_date
        delta_days = (target - birth_date).days
    else:
        target = None
        for jq in reversed(all_jieqi):
            if jq <= birth_date:
                target = jq
                break
        if target is None:
            target = birth_date
        delta_days = (birth_date - target).days

    start_age = delta_days // 3
    remainder = delta_days % 3
    extra_months = remainder * 4
    return start_age, extra_months, delta_days


def compute_month_pillar(birth_date: date, year_stem: str) -> tuple[str, str]:
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

    branch_index = EARTHLY_BRANCHES.index(branch)
    month_index = (branch_index - 2) % 12
    stem = MONTH_STEM_RULES[year_stem][month_index]
    return stem, branch


def compute_year_pillar(birth_date: date) -> tuple[str, str]:
    year = birth_date.year
    if birth_date.month < 2 or (birth_date.month == 2 and birth_date.day < 4):
        year -= 1
    stem_index = (year - 4) % 10
    branch_index = (year - 4) % 12
    return HEAVENLY_STEMS[stem_index], EARTHLY_BRANCHES[branch_index]


def is_dayun_forward(year_stem: str, gender: str) -> bool:
    stem_idx = HEAVENLY_STEMS.index(year_stem)
    yang_stem = stem_idx % 2 == 0
    is_male = gender == "male"
    return yang_stem == is_male


def compute_dayun(
    birth_date: date,
    gender: str,
    count: int = 8,
) -> Dict[str, Any]:
    year_stem, year_branch = compute_year_pillar(birth_date)
    month_stem, month_branch = compute_month_pillar(birth_date, year_stem)

    forward = is_dayun_forward(year_stem, gender)
    start_age, extra_months, delta_days = compute_start_age(birth_date, forward)

    stem_idx = HEAVENLY_STEMS.index(month_stem)
    branch_idx = EARTHLY_BRANCHES.index(month_branch)

    dayun_list: List[Dict[str, Any]] = []
    for i in range(1, count + 1):
        step = i if forward else -i
        s = HEAVENLY_STEMS[(stem_idx + step) % 10]
        b = EARTHLY_BRANCHES[(branch_idx + step) % 12]
        lo = start_age + (i - 1) * 10
        hi = lo + 9
        dayun_list.append({
            "index": i,
            "stem": s,
            "branch": b,
            "ganzhi": s + b,
            "stem_element": STEM_ELEMENTS.get(s),
            "branch_element": BRANCH_ELEMENTS.get(b),
            "start_age": lo,
            "end_age": hi,
            "age_range": f"{lo}-{hi}",
        })

    direction_zh = "顺行" if forward else "逆行"
    start_desc = f"{start_age}岁"
    if extra_months > 0:
        start_desc += f"{extra_months}个月"

    summary_parts = [
        f"出生日期：{birth_date.isoformat()}，性别：{'男' if gender == 'male' else '女'}",
        f"年柱：{year_stem}{year_branch}，月柱：{month_stem}{month_branch}",
        f"大运方向：{direction_zh}，起运年龄：{start_desc}（距节气{delta_days}天）",
        "",
        "大运排列：",
    ]
    for d in dayun_list:
        summary_parts.append(
            f"  第{d['index']}步大运：{d['ganzhi']}（{d['age_range']}岁）"
        )

    return {
        "dayun_schema_version": "1.0",
        "birth_date": birth_date.isoformat(),
        "gender": gender,
        "year_pillar": {
            "stem": year_stem,
            "branch": year_branch,
            "ganzhi": year_stem + year_branch,
        },
        "month_pillar": {
            "stem": month_stem,
            "branch": month_branch,
            "ganzhi": month_stem + month_branch,
        },
        "direction": "forward" if forward else "reverse",
        "direction_zh": direction_zh,
        "start_age": start_age,
        "start_extra_months": extra_months,
        "delta_days_to_jieqi": delta_days,
        "dayun_list": dayun_list,
        "summary_zh": "\n".join(summary_parts),
    }


__all__ = ["compute_dayun", "parse_date"]
