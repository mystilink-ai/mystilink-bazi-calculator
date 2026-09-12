# -*- coding: utf-8 -*-
"""BaZi LiuNian (annual fortune) calculation."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from mystilink_bazi.calculate import (
    BRANCH_ELEMENTS,
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    STEM_ELEMENTS,
)

SHISHEN_TABLE = {
    ("same", "same_polarity"): "比肩",
    ("same", "diff_polarity"): "劫财",
    ("i_generate", "same_polarity"): "食神",
    ("i_generate", "diff_polarity"): "伤官",
    ("i_am_generated", "same_polarity"): "偏印",
    ("i_am_generated", "diff_polarity"): "正印",
    ("i_ke", "same_polarity"): "偏财",
    ("i_ke", "diff_polarity"): "正财",
    ("ke_me", "same_polarity"): "七杀",
    ("ke_me", "diff_polarity"): "正官",
}

WUXING_ORDER = ["Wood", "Fire", "Earth", "Metal", "Water"]

DIZHI_CHONG = {
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}
DIZHI_HE = {
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午",
}
TIANGAN_HE = {
    "甲": "己", "己": "甲", "乙": "庚", "庚": "乙",
    "丙": "辛", "辛": "丙", "丁": "壬", "壬": "丁",
    "戊": "癸", "癸": "戊",
}
TIANGAN_CHONG = {
    "甲": "庚", "庚": "甲", "乙": "辛", "辛": "乙",
    "丙": "壬", "壬": "丙", "丁": "癸", "癸": "丁",
}


def _wuxing_relation(me: str, target: str) -> str:
    if me == target:
        return "same"
    mi = WUXING_ORDER.index(me)
    ti = WUXING_ORDER.index(target)
    if (mi + 1) % 5 == ti:
        return "i_generate"
    if (ti + 1) % 5 == mi:
        return "i_am_generated"
    if (mi + 2) % 5 == ti:
        return "i_ke"
    return "ke_me"


def _polarity(stem: str) -> str:
    return "yang" if HEAVENLY_STEMS.index(stem) % 2 == 0 else "yin"


def compute_shishen(day_stem: str, target_stem: str) -> str:
    me_el = STEM_ELEMENTS[day_stem]
    tgt_el = STEM_ELEMENTS[target_stem]
    relation = _wuxing_relation(me_el, tgt_el)
    same_pol = "same_polarity" if _polarity(day_stem) == _polarity(target_stem) else "diff_polarity"
    return SHISHEN_TABLE.get((relation, same_pol), "未知")


def compute_liunian_year(target_year: int) -> tuple[str, str]:
    stem_idx = (target_year - 4) % 10
    branch_idx = (target_year - 4) % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def compute_interactions(
    ln_stem: str,
    ln_branch: str,
    pillars: Optional[Dict[str, Dict[str, str]]],
) -> List[Dict[str, str]]:
    if not pillars:
        return []
    interactions: List[Dict[str, str]] = []
    pillar_names = {"year": "年柱", "month": "月柱", "day": "日柱", "hour": "时柱"}
    for key, label in pillar_names.items():
        p = pillars.get(key)
        if not p:
            continue
        p_stem = p.get("stem", "")
        p_branch = p.get("branch", "")
        if TIANGAN_HE.get(ln_stem) == p_stem:
            interactions.append({"type": "天干合", "detail": f"流年{ln_stem}合{label}{p_stem}"})
        if TIANGAN_CHONG.get(ln_stem) == p_stem:
            interactions.append({"type": "天干冲", "detail": f"流年{ln_stem}冲{label}{p_stem}"})
        if DIZHI_CHONG.get(ln_branch) == p_branch:
            interactions.append({"type": "地支冲", "detail": f"流年{ln_branch}冲{label}{p_branch}"})
        if DIZHI_HE.get(ln_branch) == p_branch:
            interactions.append({"type": "地支合", "detail": f"流年{ln_branch}合{label}{p_branch}"})
    return interactions


def compute_liunian(
    target_year: int,
    day_stem: Optional[str] = None,
    pillars: Optional[Dict[str, Dict[str, str]]] = None,
) -> Dict[str, Any]:
    ln_stem, ln_branch = compute_liunian_year(target_year)

    result: Dict[str, Any] = {
        "liunian_schema_version": "1.0",
        "target_year": target_year,
        "stem": ln_stem,
        "branch": ln_branch,
        "ganzhi": ln_stem + ln_branch,
        "stem_element": STEM_ELEMENTS.get(ln_stem),
        "branch_element": BRANCH_ELEMENTS.get(ln_branch),
    }

    if day_stem:
        shishen = compute_shishen(day_stem, ln_stem)
        result["shishen"] = shishen
        result["shishen_detail"] = f"流年天干{ln_stem}为日主{day_stem}的{shishen}"

    interactions = compute_interactions(ln_stem, ln_branch, pillars)
    if interactions:
        result["interactions"] = interactions

    summary_parts = [f"流年：{target_year}年 {ln_stem}{ln_branch}"]
    if day_stem:
        summary_parts.append(f"流年天干{ln_stem}为日主{day_stem}的{result.get('shishen', '')}")
    for inter in interactions:
        summary_parts.append(f"  {inter['detail']}")

    result["summary_zh"] = "\n".join(summary_parts)
    return result


__all__ = ["compute_liunian", "compute_shishen"]
